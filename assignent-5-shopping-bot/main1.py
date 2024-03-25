import re
import telebot
from telebot import types
import mysql.connector

# Database connection setup
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="cs_korzinka"
)

# Telegram bot token
TOKEN = '6741489602:AAGTMECus2iIQ4_Q-2T9gPwdMrgZjr2chtU'

# Create a bot instance
bot = telebot.TeleBot(TOKEN)
user_state = {}
# Helper function to execute database queries
def execute_query(query, params=None, commit=False):
    cursor = mydb.cursor()
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        if commit:
            mydb.commit()
            return cursor.lastrowid
        if query.lstrip().upper().startswith('SELECT'):
            return cursor.fetchall()
    except mysql.connector.Error as err:
        print(f"Error: '{err}'")
        return None
    finally:
        cursor.close()

# Function to show available products to the user
def show_products(chat_id):
    products = execute_query("SELECT product_id, name, price FROM products")
    for product in products:
        bot.send_message(chat_id, f"ID: {product[0]}, Name: {product[1]}, Price: {product[2]}")

# Function to add product to cart
def add_to_cart(telegram_id, product_id, quantity):
    # First, check if the product exists
    product = execute_query("SELECT name, price FROM products WHERE product_id = %s", (product_id,))
    if not product:
        return "Product not found."

    # Add the product to the user's cart
    execute_query(
        "INSERT INTO cart (telegram_id, product_id, quantity) VALUES (%s, %s, %s) "
        "ON DUPLICATE KEY UPDATE quantity = quantity + %s",
        (telegram_id, product_id, quantity, quantity),
        commit=True
    )
    return f"Added {product[0][0]} to your cart."

# Function to get the contents of the user's cart
def get_cart_contents(telegram_id):
    return execute_query(
        "SELECT p.name, c.quantity, p.price FROM cart c "
        "JOIN products p ON c.product_id = p.product_id WHERE c.telegram_id = %s",
        (telegram_id,)
    )

# Function to remove product from cart
def remove_from_cart(telegram_id, product_id):
    execute_query("DELETE FROM cart WHERE telegram_id = %s AND product_id = %s", (telegram_id, product_id), commit=True)
    return "Removed item from cart."

# Start command
@bot.message_handler(commands=['start'])
def command_start(message):
    if is_user_registered(message.from_user.id):
        bot.send_message(message.chat.id, "Welcome back! You can use the following commands:\n"
                                          "/products - Show all products\n"
                                          "/addtocart - Add a product to your cart\n"
                                          "/showcart - Show your cart\n"
                                          "/removefromcart - Remove a product from your cart")
    else:
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        markup.add('Register', 'Login')
        bot.send_message(message.chat.id, "Welcome to our shop! Please register or login.", reply_markup=markup)

# Show products command
@bot.message_handler(commands=['products'])
def command_show_products(message):
    show_products(message.chat.id)

# Add to cart command
@bot.message_handler(commands=['addtocart'])
def command_add_to_cart(message):
    msg = bot.reply_to(message, "Enter the product ID you wish to add to your cart:")
    bot.register_next_step_handler(msg, process_add_to_cart_step)

def process_add_to_cart_step(message):
    try:
        product_id = int(message.text.strip())
        result = add_to_cart(message.from_user.id, product_id, 1)
        bot.send_message(message.chat.id, result)
    except ValueError:
        bot.reply_to(message, "Please enter a valid product ID.")

# Show cart command
@bot.message_handler(commands=['showcart'])
def command_show_cart(message):
    cart_contents = get_cart_contents(message.from_user.id)
    if not cart_contents:
        bot.send_message(message.chat.id, "Your cart is empty.")
    else:
        response = "\n".join([f"{name} - Quantity: {quantity} - Price: {price}" for name, quantity, price in cart_contents])
        bot.send_message(message.chat.id, response)

# Remove from cart command
@bot.message_handler(commands=['removefromcart'])
def command_remove_from_cart(message):
    msg = bot.reply_to(message, "Enter the product ID you wish to remove from your cart:")
    bot.register_next_step_handler(msg, process_remove_from_cart_step)

def process_remove_from_cart_step(message):
    try:
        product_id = int(message.text.strip())
        result = remove_from_cart(message.from_user.id, product_id)
        bot.send_message(message.chat.id, result)
    except ValueError:
        bot.reply_to(message, "Please enter a valid product ID.")

def register_user(telegram_id, username, password, special_question, special_question_answer):

    execute_query("INSERT INTO users (telegram_id, username, password, special_question, special_question_answer) "
                  "VALUES (%s, %s, %s, %s, %s)",
                  (telegram_id, username, password, special_question, special_question_answer),
                  commit=True)
def is_user_registered(telegram_id):
    result = execute_query("SELECT COUNT(1) FROM users WHERE telegram_id = %s", (telegram_id,))
    return result and result[0][0] > 0

def check_user_login(username, password):
    hashed_password = hash_password(password)  # You must implement this
    user = execute_query("SELECT telegram_id FROM users WHERE username = %s AND password = %s",
                         (username, hashed_password))
    return user and user[0][0]

# Handler for text messages - to catch "Register" or "Login"
@bot.message_handler(func=lambda message: message.text in ['Register', 'Login'])
def handle_message(message):
    if message.text == 'Register':
        msg = bot.send_message(message.chat.id, "Please provide a username for registration:")
        bot.register_next_step_handler(msg, process_register_username_step)
    elif message.text == 'Login':
        msg = bot.send_message(message.chat.id, "Please enter your username:")
        bot.register_next_step_handler(msg, process_login_username_step)

# Registration step 1: username
def is_password_strong(password):
    # Implement your own password strength checks here. For example:
    if len(password) < 8:
        return False, "Password too short. Must be at least 8 characters."
    if not any(char.isdigit() for char in password):
        return False, "Password must contain at least one digit."
    if not any(char.isupper() for char in password):
        return False, "Password must contain at least one uppercase letter."
    if not any(char.islower() for char in password):
        return False, "Password must contain at least one lowercase letter."
    if not any(char in "!@#$%^&*()_+" for char in password):
        return False, "Password must contain at least one special character (!@#$%^&*()_+)."
    return True, "Strong password."

# Registration step 2: password
def process_register_password_step(message):
    new_password = message.text.strip()
    password_strength, password_message = is_password_strong(new_password)
    if password_strength:
        user_state[message.chat.id]['password'] = new_password
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        # Add all special questions to the markup
        for sq in SPECIAL_QUESTIONS.values():
            markup.add(sq)
        msg = bot.reply_to(message, "Choose a special question:", reply_markup=markup)
        bot.register_next_step_handler(msg, process_special_question_step)
    else:
        msg = bot.reply_to(message, password_message)
        bot.register_next_step_handler(msg, process_register_password_step)

# Registration step 3: special question
def process_special_question_step(message):
    special_question = message.text.strip()
    if special_question in SPECIAL_QUESTIONS.values():
        user_state[message.chat.id]['special_question'] = special_question
        msg = bot.reply_to(message, "Enter your answer for the special question:")
        bot.register_next_step_handler(msg, process_special_question_answer_step)
    else:
        msg = bot.reply_to(message, "Please choose a valid special question.")
        bot.register_next_step_handler(msg, process_special_question_step)

# Registration step 4: special question answer
def process_special_question_answer_step(message):
    special_question_answer = message.text.strip()
    user_state[message.chat.id]['special_question_answer'] = special_question_answer

    # Registration complete, insert user into database
    try:
        register_user(
            telegram_id=message.from_user.id,
            username=user_state[message.chat.id]['username'],
            password=user_state[message.chat.id]['password'],  # Hash this password before storing
            special_question=user_state[message.chat.id]['special_question'],
            special_question_answer=special_question_answer
        )
        bot.send_message(message.chat.id, "Registration successful! You can now use /login to sign in.")
    except Exception as e:
        bot.send_message(message.chat.id, f"An error occurred: {e}")

    # Clear the user state after registration
    del user_state[message.chat.id]


# Login step 1: username
def process_login_username_step(message):
    username = message.text.strip()
    user_state[message.chat.id] = {'username': username}
    msg = bot.send_message(message.chat.id, "Please enter your password:")
    bot.register_next_step_handler(msg, process_login_password_step)

# Login step 2: password
def process_login_password_step(message):
    username = user_state[message.chat.id]['username']
    password = message.text.strip()
    telegram_id = check_user_login(username, password)
    if telegram_id:
        bot.send_message(message.chat.id, "Login successful!")
    else:
        bot.send_message(message.chat.id, "Login failed. Please check your username and password and try again.")
# Polling
bot.polling(none_stop=True)
