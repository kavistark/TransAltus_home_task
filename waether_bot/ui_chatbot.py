import tkinter as tk
from tkinter import scrolledtext
import pandas as pd
import joblib
from datetime import datetime

model = joblib.load('temperature_prediction_model.pkl')
city_data = pd.read_csv('city_data.csv')

season_map = {'Winter': 0, 'Spring': 1, 'Summer': 2, 'Fall': 3}

def get_season(month):
    if month in [12, 1, 2]: return 'Winter'
    if month in [3, 4, 5]: return 'Spring'
    if month in [6, 7, 8]: return 'Summer'
    return 'Fall'

def available_cities():
    return sorted(city_data['city'].unique())

def extract_city(query):
    for city in city_data['city'].unique():
        if city.lower() in query.lower():
            return city
    return None

def predict_temperature(city):
    now = datetime.now()
    season = get_season(now.month)
    season_num = season_map[season]
    city_row = city_data[city_data['city'].str.lower() == city.lower()]

    if city_row.empty:
        return f"Sorry, I don't have data for {city}."

    humidity = city_row['humidity'].mean()
    pressure = city_row['pressure'].mean()
    wind_speed = city_row['wind_speed'].mean()

    features = pd.DataFrame([{
        'day_of_year': now.timetuple().tm_yday,
        'month': now.month,
        'hour': now.hour,
        'day_of_week': now.weekday(),
        'season_numeric': season_num,
        'humidity': humidity,
        'pressure': pressure,
        'wind_speed': wind_speed
    }])

    temp = model.predict(features)[0]
    temp_celsius = temp - 273.15  
    return f"Predicted temperature in {city}: {temp_celsius:.1f}°C\n💧 Humidity: {humidity:.1f}%, Pressure: {pressure:.1f} hPa"

def chatbot_response(query):
    query = query.lower()
    if "temperature" in query or "temp" in query:
        city = extract_city(query)
        if city:
            return predict_temperature(city)
        else:
            return "Please mention a valid city.\nAvailable cities: " + ", ".join(available_cities())
    elif "cities" in query or "available" in query:
        return "Available cities: " + ", ".join(available_cities())
    elif "help" in query:
        return help_message()
    elif "exit" in query or "bye" in query:
        return "Goodbye!"
    else:
        return "I didn't understand. Type 'help' for options."

def help_message():
    return (
        "- Available Commands:\n""- 'What is the temperature in [city]?'\n""- 'Show cities'\n" "- 'Help'\n"
        "- 'Exit'\n" "- Available cities: " + ", ".join(available_cities())
    )

def send_message():
    user_msg = user_input.get()
    if user_msg.strip() == "":
        return
    chat_window.config(state='normal')
    chat_window.insert(tk.END, f"You: {user_msg}\n")
    response = chatbot_response(user_msg)
    chat_window.insert(tk.END, f"Bot: {response}\n\n")
    chat_window.config(state='disabled')
    chat_window.see(tk.END)
    user_input.delete(0, tk.END)
root = tk.Tk()
root.title("Weather Chatbot")

chat_window = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=80, height=25, state='disabled')
chat_window.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

user_input = tk.Entry(root, width=60)
user_input.grid(row=1, column=0, padx=10, pady=10)

send_button = tk.Button(root, text="Send", width=10, command=send_message)
send_button.grid(row=1, column=1, padx=10, pady=10)

chat_window.config(state='normal')
chat_window.insert(tk.END, "Welcome to the Weather Chatbot!\n")
chat_window.insert(tk.END, help_message() + "\n\n")
chat_window.config(state='disabled')

root.mainloop()
