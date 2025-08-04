# server.py
import random
import asyncio
from fastapi import FastAPI

app = FastAPI()

# Global latency variable
latency_ms = random.randint(50, 2000)


async def update_latency_task():
    """Background task: update latency every 3 minutes."""
    global latency_ms
    while True:
        await asyncio.sleep(60)  # wait 3 minutes
        if random.random() < 0.8:  # 80% chance small change
            jitter = random.randint(-20, 20)
            latency_ms = max(10, latency_ms + jitter)
        else:  # 20% chance big change
            latency_ms = random.randint(50, 500)
        print(f"⚡ Latency updated to {latency_ms} ms")


@app.on_event("startup")
async def startup_event():
    """Start background latency updater when server starts."""
    asyncio.create_task(update_latency_task())


@app.get("/ping")
async def ping():
    await asyncio.sleep(latency_ms / 1000)  # convert ms → sec
    return {"status": "ok", "latency_ms": latency_ms}
