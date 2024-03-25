from database import execute_query
import bcrypt

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def register_user(telegram_id, username, password, special_question, special_question_answer):
    hashed_password = hash_password(password).decode('utf-8')
    execute_query("INSERT INTO users (telegram_id, username, password, special_question, special_question_answer) "
                  "VALUES (%s, %s, %s, %s, %s)",
                  (telegram_id, username, hashed_password, special_question, special_question_answer),
                  commit=True)

def is_user_registered(telegram_id):
    result = execute_query("SELECT COUNT(1) FROM users WHERE telegram_id = %s", (telegram_id,))
    return result and result[0][0] > 0

def check_user_login(username, password):
    user = execute_query("SELECT password FROM users WHERE username = %s", (username,))
    if user and bcrypt.checkpw(password.encode('utf-8'), user[0][0].encode('utf-8')):
        return True
    return False
