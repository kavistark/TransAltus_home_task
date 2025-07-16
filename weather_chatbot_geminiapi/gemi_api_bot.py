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
            return f"❌ City '{city}' not found."

        target_date = datetime.now()
        if day == "tomorrow":
            target_date += timedelta(days=1)

        rain_expected = False
        for entry in res['list']:
            forecast_time = datetime.strptime(entry['dt_txt'], "%Y-%m-%d %H:%M:%S")
            if forecast_time.date() == target_date.date():
                weather_descriptions = [w['main'].lower() for w in entry['weather']]
                if "rain" in weather_descriptions:
                    rain_expected = True
                    break

        if rain_expected:
            return f"✅ Yes, it will likely rain in {city} {day}."
        else:
            return f"❌ No, there is no rain expected in {city} {day}."

    except Exception as e:
        return f"Error checking forecast: {e}"

# ========== GET TEMPERATURE ==========
def get_temperature(city):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
        res = requests.get(url).json()

        if res.get("cod") != 200:
            return f"❌ City '{city}' not found."

        temp = res['main']['temp']
        condition = res['weather'][0]['description'].capitalize()

        return f"🌡️ The temperature in {city} is {temp}°C with {condition}."
    except Exception as e:
        return f"Error fetching temperature: {e}"

# ========== MAIN CHATBOT LOOP ==========
def chatbot():
    print("🤖 WeatherBot is ready! Ask about rain or temperature. (Type 'exit' to quit)")
    while True:
        user_input = input("🧑 You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("🤖 Goodbye! ☀️")
            break

        city, day, intent = extract_city_day_intent(user_input)

        if city.lower() == "unknown":
            print("🤖 I couldn't detect the city. Please rephrase your question.")
            continue

        print("🤖 Let me check that for you...")

        if intent == "raincheck":
            print(will_it_rain(city, day))
        elif intent == "temperature":
            print(get_temperature(city))
        else:
            print("🤖 I'm not sure what you're asking. Try asking about rain or temperature.")

# ========== RUN ==========
if __name__ == "__main__":
    chatbot()
