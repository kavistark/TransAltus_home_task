

import requests
import re
from datetime import datetime, timedelta

# Replace with your actual OpenWeatherMap API key
API_KEY = "e11bd703e4344f17e1a8ec69bda5c760"

# URLs for current and forecast data
CURRENT_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"

def extract_city(user_input):
    """
    Extracts the city name from the user input string.
    Handles inputs like:
    - 'What is the temperature in Chennai?'
    - 'Will it rain tomorrow in Delhi?'
    - 'Forecast for Mumbai'
    """
    # Try to capture city after 'in', 'at', or 'for'
    match = re.search(r'\b(?:in|at|for)\s+([a-zA-Z\s]+)', user_input.lower())
    if match:
        city = match.group(1)
    else:
        # If no match, try last 1–2 words as fallback
        words = re.findall(r'\b[a-zA-Z]{3,}\b', user_input)
        city = ' '.join(words[-2:]) if len(words) >= 2 else ' '.join(words)

    return city.strip().title()


def is_forecast_request(user_input):
    """
    Determines if the user is asking for a forecast (e.g., for tomorrow).
    """
    return "tomorrow" in user_input.lower() or "forecast" in user_input.lower()

def get_current_weather(city):
    params = {"q": city, "appid": API_KEY, "units": "metric"}
    response = requests.get(CURRENT_URL, params=params)
    data = response.json()

    if response.status_code != 200 or data.get("cod") != 200:
        return f"❌ City '{city}' not found. Please try another city."

    city = data["name"]
    country = data["sys"]["country"]
    temp = data["main"]["temp"]
    description = data["weather"][0]["description"].capitalize()
    humidity = data["main"]["humidity"]
    wind_speed = data["wind"]["speed"]

    return (
        f"📍 Weather in {city}, {country}:\n"
        f"🌡️ Temperature: {temp}°C\n"
        f"🌤️ Condition: {description}\n"
        f"💧 Humidity: {humidity}%\n"
        f"💨 Wind Speed: {wind_speed} m/s"
    )

def get_tomorrow_forecast(city):
    params = {"q": city, "appid": API_KEY, "units": "metric"}
    response = requests.get(FORECAST_URL, params=params)
    data = response.json()

    if response.status_code != 200 or data.get("cod") != "200":
        return f"❌ City '{city}' not found for forecast. Try again."

    tomorrow = (datetime.utcnow() + timedelta(days=1)).date()

    forecasts = data["list"]
    tomorrow_data = [item for item in forecasts if item["dt_txt"].startswith(str(tomorrow))]

    if not tomorrow_data:
        return "⚠️ No forecast data available for tomorrow."

    rain_expected = any("rain" in item["weather"][0]["main"].lower() for item in tomorrow_data)
    mid_day = tomorrow_data[len(tomorrow_data)//2]

    condition = mid_day["weather"][0]["description"].capitalize()
    temp = mid_day["main"]["temp"]

    return (
        f"🌦️ Forecast for {city} tomorrow:\n"
        f"🌡️ Temperature: {temp}°C\n"
        f"🌤️ Condition: {condition}\n"
        + ("☔ Yes, rain is expected." if rain_expected else "☀️ No rain expected.")
    )

def start_chatbot():
    print("🤖 WeatherBot is ready! Ask about current or tomorrow’s weather.")
    print("Examples:")
    print("   → What is the temperature in Chennai?")
    print("   → Will it rain tomorrow in Delhi?")
    print("Type 'exit' or 'quit' to stop.\n")

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() in ["exit", "quit"]:
            print("👋 Goodbye!")
            break

        city = extract_city(user_input)
        forecast = is_forecast_request(user_input)

        if not city:
            print("Bot: ❌ Could not detect a city in your message.\n")
            continue

        if forecast:
            response = get_tomorrow_forecast(city)
        else:
            response = get_current_weather(city)

        print(f"Bot: {response}\n")

# Run the chatbot
if __name__ == "__main__":
    start_chatbot()
