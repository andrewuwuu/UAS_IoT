# groq_client.py

import requests
from config import GROQ_ENDPOINT, GROQ_API_KEY

class GroqClient:
    """Class to interact with the GROQ API."""
    def __init__(self):
        self.endpoint = GROQ_ENDPOINT
        self.api_key = GROQ_API_KEY

    def get_prediction(self, temperature, humidity, distance):
        """Send a prediction request to GROQ and return the response."""
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a professor in electrical engineering. "
                    "You use bahasa Indonesia as your native language. You are also "
                    "expertise in IoT and natural disaster detection using sensors"
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Bagaimana kita dapat memperkirakan kondisi lingkungan dari hasil pembacaan "
                    f"beberapa sensor berikut {{DHT22:kelembapan={humidity}, suhu={temperature}, "
                    f"HC-SR04:jarak={distance} cm}}. "
                    f"Jika jarak pembacaan HC-SR04 < 50 cm, maka berarti terdapat genangan dan anda "
                    f"bisa mengabaikan input dari DHT, sehingga anda dapat fokus menganalisis genangan yang terjadi. "
                    f"Jawab dengan respon dalam 1 atau 2 kalimat. Jawab hanya dengan prediksi saja."
                ),
            },
        ]
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "messages": messages,
            "model": "llama-3.2-90b-vision-preview"
        }
        response = requests.post(self.endpoint, headers=headers, json=data)
        if response.status_code == 200:
            response_data = response.json()
            return response_data.get("choices", [{}])[0].get("message", {}).get("content", "No content in response")
        else:
            print(f"Failed to get a valid response from GROQ: {response.status_code}, {response.text}")
            return None