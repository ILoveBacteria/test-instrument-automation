import asyncio
import redis.asyncio as aioredis
import websockets

# Redis settings
REDIS_HOST = "localhost"
REDIS_PORT = 6379
CHANNEL = "robot_events"

# Track connected websocket clients
connected_clients = set()

async def handler(websocket):
    # Register client
    connected_clients.add(websocket)
    try:
        async for message in websocket:
            # Here you could also process incoming messages if needed
            print(f"Received from client: {message}")
    finally:
        # Unregister client
        connected_clients.remove(websocket)

async def redis_listener():
    redis = aioredis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    pubsub = redis.pubsub()
    await pubsub.subscribe(CHANNEL)

    async for message in pubsub.listen():
        if message["type"] == "message":
            data = message["data"]
            print(f"Redis: {data}")
            # Broadcast to all connected clients
            if connected_clients:
                await asyncio.gather(*[client.send(data) for client in connected_clients])

async def main():
    # Start websocket server
    async with websockets.serve(handler, "localhost", 8080, ping_interval=None):
        # Run redis listener forever
        await redis_listener()

if __name__ == "__main__":
    asyncio.run(main())
