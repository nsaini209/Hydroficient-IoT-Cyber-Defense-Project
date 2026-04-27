
import paho.mqtt.client as mqtt
from paho.mqtt.client import CallbackAPIVersion
import json
from datetime import datetime
import ssl # FOR TLS

TLS_CONFIG = {
    "ca_certs": "certs/ca.pem",      # Path to CA certificate
    "broker_host": "localhost",
    "broker_port": 8883,              # TLS port (not 1883!)
}

def on_connect(client, userdata, flags, reason_code, properties):
    print("\n" + "=" * 60)
    print("  GRAND MARINA WATER MONITORING DASHBOARD")
    print("  Connected at:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 60)
    client.subscribe("hydroficient/grandmarina/#")

def on_message(client, userdata, msg):
    topic = msg.topic

    if "/sensors/" in topic:
        handle_sensor_reading(msg)
    elif "/alerts/" in topic:
        handle_alert(msg)
    elif "/commands/" in topic:
        handle_command(msg)
    elif "/status/" in topic:
        handle_status(msg)
    else:
        print(f"Unknown topic: {topic}")
        
def handle_sensor_reading(msg):
    try:
        data = json.loads(msg.payload.decode())
        display_reading(data)  # Uses your existing display_reading() function
    except json.JSONDecodeError:
        print(f"\n[RAW SENSOR MESSAGE] {msg.topic}")
        print(f"      {msg.payload.decode()}")

def handle_alert(msg):
    print(f"\n*** ALERT ***")
    print(f"Topic: {msg.topic}")
    print(f"Message: {msg.payload.decode()}")

def handle_command(msg):
    print(f"\n[COMMAND] {msg.topic}: {msg.payload.decode()}")

def handle_status(msg):
    # Could update a "last seen" tracker
    print(f"\n[STATUS] {msg.topic}: {msg.payload.decode()}")

def display_reading(data):
    """Format and display a sensor reading."""
    print(f"\n{'─' * 40}")
    print(f"  Location:  {data.get('location', 'Unknown')}")
    print(f"  Device ID: {data.get('device_id', 'Unknown')}")
    print(f"  Time:      {data.get('timestamp', 'N/A')}")
    print(f"  Count:     #{data.get('counter', 0)}")
    print(f"{'─' * 40}")

    # Pressure readings
    up = data.get('pressure_upstream', 0)
    down = data.get('pressure_downstream', 0)
    print(f"  Pressure (upstream):   {up:6.1f} PSI")
    print(f"  Pressure (downstream): {down:6.1f} PSI")

    # Pressure differential (can indicate blockage)
    diff = up - down
    print(f"  Pressure differential: {diff:6.1f} PSI")

    # Flow rate
    flow = data.get('flow_rate', 0)
    print(f"  Flow rate:             {flow:6.1f} gal/min")

# Create and configure client
client = mqtt.Client(
    client_id="grand-marina-dashboard",
    callback_api_version=CallbackAPIVersion.VERSION2
)
client.on_connect = on_connect
client.on_message = on_message

# CHANGE CERTFILE AND KEYFILE LATER
print("=" * 60)
print("  Grand Marina Security Dashboard (mTLS)")
print("=" * 60)
print(f"  Subscribing to: hydroficient/grandmarina/#")
print(f"  Certificate: certs/device-001.pem")
print("=" * 60)
print("[TLS] mTLS configured with client certificate")
print(f"[CONNECTING] {TLS_CONFIG['broker_host']}:{TLS_CONFIG['broker_port']}...")

client.tls_set(
    ca_certs=TLS_CONFIG["ca_certs"],    # Trust this CA
    certfile="certs/device-001.pem",   # Client certificate (for mTLS)                
    keyfile="certs/device-001-key.pem", # Client private key (for mTLS)                 
    cert_reqs=ssl.CERT_REQUIRED,         # Verify server certificate
    tls_version=ssl.PROTOCOL_TLS,        # Use modern TLS
)

# Connect and run
print("Connecting to broker...")
client.connect(
    TLS_CONFIG["broker_host"],
    TLS_CONFIG["broker_port"],   # Port 8883 not 1883
    keepalive=60
)
client.loop_forever()

"""1. Client starts connection to localhost: 8883
                    │
                    ▼
2. TLS handshake begins
   - Client says "Hello, I support TLS 1.2/1.3"
   - Broker sends server.pem certificate
                    │
                    ▼
3. Client verifies certificate using ca.pem
   - Is it signed by our CA? ✓
   - Is it expired? ✓
   - Does hostname match? ✓
                    │
                    ▼
4. If all checks pass → Encrypted channel established
   If any check fails → Connection refused
                    │
                    ▼
5. MQTT messages flow through encrypted channel
   - Publish, subscribe, etc. work normally
   - All data is encrypted"""