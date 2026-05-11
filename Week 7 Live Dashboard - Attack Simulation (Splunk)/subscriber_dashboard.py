"""
subscriber_dashboard.py - MQTT Subscriber with Replay Defenses + Live Dashboard

Combines subscriber_defended.py (Project 6) with the dashboard server so
that every accepted and rejected message appears in real time on the web
dashboard at http://localhost:8000.

Validation checks (same as Project 6):
  1. HMAC verification (was the message tampered with?)
  2. Timestamp freshness (is the message recent?)
  3. Sequence counter (have we seen this message before?)

New in Project 7:
  - Starts the dashboard server on launch
  - Pushes every event to the browser via WebSocket
  - Sends all events to Splunk via HEC

Usage:
    python subscriber_dashboard.py
"""

import paho.mqtt.client as mqtt
import ssl
import json
import hmac
import hashlib
import requests
import time
import threading
from datetime import datetime, timezone

# Import the dashboard server
#from dashboard_server import DashboardServer

# Handle paho-mqtt 2.0+ API change
try:
    MQTT_CLIENT_ARGS = {"callback_api_version": mqtt.CallbackAPIVersion.VERSION1}
except AttributeError:
    MQTT_CLIENT_ARGS = {}

# =============================================================================
# Configuration
# =============================================================================
BROKER_HOST = "localhost"
BROKER_PORT = 8883
SUBSCRIBER_ID = "dashboard"

SPLUNK_HEC_URL   = "http://192.168.10.10:8088/services/collector/event"
SPLUNK_HEC_TOKEN = "67ea69e7-7f4c-4d25-ab18-c62241538907"
SPLUNK_INDEX     = "water_monitoring"

# Certificate files (same as Project 5)
CA_CERT     = "certs/ca.pem"
CLIENT_CERT = "certs/device-001.pem"
CLIENT_KEY  = "certs/device-001-key.pem"

# Subscribe to all Grand Marina devices
TOPIC       = "hydroficient/grandmarina/#"
CLIENT_NAME = "GrandMarina-Dashboard-Live"

# =============================================================================
# REPLAY DEFENSE: Shared Secret (must match publisher_defended.py)
# =============================================================================
SHARED_SECRET = "grandmarina-hydroficient-2024-secret-key"

# =============================================================================
# REPLAY DEFENSE: Configuration
# =============================================================================
MAX_AGE_SECONDS = 30  # Reject messages older than 30 seconds

# Track the last sequence number seen from each device
device_counters = {}

# Statistics
stats = {"accepted": 0, "rejected": 0}

# Dashboard server instance (initialized in main)
dashboard = None


# This function will send data to a splunk dashboard that I have created
# Instead of the given dashboard.
def send_to_splunk(data, event_type, device, topic, failed_check=None):
    # Logic to determine the zone based on the topic structure
    # If topic is .../device-001/sensors, we map it to main_building
    topic_parts = topic.split("/")
    raw_zone = topic_parts[-2] if len(topic_parts) > 2 else "unknown"
    
    # Mapping device IDs or topic strings to the zones used in your XML
    zone_map = {
        "device-001": "main_building",
        "device-002": "pool_spa",
        "device-003": "kitchen"
    }
    final_zone = zone_map.get(raw_zone, "main_building")

    payload = {
        "index": SPLUNK_INDEX,
        "sourcetype": "water_sensor",
        "event": {
            "event_type":     event_type,
            "device_id":      device,
            "topic":          topic,
            "zone":           final_zone,  # Now matches your XML filters
            "pressure_psi":   data.get("readings", {}).get("pressure_upstream"), # Fixed mapping
            "flow_rate_gpm":  data.get("readings", {}).get("flow_rate"),        # Fixed mapping
            "valve_position": data.get("readings", {}).get("gate_a_position"), # Fixed mapping
            "sequence":       data.get("sequence"),
            "timestamp":      data.get("timestamp"),
            "failed_check":   failed_check           
        }
    }
    
    headers = {
        "Authorization": f"Splunk {SPLUNK_HEC_TOKEN}",
        "Content-Type": "application/json"
    }
    try:
        requests.post(SPLUNK_HEC_URL, data=json.dumps(payload), headers=headers, timeout=2)
    except Exception as e:
        print(f"[HEC] Failed: {e}")


# =============================================================================
# HMAC Verification
# =============================================================================
def verify_hmac(message_dict):
    """
    Verify the HMAC signature on a message.
    Returns (True, "") if valid, (False, reason) if invalid.
    """
    received_hmac = message_dict.get("hmac")
    if received_hmac is None:
        return False, "No HMAC field in message"

    msg_copy   = {k: v for k, v in message_dict.items() if k != "hmac"}
    msg_string = json.dumps(msg_copy, sort_keys=True)

    expected_hmac = hmac.new(
        SHARED_SECRET.encode("utf-8"),
        msg_string.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

    if hmac.compare_digest(received_hmac, expected_hmac):
        return True, ""
    else:
        return False, "HMAC mismatch"


# =============================================================================
# Timestamp Validation
# =============================================================================
def check_timestamp(message_dict):
    """
    Check if the message timestamp is within the acceptable window.
    Returns (True, age_seconds) if fresh, (False, age_seconds) if stale.
    """
    timestamp_str = message_dict.get("timestamp")
    if timestamp_str is None:
        return False, -1

    try:
        msg_time = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
        now      = datetime.now(timezone.utc)
        age      = (now - msg_time).total_seconds()

        if age <= MAX_AGE_SECONDS:
            return True, age
        else:
            return False, age
    except (ValueError, TypeError):
        return False, -1


# =============================================================================
# Sequence Counter Validation
# =============================================================================
def check_sequence(message_dict):
    """
    Check if the sequence number is higher than the last seen.
    Returns (True, "") if valid, (False, reason) if replay detected.
    """
    device_id = message_dict.get("device_id", "unknown")
    sequence  = message_dict.get("sequence")

    if sequence is None:
        return False, "No sequence field in message"

    last_seen = device_counters.get(device_id, 0)

    if sequence > last_seen:
        device_counters[device_id] = sequence
        return True, ""
    else:
        return False, f"Sequence {sequence} <= last seen {last_seen}"


# =============================================================================
# Combined Validation
# =============================================================================
def validate_message(message_dict):
    """
    Run all three checks: HMAC -> Timestamp -> Sequence.
    Returns (True, results_dict) or (False, results_dict).
    """
    results = {
        "hmac":      {"passed": False, "detail": ""},
        "timestamp": {"passed": False, "detail": ""},
        "sequence":  {"passed": False, "detail": ""}
    }

    # Check 1: HMAC
    hmac_ok, hmac_reason = verify_hmac(message_dict)
    results["hmac"]["passed"] = hmac_ok
    results["hmac"]["detail"] = "Valid" if hmac_ok else hmac_reason
    if not hmac_ok:
        return False, results

    # Check 2: Timestamp freshness
    ts_ok, age = check_timestamp(message_dict)
    if age >= 0:
        results["timestamp"]["detail"] = f"Age: {age:.1f}s (max: {MAX_AGE_SECONDS}s)"
    else:
        results["timestamp"]["detail"] = "Missing or invalid timestamp"
    results["timestamp"]["passed"] = ts_ok
    if not ts_ok:
        return False, results

    # Check 3: Sequence counter
    seq_ok, seq_reason = check_sequence(message_dict)
    results["sequence"]["passed"] = seq_ok
    results["sequence"]["detail"] = "Valid (new sequence)" if seq_ok else seq_reason
    if not seq_ok:
        return False, results

    return True, results


# =============================================================================
# Callbacks
# =============================================================================
def on_connect(client, userdata, flags, rc):
    """Called when connection is established."""
    if rc == 0:
        print(f"[SUCCESS] Connected to broker as {CLIENT_NAME}")
        print(f"[INFO] Replay defenses ACTIVE")
        print(f"[INFO]   HMAC verification: ON")
        print(f"[INFO]   Timestamp window:  {MAX_AGE_SECONDS} seconds")
        print(f"[INFO]   Sequence tracking: ON")
        print(f"[INFO]   Live dashboard:    ON")
        print(f"[INFO]   Splunk HEC:        ON")
        print(f"[INFO] Subscribing to: {TOPIC}")
        client.subscribe(TOPIC, qos=1)
    else:
        print(f"[ERROR] Connection failed with code {rc}")


def on_message(client, userdata, msg):
    """Called when a message is received. Validates and pushes to dashboard + Splunk."""
    try:
        data = json.loads(msg.payload.decode())

        # Run all validation checks
        accepted, results = validate_message(data)

        device = data.get("device_id", "Unknown")
        flow   = data.get("readings", {}).get("flow_rate", "N/A")
        seq    = data.get("sequence", "N/A")

        if accepted:
            stats["accepted"] += 1

            print(f"\n[ACCEPTED] Device: {device} | Flow: {flow} LPM | Seq: {seq}")
            print(f"  HMAC: PASS | Timestamp: PASS ({results['timestamp']['detail']}) | Sequence: PASS")

            # Push to local WebSocket dashboard
            if dashboard:
                sensor_data = data.get("readings", {})
                dashboard.log_valid_message(device, sensor_data, msg.topic)

            # Send to Splunk — no failed_check for valid messages
            send_to_splunk(data, "valid", device, msg.topic, failed_check=None)

        else:
            stats["rejected"] += 1

            # FIX 2: determine failed_check BEFORE calling send_to_splunk
            #         previously send_to_splunk was called before this loop,
            #         so failed_check was always "unknown" in Splunk events
            failed_check = "unknown"
            reason       = "unknown"
            for check_name in ["hmac", "timestamp", "sequence"]:
                if not results[check_name]["passed"]:
                    failed_check = check_name.upper()
                    reason       = results[check_name]["detail"]
                    break

            print(f"\n[REJECTED] Device: {device} | Flow: {flow} LPM | Seq: {seq}")
            print(f"  Failed check: {failed_check}")
            print(f"  Reason: {reason}")

            # Push to local WebSocket dashboard
            if dashboard:
                attack_types = {
                    "HMAC":      "Message Tampering",
                    "TIMESTAMP": "Stale Message",
                    "SEQUENCE":  "Replay Attack"
                }
                attack_type = attack_types.get(failed_check, "Security Violation")
                dashboard.log_rejected_message(reason, attack_type, device, msg.topic)

            send_to_splunk(data, "attack", device, msg.topic, failed_check=failed_check)

        # Show running stats
        total = stats["accepted"] + stats["rejected"]
        print(f"  Stats: {stats['accepted']} accepted, {stats['rejected']} rejected ({total} total)")

    except json.JSONDecodeError:
        print(f"\n[REJECTED] Non-JSON message on {msg.topic}")
        stats["rejected"] += 1
        if dashboard:
            dashboard.log_rejected_message(
                "Invalid JSON", "Missing Fields", "unknown", msg.topic
            )


def on_subscribe(client, userdata, mid, granted_qos):
    """Called when subscription is confirmed."""
    print(f"[SUBSCRIBED] QoS granted: {granted_qos}")


# =============================================================================
# Main DASHBOARD IS NO LONGER REQUIRED SINCE WE ARE USING SPLUNK INSTEAD, BUT I LEFT IT IN CASE YOU WANT TO TEST LOCALLY WITHOUT SPLUNK
# =============================================================================
def main():
    global dashboard

    print("=" * 60)
    print("Grand Marina Security Dashboard (Live)")
    print("=" * 60)
    print(f"Subscribing to:  {TOPIC}")
    print(f"Certificate:     {CLIENT_CERT}")
    print(f"Max message age: {MAX_AGE_SECONDS} seconds")
    print(f"Dashboard:       http://localhost:8000")
    print(f"Splunk HEC:      {SPLUNK_HEC_URL}")
    print("=" * 60)

    # Start the dashboard server in a background thread
    #dashboard = DashboardServer()

    #def run_dashboard():
        #try:
            #dashboard.start(open_browser=True)
        #except Exception as e:
           # print(f"[ERROR] Dashboard server failed: {e}")

    #dash_thread = threading.Thread(target=run_dashboard, daemon=True)
   #dash_thread.start()
    #time.sleep(2)  # give servers time to bind

    # Set up MQTT client
    client = mqtt.Client(client_id=CLIENT_NAME, **MQTT_CLIENT_ARGS)
    client.on_connect   = on_connect
    client.on_message   = on_message
    client.on_subscribe = on_subscribe

    # Configure mTLS
    try:
        client.tls_set(
            ca_certs    = CA_CERT,
            certfile    = CLIENT_CERT,
            keyfile     = CLIENT_KEY,
            cert_reqs   = ssl.CERT_REQUIRED,
            tls_version = ssl.PROTOCOL_TLS
        )
    except FileNotFoundError as e:
        print(f"[ERROR] Certificate not found: {e}")
        print("[ERROR] Make sure your Project 5 certs/ directory is set up")
        return
    except Exception as e:
        print(f"[ERROR] TLS configuration failed: {e}")
        return

    print(f"\n[CONNECTING] {BROKER_HOST}:{BROKER_PORT}...")
    try:
        client.connect(BROKER_HOST, BROKER_PORT, keepalive=60)
    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")
        return

    print("[LISTENING] Waiting for messages (Ctrl+C to stop)...\n")
    try:
        client.loop_forever()
    except KeyboardInterrupt:
        print(f"\n\n[INFO] Shutting down...")
        print(f"[STATS] Accepted: {stats['accepted']} | Rejected: {stats['rejected']}")

    client.disconnect()
    print("[INFO] Disconnected from broker")


if __name__ == "__main__":
    main()
