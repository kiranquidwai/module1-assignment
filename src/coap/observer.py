"""
Module 1 Assignment — Task 2.2
CoAP Observer Client

Complete all TODO sections.

Run with:  python -m src.coap.observer
"""

import asyncio
import json
import logging
from datetime import datetime, timezone

import aiocoap
from aiocoap import Message, Code

logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)-8s  %(message)s")
log = logging.getLogger(__name__)

SERVER_BASE = "coap://localhost"
OBSERVE_DURATION = 60   # seconds before clean deregister


class FactoryObserver:
    """Observes CoAP sensor resources and reassembles Block2 transfers."""

    def __init__(self):
        self._ctx = None
        self._last_seq: dict[str, int] = {}     # uri -> last observe sequence number
        self._stale_count: dict[str, int] = {}  # uri -> stale notification count

    # ── Setup ──────────────────────────────────────────────────────────────────

    async def start(self) -> None:
        """Create the aiocoap client context."""
        self._ctx = await aiocoap.Context.create_client_context()

    async def stop(self) -> None:
        """Clean up the context."""
        if self._ctx:
            await self._ctx.shutdown()

    # ── Observation ────────────────────────────────────────────────────────────

    async def observe_resource(self, uri: str) -> None:
        request = Message(code=Code.GET, uri=uri)
        request.opt.observe = 0

        pr = self._ctx.request(request)

        async def observation_loop():
            async for response in pr.observation:
                self._handle_notification(uri, response)

        try:
            await asyncio.wait_for(observation_loop(), timeout=OBSERVE_DURATION)
        except asyncio.TimeoutError:
            pr.observation.cancel()
            log.info("Deregistered from %s", uri)
        # TODO: implement this coroutine
        #raise NotImplementedError

    def _handle_notification(self, uri: str, response: Message) -> None:
        seq = response.opt.observe
        last = self._last_seq.get(uri)

        if seq is not None and last is not None:
            # simple stale check
            if seq <= last:
                self._stale_count[uri] = self._stale_count.get(uri, 0) + 1
                log.warning("STALE notification on %s: seq=%s <= last=%s", uri, seq, last)
                return

        if seq is not None:
            self._last_seq[uri] = seq

        payload = json.loads(response.payload.decode())
        arrival_time = datetime.now(timezone.utc).isoformat()

        log.info(
            "[OBSERVE] %s  seq=%s  val=%s %s  @ %s",
            uri,
            seq,
            payload.get("value"),
            payload.get("unit"),
            arrival_time,
        )
        # TODO: implement this method
        pass

    # ── Block2 Transfer ────────────────────────────────────────────────────────

    async def fetch_manifest(self) -> None:
        uri = f"{SERVER_BASE}/factory/manifest"
        request = Message(code=Code.GET, uri=uri)

        response = await self._ctx.request(request).response
        payload = response.payload

        log.info("Manifest received: %s bytes", len(payload))

        data = json.loads(payload.decode())

        firmware_entries = data.get("firmware", [])
        log.info("Firmware entries in manifest: %s", len(firmware_entries))

        if response.opt.block2 is not None:
            log.info("Final Block2 option: %s", response.opt.block2)

        log.info("Block2 transfer complete")
        # TODO: implement this coroutine
        #raise NotImplementedError

    # ── Run ────────────────────────────────────────────────────────────────────

    async def run(self) -> None:
        await self.start()

        uris = [
            f"{SERVER_BASE}/factory/line1/temperature",
            f"{SERVER_BASE}/factory/line2/temperature",
        ]

        try:
            await asyncio.gather(*(self.observe_resource(uri) for uri in uris))
            await self.fetch_manifest()

            print("\nFinal stale notification summary:")
            for uri in uris:
                print(f"{uri}: {self._stale_count.get(uri, 0)} stale notifications")

        finally:
            await self.stop()


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    observer = FactoryObserver()
    asyncio.run(observer.run())