import telebot
from telebot import types
import json
import requests

API_TOKEN = '6782588844:AAFAAvegHa69wLYLVctvbXr9l053G6zwMV0'
API_KEY_WHETHER = 'a37ca20319fd9887bd39010d7fe19967'
API_KEY_LOCATION = '40fe680b2b464d98b1510cd301a6e2bf'
bot = telebot.TeleBot(API_TOKEN)

# Load your JSON data
with open('countries-api.json', 'r', encoding='utf-8') as file:
    location_data = json.load(file)

def get_weather_emoji(description):
    if 'rain' in description:
        return '🌧'
    elif 'cloud' in description:
        return '☁️'
    elif 'sunny' in description:
        return '☀️'
    elif 'snow' in description:
        return '❄️'
    elif 'clear' in description:
        return '🌤'
    else:
        return '🌈'
def get_weather(city_name):
    API_KEY = API_KEY_WHETHER
    base_url = "http://api.openweathermap.org/data/2.5/weather?"

    complete_url = f"{base_url}appid={API_KEY}&q={city_name}"
    response = requests.get(complete_url)
    weather_data = response.json()

    if weather_data['cod'] == 200:
        main = weather_data['main']
        temperature = main['temp']
        humidity = main['humidity']
        weather_description = weather_data['weather'][0]['description']
        # Get the appropriate emoji for the weather description
        weather_emoji = get_weather_emoji(weather_description.lower())

        weather_info = f"Temperature: {temperature - 273.15:.2f}°C\n"
        weather_info += f"Humidity: {humidity}%\n"
        weather_info += f"Description: {weather_description.capitalize()} {weather_emoji}\n"  # Include the emoji in the description
        return weather_info
    else:
        return "Weather information not available."

def extract_info(location):
    info = f"Country Name: {location['name']['common']}\n"
    info += f"Capital Name: {', '.join(location['capital'])}\n"
    info += f"Population: {location['population']}\n"
    info += f"Flag: {location['flags']['png']}\n"
    return info
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    button_geo = types.KeyboardButton(text="Your Location", request_location=True)
    button_country = types.KeyboardButton(text="Enter Country")
    markup.add(button_geo, button_country)
    bot.send_message(message.chat.id, "Choose an option:", reply_markup=markup)

@bot.message_handler(content_types=['location'])
def handle_location(message):
    latitude = message.location.latitude
    longitude = message.location.longitude

    city_name, country_name, country_flag = get_location_info(latitude, longitude)
    weather_info = get_weather(city_name)

    # Assuming population information is included in your JSON data for countries
    population = "Population data not available."
    for country in location_data:
        if country['name']['common'].lower() == country_name.lower():
            population = country['population']

    response = f"Country: {country_name}\nCity: {city_name}\nWeather Info: {weather_info}\nPopulation: {population}\nFlag: {country_flag}"
    bot.send_message(message.chat.id, response)

def get_location_info(latitude, longitude):
    API_KEY = API_KEY_LOCATION
    url = f'https://api.opencagedata.com/geocode/v1/json?q={latitude}+{longitude}&key={API_KEY}'
    response = requests.get(url).json()
    if response['results']:
        components = response['results'][0]['components']
        city_name = (components.get('city') or components.get('town') or
                     components.get('village') or components.get('state_district') or
                     "Unknown City")
        country_name = components.get('country', 'Unknown Country')
        country_code = components.get('country_code', '').lower()
        country_flag = f"https://flagcdn.com/w320/{country_code}.png"

        return city_name, country_name, country_flag
    else:
        return "Unknown Location", "Unknown Country", ""

# def get_location_info(latitude, longitude):
#     API_KEY = API_KEY_LOCATION  # Use your OpenCage API key
#     url = f'https://api.opencagedata.com/geocode/v1/json?q={latitude}+{longitude}&key={API_KEY}'
#     response = requests.get(url).json()
#     city_name = response['results'][0]['components'].get('city', 'Unknown City')
#     country_name = response['results'][0]['components'].get('country', 'Unknown Country')
#     country_code = response['results'][0]['components'].get('country_code', '').lower()
#     country_flag = f"https://flagcdn.com/w320/{country_code}.png"
#
#     return city_name, country_name, country_flag

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    if message.text.lower() == "enter country":
        msg = bot.reply_to(message, "Please enter the name of the country:")
        bot.register_next_step_handler(msg, process_country_info)
    else:
        bot.reply_to(message, "Please select an option from the keyboard.")

def process_country_info(message):
    country_name = message.text.strip().lower()
    country_found = False  # Flag to check if the country is found

    for location in location_data:
        if location['name']['common'].lower() == country_name:
            weather_info = get_weather(location['capital'][0])
            info = extract_info(location)
            info += "\nWeather Info:\n" + weather_info
            bot.send_message(message.chat.id, info)
            country_found = True
            break

    if not country_found:
        bot.send_message(message.chat.id, "Sorry, I couldn't find information for the country you entered. Please make sure the country name is spelled correctly.")



bot.infinity_polling()