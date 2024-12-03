import requests
from config import GROQ_ENDPOINT, GROQ_API_KEY

class GroqClient:
    """Class to interact with the GROQ API."""

    def __init__(self):
        self.endpoint = GROQ_ENDPOINT
        self.api_key = GROQ_API_KEY

    def create_message_dht(self, temperature, humidity):
        """
        Create a message for DHT sensor data (temperature and humidity).
        """
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a professor in electrical engineering. "
                    "You use bahasa Indonesia as your native language. You are also "
                    "an expert in IoT and natural disaster detection using sensors."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Bagaimana kita dapat memperkirakan kondisi lingkungan dari hasil pembacaan "
                    f"sensor berikut {{DHT22:kelembapan={humidity}, suhu={temperature}}}. "
                    f"Jawab dengan respon dalam 1 atau 2 kalimat. Jawab hanya dengan prediksi saja."
                ),
            },
        ]
        return messages

    def create_message_hcsr04(self, distance):
        """
        Create a message for HC-SR04 sensor data (distance).
        """
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a professor in electrical engineering. "
                    "You use bahasa Indonesia as your native language. You are also "
                    "an expert in IoT and natural disaster detection using sensors."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"HC-SR04 mendeteksi jarak={distance} cm yang lebih kecil dari 50 cm, "
                    f"artinya terdapat genangan. Fokuskan analisis pada genangan yang terjadi."
                ),
            },
        ]
        return messages

    def get_prediction(self, temperature=None, humidity=None, distance=None):
        """Send a prediction request to GROQ and return the response."""
        
        # Determine the type of message based on sensor inputs
        if distance is not None and distance < 50:
            messages = self.create_message_hcsr04(distance)
        elif temperature is not None and humidity is not None:
            messages = self.create_message_dht(temperature, humidity)
        else:
            raise ValueError("Sensor readings are missing. Provide either temperature, humidity, or distance.")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "messages": messages,
            "model": "llama-3.2-90b-vision-preview"
        }

        try:
            print(f"Sending request to GROQ API with: {data}")  # Debug log
            response = requests.post(self.endpoint, headers=headers, json=data)
            response.raise_for_status()  # Raises an HTTPError if the status is 4xx or 5xx
            
            # Parse and return the response content
            response_data = response.json()
            prediction = response_data.get("choices", [{}])[0].get("message", {}).get("content", "No content in response")
            
            # Print the prediction result to the terminal
            print(f"Received response from GROQ: {prediction}")
            return prediction

        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
        except requests.exceptions.ConnectionError:
            print("Error: Unable to connect to the GROQ API. Check your network connection.")
        except requests.exceptions.Timeout:
            print("Error: Request to GROQ API timed out.")
        except requests.exceptions.RequestException as e:
            print(f"An error occurred while making the request to GROQ: {e}")
        
        return None