

import telebot
from telebot import types
from fuzzywuzzy import process
from collections import defaultdict
import random

TOKEN = '6927864805:AAHUXDLgt649w-fQT2jqkS1ykNjkAZIUA7M'
bot = telebot.TeleBot(TOKEN)

ingredients_list = ['onion', 'potato', 'tomato', 'carrot', 'bread', 'chicken', 'tomato', 'cabbage']
recipes = {
    'Creamy Tomato Soup': {
        'ingredients': ['tomato', 'onion', 'garlic', 'cream'],
        'prep_time': 10,
        'cooking_instructions': 'Combine ingredients and simmer for 20 mins.',
        'difficulty': 'Easy',
        'cuisine': 'American',
        'diet_type': 'Vegan',
        'nutritional_info': {
            'calories': '250 kcal',
            'protein': '4 g',
            'carbohydrates': '18 g',
            'fats': '18 g',
            'fiber': '2 g',
            'sugar': '12 g'
        }
    },
    'Classic Salad': {
        'ingredients': ['tomato', 'carrot', 'lettuce', 'cucumber'],
        'prep_time': 55,
        'cooking_instructions': 'Chop all ingredients and toss with dressing.',
        'difficulty': 'Easy',
        'cuisine': 'European',
        'diet_type': 'None',
        'nutritional_info': {
            'calories': '120 kcal',
            'protein': '2 g',
            'carbohydrates': '10 g',
            'fats': '7 g',
            'fiber': '3 g',
            'sugar': '4 g'
        }
    }
}
# Global dictionary to store user favorites
user_favorites = defaultdict(list)
# Global dictionary to store user feedback
user_feedback = defaultdict(list)


# Start command
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('Recipe Search', 'Dietary Search')
    markup.row('Favorites', 'Get Random Recipe')
    markup.row('Help', 'Feedback')

    bot.send_message(message.chat.id,
                     "Welcome to UzCook! What would you like to do today?",
                     reply_markup=markup)


# Handle 'Recipe Search'
@bot.message_handler(func=lambda message: message.text == 'Recipe Search')
def recipe_search(message):
    msg = bot.reply_to(message, "Please enter ingredients separated by commas (e.g., onion, potato).")
    bot.register_next_step_handler(msg, process_ingredients)


@bot.message_handler(func=lambda message: message.text == 'Dietary Search')
def dietary_search(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Less than 15min', callback_data='prep_less_15'))
    markup.add(types.InlineKeyboardButton('Around 30min', callback_data='prep_around_30'))
    markup.add(types.InlineKeyboardButton('More than 45min', callback_data='prep_more_45'))
    markup.add(types.InlineKeyboardButton('Skip', callback_data='prep_skip'))
    bot.send_message(message.chat.id, "Select your preferred prep time or skip:", reply_markup=markup)


# Handle 'Favorites'
@bot.message_handler(func=lambda message: message.text == 'Favorites')
def favorites(message):
    user_id = message.chat.id
    if user_favorites[user_id]:
        favorites_str = '\n\n'.join(user_favorites[user_id])
        bot.reply_to(message, f"Here are your favorite recipes:\n\n{favorites_str}")
    else:
        bot.reply_to(message,
                     "You have no favorite recipes yet. Use the heart button to add recipes to your favorites.")


# Handle 'Get Random Recipe'
@bot.message_handler(func=lambda message: message.text == 'Get Random Recipe')
def get_random_recipe(message):
    recipe_name, details = random.choice(list(recipes.items()))
    recipe_info = format_recipe_details(recipe_name, details)
    send_recipe_with_favorite_option(message.chat.id, {"name": recipe_name, "details": recipe_info})


# Handle 'Help'
@bot.message_handler(func=lambda message: message.text == 'Help')
def help_command(message):
    help_text = (
        "Here's how you can use UzCook Bot:\n\n"
        "1. Recipe Search: Enter ingredients separated by commas to find recipes.\n"
        "2. Dietary Search: Select your dietary preferences to find suitable recipes.\n"
        "3. Favorites: View your favorite recipes that you have added.\n"
        "4. Get Random Recipe: Get a random recipe suggestion.\n"
        "5. Help: Display this help message.\n"
        "6. Feedback: Provide your feedback, report bugs, or suggest improvements.\n"
    )
    bot.reply_to(message, help_text)


# Handle 'Feedback'
@bot.message_handler(func=lambda message: message.text == 'Feedback')
def feedback(message):
    msg = bot.reply_to(message, "Please provide your feedback, report bugs, errors, or suggest improvements.")
    bot.register_next_step_handler(msg, save_feedback)


def save_feedback(message):
    user_id = message.chat.id
    user_name = message.from_user.first_name
    user_username = message.from_user.username
    feedback_text = message.text

    feedback_entry = {
        "user_id": user_id,
        "name": user_name,
        "username": user_username,
        "feedback": feedback_text
    }

    user_feedback[user_id].append(feedback_entry)
    bot.reply_to(message, "Thank you for your feedback! It has been recorded.")


# Function to process ingredients and find recipes
def process_ingredients(message):
    user_ingredients = message.text.lower().split(',')
    user_ingredients = [ingredient.strip() for ingredient in user_ingredients]

    confirmed_ingredients = []
    not_found_ingredients = []
    for user_ing in user_ingredients:
        match, score = process.extractOne(user_ing, ingredients_list)
        if score > 80:
            confirmed_ingredients.append(match)
        else:
            not_found_ingredients.append(user_ing)

    if not_found_ingredients:
        not_found_str = ', '.join(not_found_ingredients)
        bot.send_message(message.chat.id,
                         f"'{not_found_str}' were not found in our database, or you have some spelling errors. Please try again!")

    if confirmed_ingredients:
        recipes = find_recipes_with_ingredients(confirmed_ingredients)
        if recipes:
            for recipe in recipes:
                send_recipe_with_favorite_option(message.chat.id, recipe)
        else:
            bot.send_message(message.chat.id, "No recipes found with these ingredients. Please try different ones.")
    elif not not_found_ingredients:
        bot.send_message(message.chat.id, "Please check the ingredients and try again.")


def send_recipe_with_favorite_option(chat_id, recipe):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('❤️ Add to Favorites', callback_data=f'fav_{recipe["name"][:32]}'))
    bot.send_message(chat_id, recipe["details"], reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith('fav_'))
def add_favorite_handler(call):
    recipe_name = call.data.replace('fav_', '')
    user_id = call.message.chat.id
    for name, details in recipes.items():
        if recipe_name == name[:32]:  # Compare truncated name
            user_favorites[user_id].append(format_recipe_details(name, details))
            bot.answer_callback_query(call.id, "Recipe added to favorites!")
            break


# Functions to find and format recipes
def find_recipes_with_ingredients(input_ingredients):
    suggested_recipes = defaultdict(list)
    for recipe_name, details in recipes.items():
        recipe_ingredients = details['ingredients']
        common_ingredients = set(recipe_ingredients) & set(input_ingredients)
        if common_ingredients:
            suggested_recipes[len(common_ingredients)].append({
                "name": recipe_name,
                "details": format_recipe_details(recipe_name, details)
            })

    sorted_recipes = [recipe for count in sorted(suggested_recipes, reverse=True) for recipe in
                      suggested_recipes[count]]
    return sorted_recipes


# -----------------diet search functions:----------------------------
# Assumption: user_data is stored as {chat_id: {preference_type: value}}
user_data = {}  # Global dictionary to store user preferences


@bot.callback_query_handler(func=lambda call: call.data.startswith('prep_'))
def prep_time_handler(call):
    # Extract the user's choice, excluding 'prep_'
    choice = call.data.replace('prep_', '')
    user_data[call.message.chat.id] = {'prep_time': choice}
    # Proceed to ask for difficulty level
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Easy', callback_data='diff_easy'),
               types.InlineKeyboardButton('Medium', callback_data='diff_medium'),
               types.InlineKeyboardButton('Hard', callback_data='diff_hard'),
               types.InlineKeyboardButton('Skip', callback_data='diff_skip'))
    bot.edit_message_text("Select the difficulty or skip:",
                          chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          reply_markup=markup)
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith('diff_'))
def difficulty_handler(call):
    choice = call.data.replace('diff_', '')
    user_data[call.message.chat.id]['difficulty'] = choice
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('American', callback_data='cui_american'),
               types.InlineKeyboardButton('Asian', callback_data='cui_asian'),
               types.InlineKeyboardButton('European', callback_data='cui_european'),
               types.InlineKeyboardButton('Skip', callback_data='cui_skip'))
    bot.edit_message_text("Select the cuisine or skip:",
                          chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          reply_markup=markup)
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith('cui_'))
def cuisine_handler(call):
    choice = call.data.replace('cui_', '')
    user_data[call.message.chat.id]['cuisine'] = choice
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Vegan', callback_data='diet_vegan'),
               types.InlineKeyboardButton('Vegetarian', callback_data='diet_vegetarian'),
               types.InlineKeyboardButton('Gluten-Free', callback_data='diet_gluten_free'),
               types.InlineKeyboardButton('Keto', callback_data='diet_keto'),
               types.InlineKeyboardButton('Skip', callback_data='diet_skip'))
    bot.edit_message_text("Select your dietary preference or skip:",
                          chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          reply_markup=markup)
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith('diet_'))
def diet_handler(call):
    choice = call.data.replace('diet_', '')
    user_data[call.message.chat.id]['diet'] = choice
    recipes = find_recipes_with_preferences(user_data[call.message.chat.id])
    if recipes and recipes[0] != "No matching recipes found based on the selected preferences.":
        for recipe in recipes:
            send_recipe_with_favorite_option(call.message.chat.id,
                                             {"name": recipe.split('\n')[0].strip("🍴 "), "details": recipe})
    else:
        bot.send_message(call.message.chat.id, "No recipes found with these preferences.")
    bot.answer_callback_query(call.id)



def matches_prep_time(preference, recipe_minutes):
    # Mapping prep_time preferences to a range of minutes
    time_mapping = {
        'less_15': (0, 15),
        'around_30': (15, 45),
        'more_45': (45, 999),  # Assuming no recipe takes more than 999 minutes
        'skip': (0, 999)
    }
    min_time, max_time = time_mapping.get(preference, (0, 999))
    return min_time <= recipe_minutes < max_time


def find_recipes_with_preferences(preferences):
    filtered_recipes = []
    for recipe_name, details in recipes.items():
        matches_preference = True

        # Check preparation time preference
        if preferences.get('prep_time', 'skip') != 'skip' and not matches_prep_time(preferences['prep_time'],
                                                                                    details['prep_time']):
            matches_preference = False
        # Check difficulty preference
        if preferences.get('difficulty', 'skip') != 'skip' and preferences['difficulty'].lower() != details[
            'difficulty'].lower():
            matches_preference = False
        # Check cuisine preference
        if preferences.get('cuisine', 'skip') != 'skip' and preferences['cuisine'].lower() != details[
            'cuisine'].lower():
            matches_preference = False
        # Check diet type preference
        if preferences.get('diet', 'skip') != 'skip' and preferences['diet'].lower() != details['diet_type'].lower():
            matches_preference = False

        if matches_preference:
            recipe_info = format_recipe_details(recipe_name, details)
            filtered_recipes.append(recipe_info)

    return filtered_recipes if filtered_recipes else ["No matching recipes found based on the selected preferences."]


def format_recipe_details(recipe_name, details):
    ingredients_str = ', '.join(details['ingredients'])
    recipe_info = f"🍴 {recipe_name}\n" \
                  f"🥬 Ingredients: {ingredients_str}\n" \
                  f"⏳ Prep Time: {details['prep_time']} mins\n" \
                  f"📝 Instructions: {details['cooking_instructions']}\n" \
                  f"🔥 Difficulty: {details['difficulty']}\n" \
                  f"🌍 Cuisine: {details['cuisine']}\n" \
                  f"🍏 Diet: {details['diet_type']}\n" \
                  f"📊 Nutritional Info: Calories: {details['nutritional_info']['calories']}, " \
                  f"Protein: {details['nutritional_info']['protein']}, Carbs: {details['nutritional_info']['carbohydrates']}, " \
                  f"Fats: {details['nutritional_info']['fats']}, Fiber: {details['nutritional_info']['fiber']}, " \
                  f"Sugar: {details['nutritional_info']['sugar']}"
    return recipe_info


# Polling
bot.polling(none_stop=True)

