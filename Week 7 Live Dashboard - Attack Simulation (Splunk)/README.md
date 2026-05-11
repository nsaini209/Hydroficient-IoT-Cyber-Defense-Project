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
* **Python**  Install [Python](https://www.python.org/downloads/)
* **Broker:** Install the [Mosquitto MQTT Broker](https://mosquitto.org/download/).
* **Anaconda:** Install the [Anaconda Terminal](https://www.anaconda.com/docs/getting-started/anaconda/install/overview).

### 2. Generate mTLS Certificates
Before starting the broker, you must generate the Certificate Authority (CA), server, and client certificates
`python generate_client_certs.py`

### 3. Running Terminals 1-4
This is how we display our subscriber dashboard, activate the publisher, mosquitto broker, and attack simulation.

####  --------------- NOTE: Every terminal involves navigating to the correct directory for the file to execute ---------------

* **Terminal 1 Mosquitto Broker:** `mosquitto -c mosquitto_mtls.conf`
* **Terminal 2 Subscriber Dashboard:**  PLEASE NOTE TO USE GITHUB_USER_SUBSCRIBER_DASHBOARD.PY as subscriber_dashboard.py will not work as that is ran locally with Splunk
`python GITHUB_USER_SUBSCRIBER_DASHBOARD.py`
* * **Terminal 3 Publisher Dashboard:** `python publisher_defended.py`
* * **Terminal 1 Mosquitto Broker:** `attack_simulator.py`
#### ----- Make sure your dashboard is active and picking up logs, once you run the attack it will display blocked attacks! -----


## 📷 Screenshots

#### This is what you should see!
<img width="1270" height="1045" alt="Screenshot 2026-05-08 114606" src="https://github.com/user-attachments/assets/6b58e8c9-9dd6-4e0f-8571-6f82092bd247" />

#### Splunk Dashboard I've Created!
<img width="2547" height="1140" alt="Screenshot 2026-05-11 103819" src="https://github.com/user-attachments/assets/9c55f877-e5b7-49d6-9bd1-4b92d355feff" />





