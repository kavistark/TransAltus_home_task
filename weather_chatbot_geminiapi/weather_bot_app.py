import streamlit as st
import google.generativeai as genai
import requests
import re
from datetime import datetime, timedelta

# ========== API KEYS ==========
GEMINI_API_KEY = "AIzaSyAy0GZs8J__5g6PfvDi_spezHSeGM-__kg"
WEATHER_API_KEY = "e11bd703e4344f17e1a8ec69bda5c760"

# ========== CONFIGURE GEMINI ==========
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# ========== GEMINI FUNCTION ==========
def ask_gemini(prompt):
    try:
        chat = model.start_chat()
        chat.send_message(prompt)
        return chat.last.text
    except Exception as e:
        return f"Error with Gemini: {e}"

# ========== GEMINI: EXTRACT CITY, DAY, INTENT ==========
def extract_city_day_intent(user_input):
    prompt = f"""
From the following message: "{user_input}", extract:
- City name
- Day (today or tomorrow)
- Intent (temperature / raincheck / unknown)

Format:
City: <city>, Day: today/tomorrow, Intent: temperature/raincheck/unknown
If not clear, return: City: Unknown, Day: today, Intent: unknown
"""
    response = ask_gemini(prompt)

    city_match = re.search(r"City:\s*([\w\s]+)", response)
    day_match = re.search(r"Day:\s*(today|tomorrow)", response)
    intent_match = re.search(r"Intent:\s*(temperature|raincheck|unknown)", response)

    city = city_match.group(1).strip() if city_match else "Unknown"
    day = day_match.group(1) if day_match else "today"
    intent = intent_match.group(1) if intent_match else "unknown"

    return city, day, intent

# ========== CHECK RAIN ==========
def will_it_rain(city, day):
    try:
        url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={WEATHER_API_KEY}&units=metric"
        res = requests.get(url).json()

        if res.get("cod") != "200":
            return f"City '{city}' not found."

        target_date = datetime.now()
        if day == "tomorrow":
            target_date += timedelta(days=1)

        rain_expected = False
        rain_details = []

        for entry in res['list']:
            forecast_time = datetime.strptime(entry['dt_txt'], "%Y-%m-%d %H:%M:%S")
            if forecast_time.date() == target_date.date():
                # Check for explicit rain volume
                rain_volume = entry.get('rain', {}).get('3h', 0)
                if rain_volume > 0:
                    rain_expected = True
                    rain_details.append(f"{forecast_time.strftime('%H:%M')} - {rain_volume} mm")

        if rain_expected:
            times = "\n".join(rain_details)
            return f"Yes, it will likely rain in {city} {day}.\n Rain forecast:\n{times}"
        else:
            return f"No, there is no rain expected in {city} {day}."

    except Exception as e:
        return f"Error checking forecast: {e}"

# ========== GET TEMPERATURE ==========
def get_temperature(city):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
        res = requests.get(url).json()

        if res.get("cod") != 200:
            return f"City '{city}' not found."

        temp = res['main']['temp']
        condition = res['weather'][0]['description'].capitalize()

        return f"🌡️ The temperature in {city} is {temp}°C with {condition}."
    except Exception as e:
        return f"Error fetching temperature: {e}"

# ========== STREAMLIT UI ==========
st.set_page_config(page_title="Gemini WeatherBot", layout="centered")
st.title("Gemini WeatherBot")
st.write("Ask about temperature or rain in any city (today or tomorrow).")

user_input = st.text_input("Type your weather question:")

if user_input:
    with st.spinner("Thinking..."):
        city, day, intent = extract_city_day_intent(user_input)

        if city.lower() == "unknown":
            st.error("I couldn't detect the city. Please rephrase your question.")
        else:
            if intent == "raincheck":
                result = will_it_rain(city, day)
            elif intent == "temperature":
                result = get_temperature(city)
            else:
                result = "I'm not sure what you're asking. Try asking about rain or temperature."

            st.success(result)
