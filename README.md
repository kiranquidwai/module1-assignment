# Module 1 Assignment — SmartFactory IoT Protocol Integration

**Real-Time Data Analytics for IoT** · Graduate Course · Module 1
Student name: Kiran Ahmed Quidwai          
ID: 100999782

---

## Quick Start

```bash
# 1. Install dependencies and start Docker services
bash setup.sh
# 2. Run MQTT components 
python -m src.mqtt.publisher python -m src.mqtt.subscriber 
# 3. Run CoAP components 
python -m src.coap.server python -m src.coap.observer 
# 4. Run AMQP components 
python -m src.amqp.topology python -m src.amqp.producer python -m src.amqp.consumer 
# 5. Run all tests 
pytest tests/ -v --tb=short


## Repository Structure

```
module1-assignment/
├── src/
│   ├── mqtt/
│   │   ├── publisher.py     
│   │   └── subscriber.py     
│   ├── coap/
│   │   ├── server.py        
│   │   └── observer.py     
│   └── amqp/
│       ├── topology.py       
│       ├── producer.py       
│       └── consumer.py       
│
├── tests/
│   ├── mqtt/
│   ├── coap/
│   └── amqp/
│
├── report/
│   ├── packet_analysis.md    
│   └── comparison_report.md  
│
├── captures/                 
│   ├── mqtt.pcap 
│   ├── coap.pcap 
│   └── amqp.pcap
│ 
├── scripts/
│   └── capture.sh          
├── config/
│   └── mosquitto.conf       
├── docker-compose.yml      
├── requirements.txt
├── pytest.ini
└── README.md
```

---

## Running Individual Components

```bash
# Task 1 — MQTT
python -m src.mqtt.publisher       # Terminal 1
python -m src.mqtt.subscriber      # Terminal 2

# Task 2 — CoAP
python -m src.coap.server          # Terminal 1
python -m src.coap.observer        # Terminal 2

# Task 3 — AMQP (run in order)
python -m src.amqp.topology        # Once — sets up RabbitMQ topology
python -m src.amqp.producer        # Terminal 1
python -m src.amqp.consumer        # Terminal 2

# Task 4 — Packet capture (with publisher/server running)
bash scripts/capture.sh
```

---

## Running Tests

```bash
# All tests
pytest tests/ -v

# Individual task tests
pytest tests/mqtt/ -v
pytest tests/coap/ -v
pytest tests/amqp/ -v

# QoS experiment with output table (Task 1.3)
pytest tests/mqtt/test_qos_loss.py -v -s
```

---

## Infrastructure

| Service | Port | URL |
|---------|------|-----|
| Mosquitto MQTT | 1883 | mqtt://localhost:1883 |
| RabbitMQ AMQP | 5672 | amqp://localhost:5672 |
| RabbitMQ Management | 15672 | http://localhost:15672 (guest/guest) |
| CoAP server (Python) | 5683 | coap://localhost:5683 |
| InfluxDB (optional) | 8086 | http://localhost:8086 |

```bash
# Start all services
docker compose up -d

# Stop all services
docker compose down

# View logs
docker compose logs -f mosquitto
docker compose logs -f rabbitmq
```

---

Notes
MQTT QoS experiments were tested under simulated packet loss.
CoAP observable resources and Block2 transfer were implemented successfully.
Packet captures were analyzed using Wireshark.
Proxy mapping between CoAP and HTTP headers was verified using pytest tests.

---

*Graduate Course: Real-Time Data Analytics for IoT · Module 1*
