# Adaptive Load Balancer Simulation

This project simulates an adaptive load balancer in Python that distributes requests to a pool of backend servers based on their estimated latency. It uses an **explore/exploit** strategy to dynamically adapt to changing network conditions and server performance.

The simulation consists of two main components:
1.  `server.py`: A simple FastAPI-based web server that simulates a backend service with dynamically changing latency.
2.  `load_balancer_v2.py`: The client-side load balancer that sends requests and intelligently selects servers.

---

## Features

*   **Asynchronous Traffic Generation**: Uses `httpx` and `asyncio` to send a high volume of concurrent requests.
*   **Latency-Based Server Selection**: Chooses the best server based on real-time performance.
*   **Exponential Moving Average (EMA)**: Smooths out latency measurements to prevent drastic reactions to temporary spikes.
*   **Explore/Exploit Strategy**:
    *   **Exploit (95% of the time)**: Sends requests to the server with the lowest known latency.
    *   **Explore (5% of the time)**: Sends requests to other servers to update their latency data and discover if a slower server has become faster.
*   **Dynamic Backend Simulation**: The backend servers' latency changes over time, forcing the load balancer to adapt.

---

## How It Works

### Backend Servers (`server.py`)

You can run multiple instances of `server.py` on different ports. Each server has a `/ping` endpoint. A background task in each server periodically adjusts its own response latency, simulating real-world fluctuations in server or network load.

### Load Balancer (`load_balancer_v2.py`)

1.  **Latency Estimation**: The load balancer maintains an Exponential Moving Average (EMA) of the latency for each server. When a new request completes, the latency is calculated and the EMA is updated using a smoothing factor `ALPHA`.
    ```
    new_latency = ALPHA * current_latency + (1 - ALPHA) * old_latency_ema
    ```
    Failed requests are treated as having a very high latency, naturally discouraging the balancer from using unresponsive servers.

2.  **Server Selection**: Before sending a request, the balancer uses a 95/5 explore-exploit model:
    *   With 95% probability, it **exploits** its current knowledge by selecting the server with the lowest EMA latency.
    *   With 5% probability, it **explores** by selecting a random server from the rest of the pool. This ensures that the latency data for all servers stays relatively fresh.

3.  **Traffic Generation**: The `traffic_generator` function runs in a loop, sending 100 requests in a concurrent burst. After each round, it prints a summary of which servers were chosen and their current average latency, then waits before starting the next round.

---

## How to Run

### 1. Prerequisites

Install the necessary Python libraries:

```bash
pip install fastapi "uvicorn[standard]" httpx
```

### 2. Start the Backend Servers

Open five separate terminal windows. In each one, run the `server.py` script on a different port from 5001 to 5005.

*   Terminal 1: `uvicorn server:app --port 5001`
*   Terminal 2: `uvicorn server:app --port 5002`
*   Terminal 3: `uvicorn server:app --port 5003`
*   Terminal 4: `uvicorn server:app --port 5004`
*   Terminal 5: `uvicorn server:app --port 5005`

You will see output from each server as its internal latency updates.

### 3. Run the Load Balancer

In a new terminal, run the load balancer script:

```bash
python load_balancer_v2.py
```

---

## Expected Output

The load balancer will print a summary for each round of traffic. You will observe that it quickly identifies the fastest server(s) and sends most of the traffic there, while occasionally sending a few requests to other servers to "explore".

```
=== Traffic Round 1 Summary ===
http://127.0.0.1:5001/ping: avg=134.51 ms, requests=96
http://127.0.0.1:5002/ping: avg=450.12 ms, requests=1
http://127.0.0.1:5003/ping: avg=880.93 ms, requests=1
http://127.0.0.1:5004/ping: avg=1523.44 ms, requests=1
http://127.0.0.1:5005/ping: avg=245.78 ms, requests=1

=== Traffic Round 2 Summary ===
http://127.0.0.1:5001/ping: avg=138.20 ms, requests=95
http://127.0.0.1:5002/ping: avg=445.30 ms, requests=2
http://127.0.0.1:5003/ping: avg=876.11 ms, requests=1
http://127.0.0.1:5004/ping: avg=1501.80 ms, requests=0
http://127.0.0.1:5005/ping: avg=251.02 ms, requests=2
```

## Configuration

You can modify the following constants in `load_balancer_v2.py` to experiment with the behavior:
*   `SERVERS`: The list of backend server URLs.
*   `ALPHA`: The EMA smoothing factor (a value between 0 and 1). A lower value means new measurements have less impact.
*   The number of requests per round and the `asyncio.sleep()` duration in `traffic_generator`.