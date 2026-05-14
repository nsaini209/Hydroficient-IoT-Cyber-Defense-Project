# Hydroficient IoT Cyber Defense Extern Project
## For the next 8-12 Weeks my objective is to architect a secure, end-to-end MQTT telemetry pipeline for The Grand Marina Hotel (Hypothetical), Simulating real-world cyber threats to critical infrastructure and implementing defense-in-depth strategies to mitigate them.
### 💠 For Instructions on how to run the final prototype, please head to Week 8.💠

### Week 1 - Threat Model ✅
 - Overview - This project presents a comprehensive Threat Model and Security Review of the Hydrologic System. The system manages critical maritime infrastructure, including digital water level sensors, automated flood pumps, and remote-controlled valves. These components form the "heart" of daily operations, ensuring dock stability and vessel safety. 

### Week 2 - Mock Sensor Data✅
- Overview: Created a Mock Sensor that shows real values from what an actual sensor would display that monitors water pressure, upstream, downstream, and flowrate. I also created some anomalies so if there was a leakage, blockage, or sensor issues they will be displayed within the JSON file.

### Week 3 - Building an Insecure MQTT Pipeline✅
- Overview: Designed and deployed an intentionally vulnerable MQTT Pipeline to simulate common IoT security risks (Water Pipeline Sensor). By implementing cleartext communication protocols, I established a baseline for traffic analysis, allowing me to identify potential exploit vectors and practice packet-level inspection in a controlled environment.

### Week 4 - Certificates & TLS Encryption ✅
- Overview: Secured the MQTT pipeline by generating CA and server certificates using a generate_certs.py script and configuring Mosquitto to enforce TLS encryption on port 8883, rejecting any plain-text connections. Applied tls_set() across both the sensor publisher and dashboard subscriber to verify certificates on connection.

### Week 5 - Mutual TLS (mTLS) Implementation ✅
Overview: Strengthened the pipeline with Mutual TLS (mTLS) by generating unique client certificates for each simulated IoT device and requiring the broker to verify client identities. Updated the Mosquitto configuration to enforce require_certificate true, ensuring that only authenticated devices with valid, CA-signed credentials can access the MQTT network.

### Week 6 - Triple-Layer Replay Defenses ✅
Overview: Engineered a "Triple-Layer Defense" to protect telemetry data from injection and replay attacks by implementing HMAC-SHA256 signatures for message integrity, strict timestamp "freshness" windows, and incrementing sequence counters. This cryptographic validation ensures that every sensor reading is verified as authentic and original before it is processed by the backend.

### Week 7 - Splunk Integration & Attack Simulation ✅
Overview: Integrated the secure pipeline with Splunk via the HTTP Event Collector (HEC), transforming raw terminal logs into a high-fidelity security dashboard for real-time monitoring. Validated the system’s resilience by running an Attack Simulator that executed eavesdropping, data injection, and replay attempts, successfully identifying and blocking every threat on the live dashboard.

### Week 8 - AI Anomaly Detection ✅
Overview: Integrated an  Isolation Forest model to analyze real-time MQTT telemetry, specifically designed to identify statistical outliers like pipe leakages or sensor tampering that signature-based defenses might miss. By training the model on historical flowrate and pressure data, I achieved a 0.757 F1-score, ensuring high precision in distinguishing legitimate operational fluctuations from malicious anomalies. These AI-driven insights were funneled into the Splunk dashboard, completing the defense-in-depth strategy by providing a final, behavioral layer of security that triggers automated alerts the moment a deviation occurs.
<img width="2546" height="1261" alt="Screenshot 2026-05-13 131144" src="https://github.com/user-attachments/assets/73b745f2-4e81-41f1-955f-370fa59637cc" />

