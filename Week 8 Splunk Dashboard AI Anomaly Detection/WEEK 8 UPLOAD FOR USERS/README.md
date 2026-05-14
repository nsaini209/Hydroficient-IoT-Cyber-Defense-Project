# Week 8 - Splunk Dashboard AI Anomaly Detection

### This week, the focus was on architecting an AI-integrated security pipeline for an industrial water monitoring system, specifically deploying an Isolation Forest model to detect subtle sensor anomalies. This involved a rigorous training phase where model performance was evaluated using Precision, Recall, and F1 scores, alongside a comparison between Isolation Forest and Local Outlier Factor (LOF) algorithms. Tuning the contamination rate was critical in optimizing the model's ability to distinguish between normal fluctuations and genuine sensor malfunctions, such as high-pressure obstructions or supply failures. To bridge the gap between detection and visibility, a secure MQTT subscriber was developed to perform real-time rule validation—checking HMAC signatures, timestamps, and sequence numbers—before running the AI inference. 
### This pipeline ensures that only authenticated and non-tampered data reaches the model. The entire system was then integrated with a Splunk dashboard, providing a centralized view for monitoring telemetry and security events. Final validation was completed using a custom anomaly injector to test the AI’s response to subtle data drifts and an attack simulator to confirm that traditional network-based threats remained blocked by the mTLS and rule-based defenses.

### NOTE: The Splunk Dashboard is custom and ran locally. I have still left files for you to run on your machine in a web interface which is a easier to setup.

## 🚀 How to Run the Dashboard

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

### 3. Running Terminals 1-5
This is how we display our subscriber dashboard, activate the publisher, mosquitto broker, and attack simulation.

####  --------------- NOTE: Every terminal involves navigating to the correct directory for the file to execute ---------------

* **Terminal 1 Mosquitto Broker:** `mosquitto -c mosquitto_mtls.conf`
* **Terminal 2 Subscriber Dashboard:** Run the subscriber dashboard file
`python subscriber_dashboard_test.py`
* * **Terminal 3 Publisher Dashboard:** `python publisher_user.py`
* * **Terminal 4 Anomaly Injection:** To start getting more anomaly alerts to pop up on the dashboard run this file.
`anomaly_injector.py`
* * **Terminal 5 Attack Simulation:** Leave the anomaly injector file running and test the attack simulator file in terminal 5
`attack_simulator.py`

#### ----- Make sure your dashboard is active and picking up logs, once you run the attack it will display blocked attacks! -----


## 📷 Screenshots

#### What you'll see!
<img width="1588" height="1160" alt="Screenshot 2026-05-13 183821" src="https://github.com/user-attachments/assets/f2ee6eac-fe8c-44d4-8a1e-4d84d034f1e0" />
