"""
Task 2.3 — CoAP vs HTTP Proxy Test

This test starts:
1. the CoAP resource server
2. a small HTTP proxy on localhost:8080
3. compares HTTP GET result with direct CoAP GET result
"""

import asyncio
import json

import pytest
from aiohttp import web, ClientSession
import aiocoap
from aiocoap import Message, Code

from src.coap.server import build_server


COAP_BASE = "coap://localhost"
HTTP_BASE = "http://localhost:8080"


@pytest.fixture(scope="module")
async def coap_server():
    context = await build_server()
    await asyncio.sleep(0.2)
    yield context
    await context.shutdown()


@pytest.fixture(scope="module")
async def coap_client():
    client = await aiocoap.Context.create_client_context()
    await asyncio.sleep(0.2)
    yield client
    await client.shutdown()


@pytest.fixture(scope="module")
async def http_proxy(coap_server):
    async def handle(request):
        path = request.match_info["path"]
        coap_uri = f"{COAP_BASE}/{path}"

        client = await aiocoap.Context.create_client_context()
        coap_response = await client.request(
            Message(code=Code.GET, uri=coap_uri)
        ).response

        await client.shutdown()

        return web.Response(
            body=coap_response.payload,
            status=200,
            content_type="application/json",
            headers={
                "Cache-Control": "max-age=0",
                "X-CoAP-Code": str(coap_response.code),
                "X-CoAP-Content-Format": str(coap_response.opt.content_format),
            },
        )

    app = web.Application()
    app.router.add_get("/{path:.*}", handle)

    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(runner, "localhost", 8080)
    await site.start()

    await asyncio.sleep(0.2)
    yield

    await runner.cleanup()


@pytest.mark.asyncio
async def test_http_get_matches_direct_coap(coap_server, coap_client, http_proxy):
    coap_response = await coap_client.request(
        Message(code=Code.GET, uri=f"{COAP_BASE}/factory/line1/temperature")
    ).response

    direct_json = json.loads(coap_response.payload.decode())

    async with ClientSession() as session:
        async with session.get(f"{HTTP_BASE}/factory/line1/temperature") as resp:
            print("\nHTTP RESPONSE HEADERS:")
            for k, v in resp.headers.items():
                print(f"{k}: {v}")
            assert resp.status == 200
            assert resp.headers["Content-Type"].startswith("application/json")

            http_json = await resp.json()

            assert http_json == direct_json
            assert resp.headers["X-CoAP-Code"] == "2.05 Content"
            #assert resp.headers["X-CoAP-Content-Format"] == "50"
            assert resp.headers["X-CoAP-Content-Format"] == "JSON"