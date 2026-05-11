# Week 7 - Splunk Dashboard Attack Simulation

### This week, I successfully transitioned our security monitoring from "messy terminal" logs to a high-fidelity Splunk Classic dashboard. By integrating the pipeline with Splunk via the HTTP Event Collector (HEC), raw MQTT telemetry is now parsed into structured, real-time visualizations. This allows engineers to monitor the health of the Grand Marina’s water systems—including pressure and flow rates across the Main Building, Pool/Spa, and Kitchen zones—while instantly spotting anomalies that would be difficult to track in a standard text stream. To prove the resilience of the pipeline, I implemented an Attack Simulator that executes a theatrical three-phase offensive: eavesdropping, data injection with fake HMAC signatures, and replay attacks using stale timestamps. The dashboard serves as a live "Security Operations Center" (SOC) display, triggering immediate red alerts when these threats are detected. This exercise demonstrates the "defense-in-depth" approach in action, as the system’s triple-layer validation (HMAC, timestamps, and sequence counters) successfully blocks every simulated attack in real time.

## 🛠️ Technical Highlights
* **Protocol Security:** Mutual TLS (mTLS) for authenticated device-to-broker communication.
* **Cryptographic Integrity:** HMAC-SHA256 signatures for verifying that sensor data hasn't been altered in transit.
* **Anti-Replay Logic:** Dual validation using sequence tracking and timestamp "freshness" windows.
* **SIEM Integration:** Automated event forwarding to Splunk for centralized monitoring and alerting.

---

## 🚀 How to Run the Simulation

### 1. Prerequisites
Ensure you have Python installed along with the following libraries:
* **MQTT:** `pip install paho-mqtt`
* **Security/Encryption:** `pip install cryptography`
* **Networking:** `pip install requests websockets`
* **Broker:** Install the [Mosquitto MQTT Broker](https://mosquitto.org/download/).

### 2. Generate mTLS Certificates
Before starting the broker, you must generate the Certificate Authority (CA), server, and client certificates:
```bash
python generate_client_certs.py

Running the Simulation (4-Terminal Guide)
To replicate this simulation environment, open four separate Anaconda Prompt terminals and run the following commands in order:

Terminal 1: Launch the Secure Broker
Start the Mosquitto broker using the provided mTLS configuration file:

Bash
mosquitto -c mosquitto_mtls.conf -v
Terminal 2: Start the Security Dashboard (Subscriber)
Run the main monitoring pipeline.

⚠️ CRITICAL: If you are testing this repository, you MUST run GITHUB_USER_SUBSCRIBER_DASHBOARD.py. Do not use subscriber_dashboard.py, as that file is configured specifically for my local VM environment and will not function correctly for external users.

Bash
python GITHUB_USER_SUBSCRIBER_DASHBOARD.py
Terminal 3: Start Normal Operations (Publisher)
Begin sending valid, defended telemetry from the simulated hotel sensors:

Bash
python publisher_defended.py
Terminal 4: Execute Attack Simulation
Run the attack script to demonstrate how the system identifies and blocks malicious activity:

Bash
python attack_simulator.py
Once Terminal 4 begins, watch your Splunk dashboard for real-time Attack Detected alerts as the subscriber identifies and rejects eavesdropping, injection, and replay attempts.
