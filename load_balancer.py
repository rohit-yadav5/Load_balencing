# load_balancer.py
import asyncio
import random
import time
import httpx

SERVERS = [
    "http://127.0.0.1:5001/ping",
    "http://127.0.0.1:5002/ping",
    "http://127.0.0.1:5003/ping",
    "http://127.0.0.1:5004/ping",
    "http://127.0.0.1:5005/ping",
]

# Latency estimates per server (initialize as None)
latency_estimates = {url: None for url in SERVERS}

# EMA smoothing factor
ALPHA = 0.3


async def send_request(client: httpx.AsyncClient, url: str):
    """Send a request and measure latency."""
    start = time.time()
    try:
        resp = await client.get(url, timeout=10.0)
        elapsed = (time.time() - start) * 1000  # ms
        data = resp.json()
    except Exception as e:
        elapsed = 9999  # treat failure as huge latency
        data = {"error": str(e)}

    # Update moving average
    old = latency_estimates[url]
    if old is None:
        latency_estimates[url] = elapsed
    else:
        latency_estimates[url] = ALPHA * elapsed + (1 - ALPHA) * old

    return url, elapsed, data


def pick_server():
    """Pick a server based on 95/5 explore-exploit."""
    # If all latencies are None (cold start), pick randomly
    known = {k: v for k, v in latency_estimates.items() if v is not None}
    if not known:
        return random.choice(SERVERS)

    # Exploit: fastest server
    best_server = min(known, key=known.get)

    # Explore vs exploit
    if random.random() < 0.95:
        return best_server
    else:
        others = [s for s in SERVERS if s != best_server]
        return random.choice(others)


async def traffic_generator():
    """Generate 100 requests per minute."""
    async with httpx.AsyncClient() as client:
        while True:
            tasks = []
            for _ in range(100):
                server = pick_server()
                tasks.append(send_request(client, server))

            results = await asyncio.gather(*tasks)

            # Print summary
            print("\n=== Traffic Round Summary ===")
            for url in SERVERS:
                est = latency_estimates[url]
                print(f"{url}: avg={est:.2f} ms" if est else f"{url}: no data yet")

            # wait until next minute
            await asyncio.sleep(60)


if __name__ == "__main__":
    asyncio.run(traffic_generator())
