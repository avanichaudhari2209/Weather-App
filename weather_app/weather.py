# weather.py

import requests
from config import API_KEY

def get_weather(city):
    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?q={city}&units=metric&appid={API_KEY}"
    )

    try:
        res = requests.get(url, timeout=10)
        data = res.json()

        if data.get("cod") != 200:
            return None

        return {
            "city": data["name"],
            "temp": data["main"]["temp"],
            "humidity": data["main"]["humidity"],
            "condition": data["weather"][0]["main"],          # ← USED FOR ICON
            "description": data["weather"][0]["description"] # ← DISPLAY ONLY
        }

    except Exception:
        return None