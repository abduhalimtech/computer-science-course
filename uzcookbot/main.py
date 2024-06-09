import telebot
from telebot import types
import requests
from collections import defaultdict

# Replace with your actual bot token
TOKEN = '6927864805:AAHUXDLgt649w-fQT2jqkS1ykNjkAZIUA7M'
bot = telebot.TeleBot(TOKEN)

API_BASE_URL = 'http://localhost:8000/api'  # Replace with your actual API base URL

# Global dictionary to store user favorites
user_favorites = defaultdict(list)
# Global dictionary to store user feedback
user_feedback = defaultdict(list)
user_data = {}  # Global dictionary to store user preferences


# Start command
@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row('Recipe Search', 'Dietary Search')
    markup.row('Favorites', 'Get Random Recipe')
    markup.row('Help', 'Feedback')

    bot.send_message(message.chat.id, "Welcome to UzCook! What would you like to do today?", reply_markup=markup)


# Handle 'Recipe Search'
@bot.message_handler(func=lambda message: message.text == 'Recipe Search')
def recipe_search(message):
    msg = bot.reply_to(message, "Please enter ingredients separated by commas (e.g., onion, potato).")
    bot.register_next_step_handler(msg, process_ingredients)


# Handle 'Dietary Search'
@bot.message_handler(func=lambda message: message.text == 'Dietary Search')
def dietary_search(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Less than 15min', callback_data='prep_less_15'))
    markup.add(types.InlineKeyboardButton('Around 30min', callback_data='prep_around_30'))
    markup.add(types.InlineKeyboardButton('More than 45min', callback_data='prep_more_45'))
    markup.add(types.InlineKeyboardButton('Skip', callback_data='prep_skip'))
    bot.send_message(message.chat.id, "Select your preferred prep time or skip:", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith('prep_'))
def prep_time_handler(call):
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


# Handle 'Favorites'
@bot.message_handler(func=lambda message: message.text == 'Favorites')
def favorites(message):
    user_id = message.chat.id
    response = requests.get(f'{API_BASE_URL}/user-favorites/{user_id}')
    if response.status_code == 200:
        favorites = response.json()
        if favorites:
            favorites_str = '\n\n'.join([f['recipe']['name'] for f in favorites])
            bot.reply_to(message, f"Here are your favorite recipes:\n\n{favorites_str}")
        else:
            bot.reply_to(message, "You have no favorite recipes yet. Use the heart button to add recipes to your favorites.")
    else:
        bot.reply_to(message, "An error occurred while fetching your favorites.")



# Handle 'Get Random Recipe'
@bot.message_handler(func=lambda message: message.text == 'Get Random Recipe')
def get_random_recipe(message):
    response = requests.get(f'{API_BASE_URL}/random-recipe')
    if response.status_code == 200:
        recipe = response.json()
        recipe_info = format_recipe_details(recipe)
        send_recipe_with_favorite_option(message.chat.id, {"name": recipe['name'], "details": recipe_info})
    else:
        bot.reply_to(message, "An error occurred while fetching a random recipe.")


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

    response = requests.get(f'{API_BASE_URL}/recipes')
    if response.status_code == 200:
        all_recipes = response.json()
        matched_recipes = []
        for recipe in all_recipes:
            if any(ingredient in [ing['name'].lower() for ing in recipe['ingredients']] for ingredient in user_ingredients):
                matched_recipes.append(recipe)

        if matched_recipes:
            for recipe in matched_recipes:
                recipe_info = format_recipe_details(recipe)
                send_recipe_with_favorite_option(message.chat.id, {"name": recipe['name'], "details": recipe_info})
        else:
            bot.send_message(message.chat.id, "No recipes found with these ingredients. Please try different ones.")
    else:
        bot.send_message(message.chat.id, "An error occurred while fetching recipes.")


def send_recipe_with_favorite_option(chat_id, recipe):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('❤️ Add to Favorites', callback_data=f'fav_{recipe["name"][:32]}'))
    bot.send_message(chat_id, recipe["details"], reply_markup=markup)
@bot.callback_query_handler(func=lambda call: call.data.startswith('fav_'))
def add_favorite_handler(call):
    recipe_name = call.data.replace('fav_', '')
    user_id = call.message.chat.id
    recipe_id = get_recipe_id_by_name(recipe_name)
    if recipe_id:
        response = requests.post(f'{API_BASE_URL}/user-favorites', json={'customer_id': user_id, 'recipe_id': recipe_id})
        if response.status_code == 201:
            bot.answer_callback_query(call.id, "Recipe added to favorites!")
        else:
            bot.answer_callback_query(call.id, "An error occurred while adding the recipe to favorites.")
    else:
        bot.answer_callback_query(call.id, "Recipe not found.")

# Helper function to get recipe ID by name
def get_recipe_id_by_name(recipe_name):
    response = requests.get(f'{API_BASE_URL}/recipes')
    if response.status_code == 200:
        all_recipes = response.json()
        for recipe in all_recipes:
            if recipe['name'] == recipe_name:
                return recipe['id']
    return None


# Functions to format recipes
def format_recipe_details(recipe):
    ingredients_str = ', '.join([ingredient['name'] for ingredient in recipe['ingredients']])
    diet_type = recipe.get('diet_type', 'Not specified')  # Default value if 'diet_type' is missing
    nutritional_info = recipe.get('nutritional_info', {})
    calories = nutritional_info.get('calories', 'N/A')
    protein = nutritional_info.get('protein', 'N/A')
    carbohydrates = nutritional_info.get('carbohydrates', 'N/A')
    fats = nutritional_info.get('fats', 'N/A')
    fiber = nutritional_info.get('fiber', 'N/A')
    sugar = nutritional_info.get('sugar', 'N/A')

    recipe_info = (
        f"🍴 {recipe['name']}\n"
        f"🥬 Ingredients: {ingredients_str}\n"
        f"⏳ Prep Time: {recipe['prep_time']} mins\n"
        f"📝 Instructions: {recipe['cooking_instructions']}\n"
        f"🔥 Difficulty: {recipe['difficulty']}\n"
        f"🌍 Cuisine: {recipe['cuisine']}\n"
        f"🍏 Diet: {diet_type}\n"
        f"📊 Nutritional Info: Calories: {calories}, "
        f"Protein: {protein}, Carbs: {carbohydrates}, "
        f"Fats: {fats}, Fiber: {fiber}, "
        f"Sugar: {sugar}"
    )
    return recipe_info



# Functions to find and format recipes based on preferences
def matches_prep_time(preference, recipe_minutes):
    time_mapping = {
        'less_15': (0, 15),
        'around_30': (15, 45),
        'more_45': (45, 999),  # Assuming no recipe takes more than 999 minutes
        'skip': (0, 999)
    }
    min_time, max_time = time_mapping.get(preference, (0, 999))
    return min_time <= recipe_minutes < max_time


def find_recipes_with_preferences(preferences):
    response = requests.get(f'{API_BASE_URL}/recipes')
    if response.status_code == 200:
        all_recipes = response.json()
        filtered_recipes = []
        for recipe in all_recipes:
            matches_preference = True

            # Check preparation time preference
            if preferences.get('prep_time', 'skip') != 'skip' and not matches_prep_time(preferences['prep_time'], recipe['prep_time']):
                matches_preference = False
            # Check difficulty preference
            if preferences.get('difficulty', 'skip') != 'skip' and preferences['difficulty'].lower() != recipe['difficulty'].lower():
                matches_preference = False
            # Check cuisine preference
            if preferences.get('cuisine', 'skip') != 'skip' and preferences['cuisine'].lower() != recipe['cuisine'].lower():
                matches_preference = False
            # Check diet type preference
            if preferences.get('diet', 'skip') != 'skip' and preferences['diet'].lower() != recipe['diet_type'].lower():
                matches_preference = False

            if matches_preference:
                recipe_info = format_recipe_details(recipe)
                filtered_recipes.append(recipe_info)

        return filtered_recipes if filtered_recipes else ["No matching recipes found based on the selected preferences."]
    else:
        return ["An error occurred while fetching recipes."]


# Polling
bot.polling(none_stop=True)

