# sensor_data.py

class SensorData:
    """Class to store the latest sensor data."""
    def __init__(self):
        self.temperature = None
        self.humidity = None
        self.ultrasonic_distance = None  # Attribute for ultrasonic sensor data
        self.stop_dht = False  # Flag to control DHT processing

    def update_temperature(self, temp):
        if not self.stop_dht:  # Process only if stop_dht is False
            self.temperature = float(temp)
            print(f"Updated temperature: {self.temperature}°C")

    def update_humidity(self, hum):
        if not self.stop_dht:  # Process only if stop_dht is False
            self.humidity = float(hum)
            print(f"Updated humidity: {self.humidity}%")

    def update_ultrasonic_distance(self, distance):
        self.ultrasonic_distance = float(distance)
        self.stop_dht = True  # Stop processing DHT data upon receiving ultrasonic input
        print(f"Updated distance: {self.ultrasonic_distance} cm - Stopping DHT updates.")

    def is_ready(self):
        # Ready only when all required data (temperature, humidity, and distance) is available
        return (self.temperature is not None and 
                self.humidity is not None and 
                self.ultrasonic_distance is not None)

    def reset(self):
        self.temperature = None
        self.humidity = None
        self.ultrasonic_distance = None
        self.stop_dht = False  # Reset the stop flag to resume DHT processing