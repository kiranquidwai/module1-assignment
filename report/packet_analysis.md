# Module 1 Assignment — Packet Analysis
## Task 4: Wire-Level Protocol Annotation

---

## 4.2 MQTT Packet Annotations

### CONNECT Packet

| Field | Offset (bytes) | Raw Hex | Decoded Value |
|-------|---------------|---------|---------------|
| Frame type + flags (byte 1) | 0 | `10` | Type=CONNECT (0001), flags=0000 |
| Remaining length (byte 2) | 1 | `27` | 39 bytes |
| Protocol name length | 2–3 | `00 04` | 4 |
| Protocol name | 4–7 | `4D 51 54 54` | "MQTT" |
| Protocol version | 8 | `04` | 4 (MQTT v3.1.1) |
| Connect flags | 9 | `00` | See breakdown below |
| Keep-alive | 10–11 | `00 3C` | 60 seconds |
| Client ID length | 12–13 | `00 1B` | 27 |
| Client ID | 14–… | `73 6D 61 ` | "smartfactory-subscriber-001" |

**Connect Flags byte breakdown:**

| Bit | Name | Value | Meaning |
|-----|------|-------|---------|
| 7 | Username flag | 0 | Username not present |
| 6 | Password flag | 0 | Password not present |
| 5 | Will retain | 0 | No retained will message |
| 4–3 | Will QoS | 00 | QoS0 |
| 2 | Will flag | 0 | Will message disabled |
| 1 | Clean session | 0 | Persistent session |
| 0 | Reserved | 0 | — |

---

### QoS 1 PUBLISH Packet

| Field | Offset (bytes) | Raw Hex | Decoded Value |
|-------|---------------|---------|---------------|
| Fixed header byte 1 | 0 | `33` | Type=PUBLISH(0011), DUP=0, QoS=1, RETAIN=1 |
| Remaining length | 1 | `1F` | 31 bytes |
| Topic length | 2–3 | `00 14` | 20 |
| Topic string | 4–… | `66 61 63 ...` | "factory/line1/status" |
| Packet Identifier | … | `15 9F` | 5535 |
| Payload | … | `6F 66 66 6C 69 6E 65` | "offline" |

**Fixed header byte 1 bit expansion:**

| Bits 7–4 (packet type) | Bit 3 (DUP) | Bits 2–1 (QoS) | Bit 0 (RETAIN) |
|------------------------|-------------|----------------|----------------|
| `0011` = PUBLISH (3)  | `0` = first delivery   | `01` = QoS 1   | `1` = retained      |

---

### PUBACK Packet

| Field | Offset | Raw Hex | Decoded Value |
|-------|--------|---------|---------------|
| Fixed header | 0 | `40` | Type=PUBACK (0100) |
| Remaining length | 1 | `02` | 2 bytes |
| Packet Identifier | 2–3 | `15 9F` | 5535 |

**Packet Identifier match:** PUBLISH PKT ID = 5535 ; PUBACK PKT ID = 5535 ; **Match? Yes**

---

## 4.3 CoAP Packet Annotations

### CON GET Request

```
Bytes:   42 01 70 56  f6 b4 39 6c 6f ...
       [   Header   ] [  Token  ] [Options...]
```

| Field | Bits/Bytes | Raw Value | Decoded Value |
|-------|-----------|-----------|---------------|
| Version (bits 7–6) | 2 bits | `01` | 1 (always 1) |
| Type (bits 5–4) | 2 bits | `00` | Confirmable = CON |
| TKL (bits 3–0) | 4 bits | `0010` | Token length = 2 |
| Code (byte 1) | 8 bits | `01` | 0.01 = GET |
| Message ID (bytes 2–3) | 16 bits | `70 56` | 28758 |
| Token (bytes 4–TKL+3) | TKL bytes | `F6 B4 …` | 0xf6b4 |
| Option Delta | 4 bits | `B` | Delta = 11, Option# = 11 (Uri-Path) |
| Option Length | 4 bits | `7` | 7 bytes |
| Option Value | 7 bytes | `66 61 63 …` | "factory" (Uri-Path) |

**Byte 0 full expansion:**

| Bit 7 | Bit 6 | Bit 5 | Bit 4 | Bit 3 | Bit 2 | Bit 1 | Bit 0 |
|-------|-------|-------|-------|-------|-------|-------|-------|
| Ver   | Ver   | T     | T     | TKL   | TKL   | TKL   | TKL   |
| `0`   | `1`   | `0`   | `0`   | `0`   | `0`   | `1`   | `0`   |

---

### ACK 2.05 Content Response

| Field | Bytes | Raw Hex | Decoded Value |
|-------|-------|---------|---------------|
| Fixed header byte 0 | 0 | `62` | Ver=01, T=10 (ACK), TKL=2 |
| Code byte 1 | 1 | `45` | 2.05 = Content |
| Message ID | 2–3 | `70 56` | 28758 (matches request? Yes) |
| Token | 4–… | `F6 B4 …` | 0xf6b4 (matches request? Yes) |
| Option: Content-Format | … | `11 32` | Option# = 12, Value = 50 (application/json) |
| Payload Marker | … | `FF` | 0xFF |
| Payload | … | `7B 22 76 …` | "{\"value\":75.416,\"unit\":\"C\"...}" |

---

### Observe Notification

| Field | Value |
|-------|-------|
| Observe option number | 6 |
| Observe sequence value | 0 |
| Message type | CON (CON / NON) |
| Response code | 2.05 Content |

---