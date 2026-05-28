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
| Sensor → Cloud (high frequency, <100 ms latency) | | |
| Actuator commands (safety-critical, exactly-once) | | |
| Backend service-to-service routing | | |
| OTA firmware delivery to constrained MCU (Class 2) | | |

### Detailed Justification

> *(Write 500–700 words here. Each recommendation must cite specific evidence — e.g. measured latency values from Section 5.1, packet overhead observed in Task 4, or implementation complexity experienced in Tasks 1–3.)*

---

## 5.4 Reflection

*(300–400 words addressing all three prompts below.)*

### Technical Challenge

> *Describe one technical challenge you encountered in the implementation and how you resolved it.*

### Most Surprising Protocol Difference

> *Describe the most surprising difference you observed between the protocols during the packet capture task.*

### Most Complex Protocol to Implement

> *Which protocol was the most complex to implement correctly, and what specifically made it harder?*

---

*Module 1 Assignment — Real-Time Data Analytics for IoT*
