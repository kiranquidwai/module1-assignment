"""
Module 1 Assignment — Task 1.2
MQTT Wildcard Subscriber

Complete all TODO sections. Do not modify the function signatures.
"""

import json
import logging
import time
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any

import paho.mqtt.client as mqtt

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ── Configuration ─────────────────────────────────────────────────────────────
BROKER_HOST  = "localhost"
BROKER_PORT  = 1883
CLIENT_ID    = "smartfactory-subscriber-001"

TOPIC_ALL        = "factory/#"         # all factory messages
TOPIC_TEMP       = "factory/+/temperature"  # all temperature readings (any line)

CRITICAL_TEMP    = 85.0
SUMMARY_INTERVAL = 30   # seconds


class SmartFactorySubscriber:
    """Subscribes to SmartFactory sensor topics and processes incoming data."""

    def __init__(self, broker_host: str = BROKER_HOST, broker_port: int = BROKER_PORT):
        self.broker_host  = broker_host
        self.broker_port  = broker_port
        self._client      = mqtt.Client(client_id=CLIENT_ID, clean_session=False)
        self._msg_counts: dict[str, int] = defaultdict(int)
        self._last_summary = time.time()
        self._alerts_fired = 0

        self._client.on_connect = self.on_connect
        self._client.on_message = self.on_message

    # ── Connection ─────────────────────────────────────────────────────────────

    def on_connect(self, client, userdata, flags: dict, rc: int) -> None:
        if rc == 0:
            log.info("Connected to broker")
            client.subscribe(TOPIC_ALL, qos=1)
            client.subscribe(TOPIC_TEMP, qos=2)
            log.info("Subscribed to %s at QoS 1", TOPIC_ALL)
            log.info("Subscribed to %s at QoS 2", TOPIC_TEMP)
        else:
            log.error("Connection failed with rc=%s", rc)
        # TODO: implement this callback
        pass

    # ── Message Handling ───────────────────────────────────────────────────────

    def on_message(self, client, userdata, msg: mqtt.MQTTMessage) -> None:
        self._msg_counts[msg.topic] += 1

        raw_payload = msg.payload.decode("utf-8")

        try:
            payload = json.loads(raw_payload)
        except json.JSONDecodeError:
            payload = raw_payload

        self._print_message(msg, payload)

        if msg.topic.endswith("/temperature"):
            self._check_temperature_alert(msg.topic, payload)

        now = time.time()
        if now - self._last_summary >= SUMMARY_INTERVAL:
            self._print_summary()
            self._last_summary = now
        # TODO: implement this callback
        pass

    def _print_message(self, msg: mqtt.MQTTMessage, payload: Any) -> None:
        current_time = datetime.now(timezone.utc).strftime("%H:%M:%S")

        if isinstance(payload, dict) and "value" in payload:
            value = payload["value"]
            unit = payload.get("unit", "")
            value_text = f"{value} {unit}".strip()
        else:
            value_text = str(payload)

        print(
            f"[{current_time}] {msg.topic}  "
            f"val={value_text}  QoS={msg.qos}  retain={msg.retain}"
        )
        # TODO: implement this method
        pass

    def _check_temperature_alert(self, topic: str, payload: Any) -> None:
        if not isinstance(payload, dict):
            return

        value = payload.get("value")

        if value is None:
            return

        try:
            value = float(value)
        except ValueError:
            return

        if value > CRITICAL_TEMP:
            self._alerts_fired += 1
            timestamp = payload.get("timestamp", datetime.now(timezone.utc).isoformat())

            print("╔══════════════════════════════════════╗")
            print(f"║  ⚠ CRITICAL ALERT — {topic}")
            print(f"║  Temperature: {value}°C  (threshold: {CRITICAL_TEMP}°C)")
            print(f"║  Time: {timestamp}")
            print("╚══════════════════════════════════════╝")
        # TODO: implement this method
        pass

    def _print_summary(self) -> None:
        print("── Message Summary ──────────────────────")

        total = 0
        for topic, count in sorted(self._msg_counts.items()):
            print(f"{topic:<50}  {count:>6} msgs")
            total += count

        print(f"Total: {total} messages  |  Alerts fired: {self._alerts_fired}")
        print("─────────────────────────────────────────")
        # TODO: implement this method
        pass

    # ── Run ────────────────────────────────────────────────────────────────────

    def run(self) -> None:
        """Connect and block until interrupted."""
        self._client.connect(self.broker_host, self.broker_port, keepalive=60)
        log.info("Listening for messages (Ctrl-C to stop)")
        try:
            self._client.loop_forever()
        except KeyboardInterrupt:
            log.info("Subscriber stopped")
        finally:
            self._client.disconnect()


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    sub = SmartFactorySubscriber()
    sub.run()
