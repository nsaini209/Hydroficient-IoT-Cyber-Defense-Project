from datetime import datetime, timezone
import random
import json

# MAIN CLASS
class WaterSensor:
    def __init__(self, device_id):
        self.device_id = device_id
        self.counter = 0 # counter starts at 0

        # Base values we have given our sensor
        self.pressure_up = 75.0
        self.pressure_down = 76.0
        self.flow = 35.0

    def get_reading(self):

        #this will generate a normal sensor reading and the counter will add +1 to every new reading
        self.counter += 1

        #Add small random variation ( +- units)

        pressure_up = self.pressure_up + random.uniform(-3, 3)
        pressure_down = self.pressure_down + random.uniform(-3, 3)
        flow = self.flow + random.uniform(-3, 3)
        timestamp = datetime.now(timezone.utc).isoformat()
        return {
            "device_id": self.device_id,
            "counter": self.counter,
            "pressure_upstream": round(pressure_up, 1),
            "pressure_downstream": round(pressure_down, 1),
            "flow_rate":  round(flow, 1),
            "timestamp":  timestamp
        }

# SIMULATING LEAK
    def simulate_leak(self):
     # Simulate a water leak with high flow rate
        reading = self.get_reading()
        reading['flow_rate'] = round(random.uniform(80, 120), 1) #This is way above normal range which is 30, 60
        return reading

# SIMULATING BLOCKAGE
    def simulate_blockage(self):
        """Simulate a pipe blockage with low downstream pressure"""
        reading = self.get_reading()
        reading["pressure_upstream"] = round(random.uniform(85, 95), 1)  # High upstream
        reading["pressure_downstream"] = round(random.uniform(30, 50), 1)  # Low downstream
        return reading

    # SIMULATING STUCK SENSOR
    def simulate_stuck_sensor(self, stuck_value=82.0):
        """Simulate a sensor that's stuck on one value"""
        reading = self.get_reading()
        reading["pressure_upstream"] = stuck_value  # Since we gave the stuck parameter a value of 82.0 it will stay at that number.
        reading["pressure_downstream"] = stuck_value
        reading["flow_rate"] = stuck_value
        return reading
    
#Creating the class sensor
sensor = WaterSensor("House-Kitchen-Sensor")

#Creating the legitimate readings
for i in range(10):
    print(sensor.get_reading())


    #Generating anomalies 
print("\n === Anomalies Detected ===")
print("Leakage Detected:", sensor.simulate_leak())
print("Blockage Detected:", sensor.simulate_blockage())
print("Sensor Issue Detected:", sensor.simulate_stuck_sensor())

#Generate 100 readings
sensor = WaterSensor("House-Kitchen-Sensor")
readings = []

#100 Normal readings
for y in range(100):
    readings.append(sensor.get_reading())

#Additional 15 readings for anomalies
for _ in range(5):
    readings.append(sensor.simulate_leak())
    readings.append(sensor.simulate_blockage())
    readings.append(sensor.simulate_stuck_sensor())

#Saving to JSON file
with open ("sensor_data_today.json", "w") as f:
    json.dump(readings, f, indent=4)

    print(f"\nSaved {len(readings)} readings to sensor_data_today.json")
    