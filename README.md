Adaptive Load Balancer Simulation
Overview
This project simulates a client-side load balancer using Python with FastAPI, asyncio, and httpx. It demonstrates adaptive traffic routing based on real-time server performance.
Features
Latency-Driven Routing: Uses Exponential Moving Average (EMA) for smooth latency estimation.
Explore/Exploit Strategy: Balances requests between known fast servers (exploit) and others (explore).
Asynchronous: Efficiently handles concurrent traffic with asyncio and httpx.
Dynamic Adaptation: Automatically adjusts traffic to servers based on their changing performance.
Running the Simulation
Install Dependencies
pip install fastapi "uvicorn[standard]" httpx
Start Backend Servers
Open five terminals and run:
uvicorn server:app --port 5001
uvicorn server:app --port 5002
uvicorn server:app --port 5003
uvicorn server:app --port 5004
uvicorn server:app --port 5005
Run the Load Balancer
python load_balancer_v2.py
Summary
Each round shows performance metrics for servers.
Most traffic goes to the fastest server, with some exploring other options.
Configuration
Adjust these parameters in load_balancer_v2.py:
SERVERS: List of backend server URLs.
ALPHA: EMA smoothing factor (higher values prioritize recent data).
Requests per round and asyncio.sleep() delay.