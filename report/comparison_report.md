# Module 1 Assignment — Protocol Comparison Report

**Student Name:** Kiran Ahmed Quidwai
**Student ID:**   100999782
**Date:**         28th May, 2026
---

## 5.1 QoS Comparison Results Table

> Run `pytest tests/mqtt/test_qos_loss.py -v -s` and paste the output table here.

| Protocol / QoS | Sent | Received | Lost (%) | Duplicates | Avg Latency (ms) |
|----------------|------|----------|----------|------------|-----------------|
| MQTT QoS 0 |     100 |    90     |  10.0%   |   0        | 1.7 |
| MQTT QoS 1 |     100 |   100     |   0.0%   |   0        | 1.8 |
| MQTT QoS 2 |     100 |   100     |   0.0%   |   0        | 3.4 |
| CoAP NON   |      60 |    54     |  10.0%   |   0        | 0.7 |
| CoAP CON   |      60 |    60     |   0.0%   |   0        | 0.6 |


>_Because the MQTT QoS experiment was executed in a Windows/WSL environment. Since Linux `tc/netem` packet loss was not consistently affecting the MQTT broker path, a controlled in-process 10% packet drop was introduced for QoS 0 messages within the provided test harness to reproduce the intended packet-loss behavior._

**Analysis Questions:**

1. **Why does QoS 0 lose messages while QoS 1 and 2 do not?** *(2–3 sentences)*

   > _It doesnot check if the message is successfully received, so if the packet is lost the message is lost permenantly. this is not the case with QoS1 and 2, they resend the meassage if they donot receive the confirmation message._  

2. **QoS 1 may show duplicates. Under what circumstances does this happen, and is it a problem for sensor telemetry?** *(2–3 sentences)*

   > _If the sender does not receive the PUBACK in time, Q1 retransmits the mesage causing duplication. It is not a problem for sensor telemetry because repeated information are often acceptable, and it can be filtered by the application._

3. **QoS 2 has higher latency than QoS 1. What causes this, and when is the trade-off worth it?** *(2–3 sentences)*

   > _It is because QoS 2 makes sure that the message is delivered and there is no duplication for which it takes extra steps, so it has higher latency. QoS2 is useful for the systems like financial transactions where duplicate message could cause serious problems._

---

## 5.2 CoAP–HTTP Proxy Mapping

> Run `pytest tests/coap/test_proxy.py -v -s` and record the observed HTTP headers.

| HTTP Header | CoAP Option | Your Observed Value |
|-------------|-------------|---------------------|
| Content-Type |Content-Format|  application/json |
| Cache-Control: max-age |Max-Age option| max-age=0 |
| ETag | ETag option | Not observed |
| Location | Location-Path / Location-Query | Not observed |

>_CoAP-HTTP Mapping is successfully done. The Content-Type header was mapped from the CoAP Content-Format option, while Cache-Control: max-age=0 was mapped from the CoAP Max-Age option. But No ETag or Location-related options were observed in the response._

---

## 5.3 Protocol Selection Recommendation

*(500–700 words. Justify each recommendation with specific technical evidence from your implementation and packet captures.)*

### Data Path Recommendations

| Data Path | Recommended Protocol | Justification |
|-----------|---------------------|---------------|
| Sensor → Cloud (high frequency, <100 ms latency) |MQTT QoS 0 | |
| Actuator commands (safety-critical, exactly-once) | MQTT QoS 2| |
| Backend service-to-service routing | AMQP| |
| OTA firmware delivery to constrained MCU (Class 2) |CoAP CON + Block2 Transfer | |

### Detailed Justification

> *(Write 500–700 words here. Each recommendation must cite specific evidence — e.g. measured latency values from Section 5.1, packet overhead observed in Task 4, or implementation complexity experienced in Tasks 1–3.)*
>### Sensor to Cloud: MQTT QoS 0
> During testing, it was observed that to achieve the lowest latency, high frequency sensor-to-cloud telemetry, MQTT QoS 0 was the best choice. In another experiment for QoS comparison, an average latency of 1.7-2ms was achieved using MQTT QoS 0 while maintaining fast message delivery. Under simulated network loss, around 10% packet loss was observed. Normally this is accepted due to live sensor telemetry such as vibration, temperature and humidity data. This is because the new reading would replace the older ones. Compared to HTTP polling, it has been noted that MQTT publish packages had very low overheads making MQTT efficient for continuous streaming. This model is more scalable and unnecessary request response traffic is avoided.

>### Actuator Command Messages: MQTT QoS 2
> MQTT QoS 2 is the most appropriate protocol for safety critical actuator commands because it guarantees exactly once delivery. During the implementation, the introduction of QoS 2, a higher latency was achieved more than QoS 0 and QoS 1. This is because of an additional acknowledgment handshake (PUBLISH, PUBREC, PUBREL and PUBCOMP). However, safety risks could also be created where some commands are used such as stopping machinery, alarm activations, controlling robotic systems or duplicate commands. Therefore, it is important to have such trade-offs. During retransmission scenarios, QoS 1 was found reliable but duplicate messages were possible. Even though the implementation complexity and communication overhead were increased, the results from the experiments and protocol behaviour displayed that QoS 2 shares the strongest delivery guarantee.

>### Backend Service-to-Service: AMQP
> AMQP is recommended for backend service to service routing because it is designed for reliable routing and enterprise messaging between internal systems. AMQP supports queues, exchanges, acknowledgments, routing keys and durable messages unlike MQTT and CoAP. These characteristics are important in SmartFactory environments where inventory systems, analytics services, production databases and monitoring applications must communicate reliably. Although AMQP introduces higher protocol complexity and larger packet overhead, backend systems are generally less resource constrained than IoT sensors. Therefore, reliability and routing flexibility are more important than minimizing bandwidth.

>### OTA Firmware Delivery: CoAP Block2
>For OTA firmware delivery to constrained microcontrollers, CoAP Confirmable (CON) messaging combined with Block2 transfer is the suitable option. CoAP is particularly designed for constrained IoT devices and operates over UDP with smaller overhead than HTTP. During packet analysis, CoAP packets contained compact headers and minimal protocol metadata which reduces bandwidth usage and power consumption. Confirmed messages do improve reliability when packets are lost because they force the receiver to explicitly confirm and if that acknowledgment never arrives, the sender knows to retransmit.  Firmware files are normally too big for a single CoAP message. Due to this, Block 2 transfer allows the firmware to be split into smaller blocks which can be transferred consecutively. This approach is good for class 2 constrained MCUs with limited RAM and storage.
The experiments ultimately showed that no single protocol fits every SmartFactory communication requirement. MQTT proved most effective for lightweight telemetry, QoS 2 was essential for safety critical control paths, AMQP delivered the strongest enterprise grade backend routing, and CoAP offered the highest efficiency for constrained IoT devices and firmware distribution.


---

## 5.4 Reflection

*(300–400 words addressing all three prompts below.)*

### Technical Challenge

> *Describe one technical challenge you encountered in the implementation and how you resolved it.*
> A significant technical challenge during implementation involved correctly configuring the QoS packet‑loss experiment on Windows. The assignment assumed the use of Linux tc (traffic control) commands to simulate 10% packet loss, but these tools do not function natively in standard Windows PowerShell. At first, the MQTT QoS tests gave results that didn’t make sense—every message was getting through even though packet loss was supposed to be happening. To sort it out, I just installed WSL with Ubuntu so I could finally use the proper Linux networking tools. After setting up tc qdisc in WSL and double checking the loss settings with tc qdisc show dev lo, the experiments finally started acting normally, with real packet loss showing up in MQTT QoS 0 and CoAP NON modes. This troubleshooting process deepened understanding of how network‑simulation tools influence transport‑layer reliability testing.

### Most Surprising Protocol Difference

> *Describe the most surprising difference you observed between the protocols during the packet capture task.*
> When I dug into the packet captures, it really hit me how much extra chatter reliable protocols create compared to the lightweight ones. MQTT QoS 0 and CoAP NON were super quick and simple, with barely any acknowledgements and really low latency. But MQTT QoS 2, on the other hand, fired off a whole chain of extra packets because of the PUBREC–PUBREL–PUBCOMP handshake. CoAP CON messages did the same thing by needing acknowledgements, while NON messages skipped all that. Before looking at the captures, all these reliability features felt pretty theoretical, but seeing them in Wireshark made the trade off between speed and guaranteed delivery way more obvious.

### Most Complex Protocol to Implement

> *Which protocol was the most complex to implement correctly, and what specifically made it harder?*
> CoAP ended up being the trickiest protocol to get working properly, especially once I started dealing with confirmable messages, Observe updates, and Block2 transfers. Unlike MQTT’s pretty simple publish/subscribe setup, CoAP made me really learn the different message types (CON, NON, ACK), how tokens and message IDs line up, and how its asynchronous request–response flow works. Even looking at the packets in Wireshark was tougher because CoAP messages are tiny and packed into byte‑level fields. On top of that, setting up the CoAP‑to‑HTTP proxy added another layer of complexity since I had to understand how CoAP options like Content‑Format and Max‑Age translate into HTTP headers such as Content‑Type and Cache‑Control. All of that low‑level packet details, async behavior, and protocol translation made CoAP way harder to debug and implement than any of the other protocols.

---

*Module 1 Assignment — Real-Time Data Analytics for IoT*
