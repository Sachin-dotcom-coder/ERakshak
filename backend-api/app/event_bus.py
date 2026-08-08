import json
import redis
import os
import asyncio
from typing import Set

class EventBus:
    def __init__(self):
        self.redis_host = os.getenv("REDIS_HOST", "localhost")
        self.redis_port = int(os.getenv("REDIS_PORT", 6379))
        self.redis_client = None
        self.in_memory_queues: Set[asyncio.Queue] = set()
        self._connect()

    def _connect(self):
        try:
            self.redis_client = redis.Redis(
                host=self.redis_host, 
                port=self.redis_port, 
                decode_responses=True,
                socket_timeout=1.0
            )
            self.redis_client.ping()
            print("EventBus: Connected to Redis successfully.")
        except Exception as e:
            print(f"EventBus: Redis server not found. Falling back to in-memory broker. ({e})")
            self.redis_client = None

    async def publish(self, channel: str, data: dict):
        """
        Publishes message to the specified channel.
        If Redis is connected, it uses Redis Pub/Sub.
        Otherwise, it distributes to registered in-memory queues.
        """
        # Publish to Redis
        if self.redis_client:
            try:
                self.redis_client.publish(channel, json.dumps(data))
                return
            except Exception as e:
                print(f"EventBus: Redis publish error: {e}. Reverting to in-memory.")
                self.redis_client = None
        
        # Fallback: In-memory queues (for WebSockets when running on a single local process)
        if self.in_memory_queues:
            for queue in list(self.in_memory_queues):
                try:
                    await queue.put({"channel": channel, "data": data})
                except Exception as e:
                    print(f"EventBus: In-memory queue write error: {e}")

    def register_queue(self, queue: asyncio.Queue):
        self.in_memory_queues.add(queue)
        print(f"EventBus: Registered new active listener queue (Total: {len(self.in_memory_queues)})")

    def unregister_queue(self, queue: asyncio.Queue):
        self.in_memory_queues.discard(queue)
        print(f"EventBus: Unregistered listener queue (Total: {len(self.in_memory_queues)})")

event_bus = EventBus()
