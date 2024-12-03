import paho.mqtt.client as mqtt
from config import (
    BROKER_ADDRESS,
    MQTT_TOPIC_TEMPERATURE,
    MQTT_TOPIC_HUMIDITY,
    MQTT_TOPIC_ULTRASONIC,
    MQTT_TOPIC_RESPONSE_DHT,
    MQTT_TOPIC_RESPONSE_HCSR04,
)
from groq_client import GroqClient


class MqttHandler:
    """Class to handle MQTT connections and messaging."""

    def __init__(self, sensor_data, groq_client: GroqClient):
        self.client = mqtt.Client()
        self.sensor_data = sensor_data
        self.groq_client = groq_client
        self.broker_address = BROKER_ADDRESS
        self.setup_callbacks()

    def setup_callbacks(self):
        """Setup MQTT client callbacks."""
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, rc):
        """Handle connection to MQTT broker."""
        if rc == 0:
            print("Connected to MQTT Broker!")
            client.subscribe(MQTT_TOPIC_TEMPERATURE)
            client.subscribe(MQTT_TOPIC_HUMIDITY)
            client.subscribe(MQTT_TOPIC_ULTRASONIC)
        else:
            print(f"Failed to connect to MQTT Broker, return code {rc}")

    def on_message(self, client, userdata, msg):
        """Handle incoming MQTT messages."""
        try:
            topic = msg.topic
            payload = msg.payload.decode()
            print(f"Received message on topic {topic}: {payload}")

            # Update sensor data based on topic
            if topic == MQTT_TOPIC_TEMPERATURE:
                self.sensor_data.update_temperature(payload)
            elif topic == MQTT_TOPIC_HUMIDITY:
                self.sensor_data.update_humidity(payload)
            elif topic == MQTT_TOPIC_ULTRASONIC:
                self.sensor_data.update_ultrasonic_distance(payload)

            # Check if all sensor data is ready for prediction
            if self.sensor_data.is_ready():
                self.handle_prediction()
                self.sensor_data.reset()
        except Exception as e:
            print(f"Error processing message: {e}")

    def handle_prediction(self):
        """Request a prediction and publish the response to the appropriate topic."""
        try:
            if (
                self.sensor_data.ultrasonic_distance is not None
                and self.sensor_data.ultrasonic_distance < 50
            ):
                # Use HC-SR04 data for prediction
                prediction = self.groq_client.get_prediction(
                    distance=self.sensor_data.ultrasonic_distance
                )
                sensor_type = "HC-SR04"
            else:
                # Use DHT sensor data for prediction
                prediction = self.groq_client.get_prediction(
                    temperature=self.sensor_data.temperature,
                    humidity=self.sensor_data.humidity,
                )
                sensor_type = "DHT"

            if prediction:
                self.publish_response(prediction, sensor_type)
            else:
                print("Prediction failed or no response received from GROQ API")
        except Exception as e:
            print(f"Error in prediction process: {e}")

    def publish_response(self, response_message, sensor_type):
        """Publish response to the appropriate MQTT topic."""
        if sensor_type == "DHT":
            topic = MQTT_TOPIC_RESPONSE_DHT
        elif sensor_type == "HC-SR04":
            topic = MQTT_TOPIC_RESPONSE_HCSR04
        else:
            raise ValueError(f"Unknown sensor type: {sensor_type}")

        self.client.publish(topic, response_message)
        print(f"Published response to {topic}: {response_message}")

    def connect_and_run(self):
        """Connect to the MQTT broker and start the loop."""
        self.client.connect(self.broker_address)
        print(f"Connecting to MQTT broker at {self.broker_address}...")
        self.client.loop_forever()