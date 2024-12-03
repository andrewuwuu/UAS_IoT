# sensor_data.py

class SensorData:
    """Class to store the latest sensor data."""
    def __init__(self):
        self.temperature = None
        self.humidity = None
        self.ultrasonic_distance = None

    def update_temperature(self, temp):
        self.temperature = float(temp)
        print(f"Updated temperature: {self.temperature}°C")

    def update_humidity(self, hum):
        self.humidity = float(hum)
        print(f"Updated humidity: {self.humidity}%")

    def update_ultrasonic_distance(self, distance):
        self.ultrasonic_distance = float(distance)
        print(f"Updated distance: {self.ultrasonic_distance} cm")

    def is_ready(self):
        return (self.temperature is not None and 
                self.humidity is not None and 
                self.ultrasonic_distance is not None)

    def reset(self):
        self.temperature = None
        self.humidity = None
        self.ultrasonic_distance = None