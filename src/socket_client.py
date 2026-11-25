"""Small WebSocket client proving the prediction stream works.

Run the API first, then:
    python -m src.socket_client
"""

from __future__ import annotations

import asyncio
import json

import websockets


async def main() -> None:
    uri = "ws://127.0.0.1:8000/ws/predictions"
    async with websockets.connect(uri) as websocket:
        message = await websocket.recv()
        payload = json.loads(message)
        print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
