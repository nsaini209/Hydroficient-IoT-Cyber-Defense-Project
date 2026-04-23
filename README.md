# Hydroficient-IoT-Cyber-Defense-Project
## An 8 week process of working on a project that covers detecting anomalies and more!

### Week 1 - Threat Model ✅
 - Overview - This project presents a comprehensive Threat Model and Security Review of the Hydrologic System. The system manages critical maritime infrastructure, including digital water level sensors, automated flood pumps, and remote-controlled valves. These components form the "heart" of daily operations, ensuring dock stability and vessel safety. 

### Week 2 - Mock Sensor Data✅
- Overview: Created a Mock Sensor that shows real values from what an actual sensor would display that monitors water pressure, upstream, downstream, and flowrate. I also created some anomalies so if there was a leakage, blockage, or sensor issues they will be displayed within the JSON file.

### Week 3 - Building an Insecure MQTT Pipeline✅
- Overview: Designed and deployed an intentionally vulnerable MQTT Pipeline to simulate common IoT security risks (Water Pipeline Sensor). By implementing cleartext communication protocols, I established a baseline for traffic analysis, allowing me to identify potential exploit vectors and practice packet-level inspection in a controlled environment.

### Week 4 - Certificates & TLS Encryption ✅
- Overview: Secured the MQTT pipeline by generating CA and server certificates using a generate_certs.py script and configuring Mosquitto to enforce TLS encryption on port 8883, rejecting any plain-text connections. Applied tls_set() across both the sensor publisher and dashboard subscriber to verify certificates on connection.
