from database import execute_query

def show_products(chat_id, bot):
    products = execute_query("SELECT product_id, name, price FROM products")
    for product in products:
        bot.send_message(chat_id, f"ID: {product[0]}, Name: {product[1]}, Price: {product[2]}")

def add_to_cart(telegram_id, product_id, quantity):
    product = execute_query("SELECT name, price FROM products WHERE product_id = %s", (product_id,))
    if not product:
        return "Product not found."

    execute_query(
        "INSERT INTO cart (telegram_id, product_id, quantity) VALUES (%s, %s, %s) "
        "ON DUPLICATE KEY UPDATE quantity = quantity + %s",
        (telegram_id, product_id, quantity, quantity),
        commit=True
    )
    return f"Added {product[0][0]} to your cart."

def get_cart_contents(telegram_id):
    return execute_query(
        "SELECT p.name, c.quantity, p.price FROM cart c "
        "JOIN products p ON c.product_id = p.product_id WHERE c.telegram_id = %s",
        (telegram_id,)
    )

def remove_from_cart(telegram_id, product_id):
    execute_query("DELETE FROM cart WHERE telegram_id = %s AND product_id = %s", (telegram_id, product_id), commit=True)
    return "Removed item from cart."
