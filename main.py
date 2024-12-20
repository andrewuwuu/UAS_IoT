# main.py
from data_sensor import SensorData
from groq_client import GroqClient
from mqtt_handler import MqttHandler

if __name__ == "__main__":
    sensor_data = SensorData()
    groq_client = GroqClient()
    mqtt_handler = MqttHandler(sensor_data, groq_client)
    
    mqtt_handler.connect_and_run()