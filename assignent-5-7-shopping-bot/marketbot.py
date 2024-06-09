from itertools import product

import telebot
from telebot import types
from main import *

bot = telebot.TeleBot('6741489602:AAGTMECus2iIQ4_Q-2T9gPwdMrgZjr2chtU')
user_info = {
    "name":False,
    "password":False
}
product = {
    "ID": False,
    "Name": False,
    "Price": False,
    "Amount": False,
    "Total": False
}
# Admin User IDs
ADMIN_USER_IDS = [1311488399, 987654321]
logged_in_admins = set()  # This will store the Telegram IDs of users who successfully log in as admins


def is_admin(user_id):
    """Check if the user is an admin."""
    return user_id in ADMIN_USER_IDS

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    register_button = types.InlineKeyboardButton('Register', callback_data='register')
    login_button = types.InlineKeyboardButton('Login', callback_data='login')
    admin_login_button = types.InlineKeyboardButton('Login as Admin', callback_data='admin_login')  # Admin login button

    markup.add(register_button, login_button, admin_login_button)

    # Check if the user is an admin
    # if message.from_user.id in ADMIN_USER_IDS:
    #     # Admin-specific buttons
    #     admin_command_button = types.InlineKeyboardButton('Admin Commands', callback_data='admin_commands')
    #
    #     markup.row(admin_command_button)

    bot.send_message(message.chat.id, "Choose your option", reply_markup=markup)

# -----------------------admin:
# Command handler to initiate add product process

@bot.message_handler(commands=['add_product'])
def add_product(message):
    """Handle the /add_product command."""
    if message.from_user.id not in logged_in_admins:
        bot.reply_to(message, "You are not logged in as an admin.")
        return

    msg = bot.reply_to(message, "Enter product details in the format: Name, Price, Quantity")
    bot.register_next_step_handler(msg, process_add_product)


def process_add_product(message):
    """Process adding a product."""
    try:
        chat_id = message.chat.id
        product_details = message.text.split(',')

        if len(product_details) != 3:
            bot.send_message(chat_id, "Please enter the product details in the format: Name, Price, Quantity.")
            return

        name, price, quantity = product_details
        is_valid, validation_msg = validate_product_details(name.strip(), price.strip(), quantity.strip())
        if not is_valid:
            bot.send_message(chat_id, validation_msg)
            return
        add_product_to_db(name.strip(), float(price.strip()), int(quantity.strip()))


        bot.send_message(chat_id, "Product added successfully! \n /products - to show products ")
    except Exception as e:
        bot.reply_to(message, 'Failed to add the product.')


@bot.message_handler(commands=['delete_product'])
def delete_product(message):
    """Handle the /delete_product command."""
    if message.from_user.id not in logged_in_admins:
        bot.reply_to(message, "You are not logged in as an admin.")
        return

    msg = bot.reply_to(message, "Enter the product ID to delete")
    bot.register_next_step_handler(msg, process_delete_product)


def process_delete_product(message):
    """Process deleting a product."""
    try:
        chat_id = message.chat.id
        product_id = int(message.text.strip())
        products = get_products_data()
        for i in products:
            if product_id == i[0]:
                delete_product_from_db(product_id)
                bot.send_message(chat_id, "Product deleted successfully!")
                return
        bot.send_message(chat_id, "The Wrong product ID. \n Please try again: \n /delete_product")

    except Exception as e:
        bot.reply_to(message, 'Failed to delete the product.')

# Define a mapping from commands to database column names
command_to_column = {
    '/edit_product_name': 'name',
    '/edit_product_price': 'price',
    '/edit_product_quantity': 'quantity'
}

@bot.message_handler(commands=['edit_product_name'])
def edit_product_name_handler(message):
    process_edit_request(message, 'name')

@bot.message_handler(commands=['edit_product_price'])
def edit_product_price_handler(message):
    process_edit_request(message, 'price')

@bot.message_handler(commands=['edit_product_quantity'])
def edit_product_quantity_handler(message):
    process_edit_request(message, 'quantity')

def process_edit_request(message, column):
    if message.from_user.id not in logged_in_admins:
        bot.reply_to(message, "You are not logged in as an admin.")
        return

    attribute = column.capitalize()
    msg = bot.reply_to(message, f"Please enter the product ID and {attribute} in this format: Id, {attribute}")
    bot.register_next_step_handler(msg, lambda msg: process_edit_product(msg, column))

def process_edit_product(message, column):
    chat_id = message.chat.id

    try:
        product_details = message.text.split(',')
        if len(product_details) != 2:
            bot.send_message(chat_id, f"Please enter the product ID and {column.capitalize()} in the correct format.")
            return

        product_id, value = [detail.strip() for detail in product_details]
        product_id = int(product_id)

        # For price and quantity, ensure conversion to the correct type
        if column in ['price', 'quantity']:
            value = float(value) if column == 'price' else int(value)

        if update_product(product_id, column, value):
            bot.send_message(chat_id, f"Product {column} updated successfully!")
        else:
            bot.send_message(chat_id, "No product found with the given ID. Please try again.")

    except ValueError:
        bot.send_message(chat_id, f"Invalid value. Please ensure the product ID is numeric and the {column} is in the correct format.")
    except Exception as e:
        bot.reply_to(message, f'Failed to update the product {column}. Error: {e}')

@bot.message_handler(commands=['total_products_sold'])
def show_total_products_sold(message):
    if message.from_user.id not in logged_in_admins:
        bot.reply_to(message, "You are not logged in as an admin.")
        return

    total_sold = total_products_sold()
    if total_sold is not None:
        bot.reply_to(message, f"The total number of products sold is: {total_sold}")
    else:
        bot.reply_to(message, "There was an error fetching the total number of products sold.")

@bot.message_handler(commands=['product_sales'])
def ask_product_id(message):
    if message.from_user.id not in logged_in_admins:
        bot.reply_to(message, "You are not logged in as an admin.")
        return

    msg = bot.reply_to(message, "Please enter the product ID to see total sales:")
    bot.register_next_step_handler(msg, show_product_sales)

def show_product_sales(message):
    try:
        product_id = int(message.text.strip())
        total_sold = get_product_sales(product_id)

        if total_sold is not None:
            bot.reply_to(message, f"Total sales for product {product_id}: {total_sold}")
        else:
            bot.reply_to(message, "There was an error fetching the sales data.")

    except ValueError:
        bot.reply_to(message, "Invalid product ID. Please enter a numeric ID.")
    except Exception as e:
        bot.reply_to(message, f"Failed to retrieve sales data. Error: {e}")


# ---------------------------

@bot.message_handler(commands=['products'])
def products(message):
    products = get_products_data()
    for product in products:
        pr_info = (f"ID: {product[0]}"
                   f"\nProduct Name: {product[1]}"
                   f"\nPrice: {product[2]}"
                   f"\nQuantity: {product[3]}")
        bot.send_message(message.chat.id, f"{pr_info}")
    bot.send_message(message.chat.id, "Enter product ID to add to cart!")
    bot.register_next_step_handler(message, choose_product)

def choose_product(message):
    pr_id = message.text
    pr_data = get_products_data()
    for i in pr_data:
        if i[0] == int(pr_id):
            product["ID"] = i[0]
            product["Name"] = i[1]
            product["Price"] = i[2]
            bot.send_message(message.chat.id ,"enter amount")
            bot.register_next_step_handler(message, product_amount)

def product_amount(message):
    markup = types.InlineKeyboardMarkup()
    yes_button = types.InlineKeyboardButton('Yes', callback_data='yes')
    no_button = types.InlineKeyboardButton('No', callback_data='no')
    markup.add(yes_button, no_button)

    try:
        amount_requested = int(message.text)
    except ValueError:
        bot.send_message(message.chat.id, "Please enter a valid number for the amount.")
        bot.register_next_step_handler(message, product_amount)  # Ask for the amount again
        return

    pr_data = get_products_data()
    for product_details in pr_data:
        if product_details[0] == product["ID"]:
            available_quantity = product_details[3]  # Assuming the 4th element is quantity

            if amount_requested > available_quantity:
                bot.send_message(message.chat.id, f"You have exceeded the available amount. There are only {available_quantity} units available. Please enter a new amount:")
                bot.register_next_step_handler(message, product_amount)  # Ask for the amount again
                return  # Exit this iteration and wait for the new amount

            product["Amount"] = amount_requested
            total = float(product_details[2]) * amount_requested  # Assuming the 3rd element is price
            product["Total"] = round(total, 1)

            add_product_to_cart(product["ID"], product["Name"], product["Price"], product["Amount"], product["Total"])
            bot.send_message(message.chat.id, "Do you want to buy anything else?", reply_markup=markup)
            return

    bot.send_message(message.chat.id, "The product was not found.")



def handle_name(message):
    username=message.text
    user_info['name'] = username
    bot.send_message(message.chat.id, f"{username.capitalize()}, Enter Your password")
    bot.register_next_step_handler(message, handle_password)

def handle_password(message):
    password=message.text
    user_info['password'] = password
    add_user(user_info["name"], user_info["password"])
    bot.send_message(message.chat.id, "Registration successful! \n\n" "/products - to show products")

def check_name(message):
    username=message.text
    user_data=get_users_data()
    for i in user_data:
        if i[1].lower() == username.lower():
            bot.send_message(message.chat.id, f"{username.capitalize()}, enter your password")
            bot.register_next_step_handler(message, check_password)
            return
    bot.reply_to(message, "This data is not found")

def check_password(message):
    password=message.text
    user_data=get_users_data()
    for i in user_data:
        if i[2]==password:
            bot.send_message(message.chat.id, "You logged in successfully. \n " "/products - to show products")
            bot.register_next_step_handler(message, products)
            return
    bot.reply_to(message, "Your password is incorrect!")

@bot.message_handler(commands=['cart'])
def cart(message):
    markup = types.InlineKeyboardMarkup()
    buy_button = types.InlineKeyboardButton('Buy products', callback_data='buy')
    # delete_button = types.InlineKeyboardButton('Delete products', callback_data='delete')
    quit_button = types.InlineKeyboardButton('Quit', callback_data='quit')

    markup.row(buy_button)
    # markup.row(delete_button)
    markup.row(quit_button)

    cart_data=get_carts_data()
    cart_info=""
    total_sum=0
    if cart_data:
        for i in cart_data:
            cart_info+=f"Product: {i[1]} \n Quantity: {i[2]} \n Price: {i[3]} \n Total: {i[4]}\n\n"
            total_sum+=float(i[5])
        bot.send_message(message.chat.id, f"{cart_info} Total sum of all products: ${total_sum}", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Your cart is empty")

def delete_product(message):
    user_choice = message.text
    cart_data = get_carts_data()
    for i in cart_data:
        if i[0]==int(user_choice):
            delete_cart_item(int(user_choice))
    bot.send_message(message.chat.id, "Product is deleted\n\n /cart - to show cart")

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == 'register':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Enter Your username')
        bot.register_next_step_handler(call.message, handle_name)
    elif call.data == 'login':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Enter your username: ')
        bot.register_next_step_handler(call.message, check_name)
    elif call.data == 'buy':
        product_data = get_products_data()
        cart_data = get_carts_data()

        for cart_item in cart_data:
            product_id, quantity_sold = cart_item[1], cart_item[4]

            # Deduct the quantity from the product inventory
            deduct_quantity(product_id, quantity_sold)

            # Record the sale in the sales table
            record_sale(product_id, quantity_sold)

        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Thank you for your purchase! ')
        clear_cart_data()

    elif call.data == 'delete':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Enter product ID to delete')
        bot.register_next_step_handler(call.message, delete_product)
    elif call.data == "quit":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Goodbye!')
        clear_cart_data()
    elif call.data == 'yes':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Enter Product Id: ")
        bot.register_next_step_handler(call.message, choose_product)
    elif call.data == 'no':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="/cart - to show cart")
    elif call.data == 'admin_commands':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="/add_product - to add product \n "
                                                                                                     "/delete_product - to delete product \n "
                                                                                                     "/edit_product_name - to edit product name \n "
                                                                                                     "/edit_product_price - to edit product price \n "
                                                                                                     "/edit_product_quantity - to edit product quantity \n "
                                                                                                     "/total_products_sold - to show products sales info \n "
                                                                                                     "/product_sales - to show a product sale info \n ")
    elif call.data == 'admin_login':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text="Enter admin username:")
        bot.register_next_step_handler(call.message, admin_username_step)

def admin_username_step(message):
    if message.text == "admin":  # Check the username
        bot.send_message(message.chat.id, "Enter admin password:")
        bot.register_next_step_handler(message, admin_password_step)
    else:
        bot.send_message(message.chat.id, "Invalid admin username.")

def admin_password_step(message):
    if message.text == "12345" and is_admin(message.from_user.id):  # Check the password and if the user is an admin
        logged_in_admins.add(message.from_user.id)
        bot.send_message(message.chat.id, "Admin login successful. You can now use admin commands. \n\n"" /add_product - to add product \n "
                                                                                                     "/delete_product - to delete product \n "
                                                                                                     "/edit_product_name - to edit product name \n "
                                                                                                     "/edit_product_price - to edit product price \n "
                                                                                                     "/edit_product_quantity - to edit product quantity \n "
                                                                                                     "/total_products_sold - to show products sales info \n "
                                                                                                     "/product_sales - to show a product sale info \n ")
    else:
        bot.send_message(message.chat.id, "Invalid admin password or you are not authorized.")

if __name__ == '__main__':
    bot.polling(none_stop=True)

