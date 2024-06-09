import mysql.connector
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="root",
  database="cs_shopping_bot"
)

mycursor = mydb.cursor()

mycursor.execute("SELECT * FROM customers")

myresult = mycursor.fetchall()

def get_users_data():
  mycursor.execute("SELECT * FROM customers")
  return mycursor.fetchall()


def get_products_data():
  with mydb.cursor() as cursor:
    cursor.execute("SELECT * FROM products")
    return cursor.fetchall()


def get_carts_data():
  mycursor.execute("SELECT * FROM carts")
  return mycursor.fetchall()

def add_user(name, password):
  sql = "INSERT INTO customers (username, password) VALUES (%s, %s)"
  val = (name, password)
  mycursor.execute(sql, val)
  mydb.commit()

def add_product_to_cart(product_id, products, price, amount, total):
  sql = "INSERT INTO carts (product_id, products, price, amount, total) VALUES (%s, %s, %s, %s, %s)"
  val = (product_id, products, price, amount, total)
  mycursor.execute(sql, val)
  mydb.commit()

def delete_cart_item(id):
  sql = f"DELETE FROM carts WHERE id = {id}"
  mycursor.execute(sql)
  mydb.commit()

def clear_cart_data():
  sql = "Truncate table carts"
  mycursor.execute(sql)
  mydb.commit()
  mycursor.close()
  mydb.close()


def deduct_quantity(product_id, amount):
  try:
    # First, fetch the current quantity of the product
    sql_get = "SELECT quantity FROM products WHERE id = %s"
    mycursor.execute(sql_get, (product_id,))
    result = mycursor.fetchone()

    if result:
      current_quantity = result[0]

      # Calculate the new quantity after deduction
      new_quantity = current_quantity - amount
      if new_quantity < 0:
        print(f"Cannot deduct {amount} from product {product_id}: Not enough stock.")
        return False

      # Update the product's quantity in the database
      sql_update = "UPDATE products SET quantity = %s WHERE id = %s"
      mycursor.execute(sql_update, (new_quantity, product_id))
      mydb.commit()

      print(f"Quantity for product {product_id} deducted by {amount}. New quantity: {new_quantity}")
      return True
    else:
      print(f"Product with ID {product_id} not found.")
      return False

  except mysql.connector.Error as err:
    print(f"Error deducting quantity for product {product_id}: {err}")
    mydb.rollback()
    return False


def record_sale(product_id, quantity_sold):
  """Records a sale in the sales table."""
  try:

    sql = "INSERT INTO sales (product_id, quantity) VALUES (%s, %s)"
    val = (product_id, quantity_sold)
    mycursor.execute(sql, val)
    mydb.commit()

    print(f"Sale recorded: Product ID {product_id}, Quantity {quantity_sold}")

  except mysql.connector.Error as err:
    print(f"Error recording sale for product {product_id}: {err}")
    mydb.rollback()

def validate_product_details(name, price, quantity):
  """Validate product details."""
  if not name or type(name) is not str:
    return False, "Invalid product name."
  try:
    price = float(price)
    if price <= 0:
      return False, "Price must be a positive number."
  except ValueError:
    return False, "Invalid price format."

  try:
    quantity = int(quantity)
    if quantity < 0:
      return False, "Quantity cannot be negative."
  except ValueError:
    return False, "Invalid quantity format."

  return True, ""

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

    cursor.execute("INSERT INTO products (name, price, quantity) VALUES (%s, %s, %s)",
                   (name.strip(), float(price.strip()), int(quantity.strip())))
    db.commit()

    bot.send_message(chat_id, "Product added successfully!")
  except Exception as e:
    bot.reply_to(message, 'Failed to add the product.')


def add_product_to_db(name, price, quantity):
  """Add a new product to the database."""
  try:
    # Prepare SQL query to insert a new product
    sql = "INSERT INTO products (name, price, quantity) VALUES (%s, %s, %s)"
    val = (name, price, quantity)

    # Execute the SQL command
    mycursor.execute(sql, val)

    # Commit the changes to the database
    mydb.commit()

    print(mycursor.rowcount, "record inserted.")  # Optional: Print how many rows were inserted
  except mysql.connector.Error as err:
    print("Failed to insert record into MySQL table: {}".format(err))
    # Optionally, you can rollback the changes if an error occurs
    mydb.rollback()

def delete_product_from_db(product_id):
  """Delete a product from the database by its ID."""
  try:
    # Prepare SQL query to delete a product by its ID
    sql = "DELETE FROM products WHERE id = %s"
    val = (product_id,)

    # Execute the SQL command
    mycursor.execute(sql, val)

    # Commit the changes to the database
    mydb.commit()

    print(mycursor.rowcount, "record(s) deleted")  # Optional: Print how many rows were deleted
  except mysql.connector.Error as err:
    print("Failed to delete record from MySQL table: {}".format(err))
    # Optionally, you can rollback the changes if an error occurs
    mydb.rollback()


def update_product(product_id, column, value):
  """Update a product in the database by its ID.

  Args:
      product_id (int): The ID of the product to update.
      column (str): The name of the column to update ('name', 'price', or 'quantity').
      value (str/int/float): The new value for the column. The type depends on the column being updated.
  """
  # Check if the column name is valid to prevent SQL injection
  if column not in ['name', 'price', 'quantity']:
    print("Invalid column name.")
    return False

  try:
    # Using a parameterized query to ensure safety against SQL injection
    sql = f"UPDATE products SET {column} = %s WHERE id = %s"
    val = (value, product_id)
    mycursor.execute(sql, val)
    mydb.commit()

    if mycursor.rowcount > 0:
      print(f"{mycursor.rowcount} record(s) updated")
      return True
    else:
      print("No record updated. Please check the product ID.")
      return False

  except mysql.connector.Error as err:
    print(f"Failed to update record: {err}")
    mydb.rollback()
    return False

def total_products_sold():
  """Returns the total number of products sold."""
  try:
    # Query to calculate the sum of all quantities sold from the sales table
    sql = "SELECT SUM(quantity) FROM sales"
    mycursor.execute(sql)
    result = mycursor.fetchone()  # Fetch the result of the query

    total_sold = result[0] if result[0] is not None else 0  # Check if the result is not None
    print(f"Total products sold: {total_sold}")
    return total_sold

  except mysql.connector.Error as err:
    print(f"Error fetching total products sold: {err}")
    return None

def get_product_sales(product_id):
  """Returns the total quantity sold for a specific product."""
  try:
    sql = "SELECT SUM(quantity) FROM sales WHERE product_id = %s"
    mycursor.execute(sql, (product_id,))
    result = mycursor.fetchone()

    total_sold = result[0] if result[0] is not None else 0
    print(f"Total sold for product {product_id}: {total_sold}")
    return total_sold

  except mysql.connector.Error as err:
    print(f"Error fetching sales for product {product_id}: {err}")
    return None