import telebot
from telebot import types
from config import TELEGRAM_TOKEN
import auth
import cart

bot = telebot.TeleBot(TELEGRAM_TOKEN)
user_state = {}

@bot.message_handler(commands=['start'])
def command_start(message):
    if auth.is_user_registered(message.from_user.id):
        bot.send_message(message.chat.id, "Welcome back! You can use the following commands:\n"
                                          "/products - Show all products\n"
                                          "/addtocart - Add a product to your cart\n"
                                          "/showcart - Show your cart\n"
                                          "/removefromcart - Remove a product from your cart")
    else:
        markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        markup.add('Register', 'Login')
        bot.send_message(message.chat.id, "Welcome to our shop! Please register or login.", reply_markup=markup)

@bot.message_handler(commands=['products'])
def command_show_products(message):
    cart.show_products(message.chat.id, bot)

@bot.message_handler(commands=['addtocart'])
def command_add_to_cart(message):
    msg = bot.reply_to(message, "Enter the product ID you wish to add to your cart:")
    bot.register_next_step_handler(msg, process_add_to_cart_step)

def process_add_to_cart_step(message):
    try:
        product_id = int(message.text.strip())
        result = cart.add_to_cart(message.from_user.id, product_id, 1)
        bot.send_message(message.chat.id, result)
    except ValueError:
        bot.reply_to(message, "Please enter a valid product ID.")

@bot.message_handler(commands=['showcart'])
def command_show_cart(message):
    cart_contents = cart.get_cart_contents(message.from_user.id)
    if not cart_contents:
        bot.send_message(message.chat.id, "Your cart is empty.")
    else:
        response = "\n".join([f"{name} - Quantity: {quantity} - Price: {price}" for name, quantity, price in cart_contents])
        bot.send_message(message.chat.id, response)

@bot.message_handler(commands=['removefromcart'])
def command_remove_from_cart(message):
    msg = bot.reply_to(message, "Enter the product ID you wish to remove from your cart:")
    bot.register_next_step_handler(msg, process_remove_from_cart_step)

def process_remove_from_cart_step(message):
    try:
        product_id = int(message.text.strip())
        result = cart.remove_from_cart(message.from_user.id, product_id)
        bot.send_message(message.chat.id, result)
    except ValueError:
        bot.reply_to(message, "Please enter a valid product ID.")

# Here you will need to add the rest of the bot handlers, particularly for user authentication.
# For example:
bot.message_handler(func=lambda message: message.text == 'Register')
bot.message_handler(func=lambda message: message.text == 'Login')
# And any other handlers you need for your bot's functionality.

if __name__ == '__main__':
    bot.polling(none_stop=True)
