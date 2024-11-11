# mqtt_handler.py

import paho.mqtt.client as mqtt
from config import BROKER_ADDRESS, MQTT_TOPIC_TEMPERATURE, MQTT_TOPIC_HUMIDITY, MQTT_TOPIC_ULTRASONIC, MQTT_TOPIC_RESPONSE

class MqttHandler:
    """Class to handle MQTT connections and messaging."""
    def __init__(self, sensor_data, groq_client):
        self.client = mqtt.Client()
        self.sensor_data = sensor_data
        self.groq_client = groq_client
        self.setup_callbacks()
        self.broker_address = BROKER_ADDRESS

    def setup_callbacks(self):
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
            client.subscribe(MQTT_TOPIC_TEMPERATURE)
            client.subscribe(MQTT_TOPIC_HUMIDITY)
            client.subscribe(MQTT_TOPIC_ULTRASONIC)  # Subscribe to ultrasonic sensor topic
        else:
            print(f"Failed to connect, return code {rc}")

    def on_message(self, client, userdata, msg):
        try:
            # Handle DHT messages only if stop_dht is False
            if msg.topic == MQTT_TOPIC_TEMPERATURE and not self.sensor_data.stop_dht:
                self.sensor_data.update_temperature(msg.payload.decode())
            elif msg.topic == MQTT_TOPIC_HUMIDITY and not self.sensor_data.stop_dht:
                self.sensor_data.update_humidity(msg.payload.decode())
            elif msg.topic == MQTT_TOPIC_ULTRASONIC:
                # Update ultrasonic data and set flag to stop DHT data processing
                self.sensor_data.update_ultrasonic_distance(msg.payload.decode())

            if self.sensor_data.is_ready():
                prediction = self.groq_client.get_prediction(
                    self.sensor_data.temperature,
                    self.sensor_data.humidity,
                    self.sensor_data.ultrasonic_distance
                )
                if prediction:
                    self.publish_response(prediction)
                self.sensor_data.reset()  # Reset to start listening to DHT data again

        except Exception as e:
            print(f"Error processing message: {e}")

    def publish_response(self, response_message):
        self.client.publish(MQTT_TOPIC_RESPONSE, response_message)
        print(f"Published response to {MQTT_TOPIC_RESPONSE}")

    def connect_and_run(self):
        self.client.connect(self.broker_address)
        self.client.loop_forever()