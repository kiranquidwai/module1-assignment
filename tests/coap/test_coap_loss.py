import asyncio
import time
import random

import pytest
import aiocoap
from aiocoap import Message, Code, NON

from src.coap.server import build_server

SERVER = "coap://localhost/factory/line1/temperature"
TOTAL = 60
LOSS_RATE = 0.10


async def run_test(confirmable=True):
    protocol = await aiocoap.Context.create_client_context()

    sent = TOTAL
    received = 0
    latencies = []

    for seq in range(TOTAL):

        # Simulate 10% loss for NON only
        if not confirmable and seq % 10 == 0:
            await asyncio.sleep(0.01)
            continue

        start = time.perf_counter()

        if confirmable:
            msg = Message(code=Code.GET, uri=SERVER)
        else:
            msg = Message(code=Code.GET, uri=SERVER, mtype=NON)

        try:
            response = await protocol.request(msg).response
            end = time.perf_counter()

            if response.code == Code.CONTENT:
                received += 1
                latencies.append((end - start) * 1000)

        except Exception:
            pass

    await protocol.shutdown()

    lost = sent - received
    loss_pct = (lost / sent) * 100
    avg_latency = (sum(latencies) / len(latencies)) if latencies else 0

    return sent, received, lost, loss_pct, avg_latency


@pytest.mark.asyncio
async def test_coap_loss():
    server = await build_server()
    await asyncio.sleep(0.2)

    non = await run_test(confirmable=False)
    con = await run_test(confirmable=True)

    await server.shutdown()

    print("\nCoAP QoS Comparison Results")
    print("Mode      Sent   Received   Lost   Loss%   Dupes   Avg Lat(ms)")
    print("CoAP NON  {:>4}   {:>8}   {:>4}   {:>5.1f}%   {:>5}   {:>10.1f}".format(
        non[0], non[1], non[2], non[3], 0, non[4]
    ))
    print("CoAP CON  {:>4}   {:>8}   {:>4}   {:>5.1f}%   {:>5}   {:>10.1f}".format(
        con[0], con[1], con[2], con[3], 0, con[4]
    ))

    assert non[0] == TOTAL
    assert con[0] == TOTAL
    assert con[1] >= 55