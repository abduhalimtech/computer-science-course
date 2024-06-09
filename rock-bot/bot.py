import telebot
from telebot import types
import random
import threading
import mysql.connector
from mysql.connector import Error

API_TOKEN = '7157356565:AAESsm7iMul-b14o8DhwIBYmsM1HuWqTzag'  # Replace with your actual API token
bot = telebot.TeleBot(API_TOKEN)

# Database setup and connection
def create_connection():
    """Create and return a database connection."""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='cs_rockbot',
            user='root',
            password='root'  # Ensure your password is secure and not exposed
        )
        if connection.is_connected():
            print("Connected to the database")
        return connection
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return None

def create_table(connection):
    """Ensure the game results table exists."""
    try:
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS game_results (
                game_no INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255),
                winner VARCHAR(255),
                user_score INT,
                opponent_score INT,
                tie BOOLEAN,
                game_time_seconds INT
            )
        """)
        connection.commit()
        cursor.close()
    except Error as e:
        print(f"Error creating table: {e}")

connection = create_connection()
create_table(connection)

# Game choices and user state
choices = {"Rock": "🪨", "Paper": "📄", "Scissors": "✂️"}
user_game_states = {}
user_queue = []

# Utility functions
def start_timer(user_id, chat_id):
    """Start a timer for the user to make a move."""
    timer = threading.Timer(15.0, timeout, args=(user_id, chat_id))
    timer.start()
    user_game_states[user_id]['timer'] = timer

def timeout(user_id, chat_id):
    """Handle user timeout by ending the round as a loss."""
    if user_id in user_game_states:
        bot.send_message(chat_id, "⏰ Time's up! You didn't respond in time. You lose this round!")
        handle_round_end(user_id, chat_id, 'timeout')

@bot.message_handler(commands=['start'])
def send_welcome(message):
    """Send a welcome message with game options."""
    welcome_text = ("<b>Welcome to Rock, Paper, Scissors!</b>\n\n"
                    "Press 'User vs AI' to play against the AI or 'User vs User' to play against another user.")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add('User vs AI 🤖', 'User vs User 👥', 'Show Records 📊', 'Show Analytics 📈')
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup, parse_mode='HTML')

def send_options(chat_id, user_id):
    """Send game options (Rock, Paper, Scissors) to the user."""
    markup = types.InlineKeyboardMarkup()
    buttons = [types.InlineKeyboardButton(text=f"{emoji} {choice}", callback_data=choice) for choice, emoji in choices.items()]
    markup.add(*buttons)
    bot.send_message(chat_id, "<b>Choose Rock, Paper, or Scissors:</b>", reply_markup=markup, parse_mode='HTML')
    start_timer(user_id, chat_id)

# Game handlers
@bot.message_handler(func=lambda message: message.text in ['User vs AI 🤖', 'User vs User 👥'])
def handle_game_start(message):
    """Handle game start for both AI and user vs user modes."""
    user_id = message.from_user.id
    chat_id = message.chat.id
    if message.text == 'User vs AI 🤖':
        user_game_states[user_id] = {'opponent': 'ai', 'user_score': 0, 'opponent_score': 0, 'round': 1, 'timer': None}
        send_options(chat_id, user_id)
    elif message.text == 'User vs User 👥':
        if user_id not in user_queue:
            user_queue.append(user_id)
            user_game_states[user_id] = {'opponent': None, 'user_score': 0, 'opponent_score': 0, 'round': 1, 'timer': None}
            bot.send_message(chat_id, "👥 You've joined the queue! Waiting for an opponent...", parse_mode='HTML')
            match_users_for_game()
        else:
            bot.send_message(chat_id, "👥 You're already in the queue or in a game! Please wait...", parse_mode='HTML')

def match_users_for_game():
    """Match two users from the queue to start a game."""
    if len(user_queue) < 2:
        return
    user_id1 = user_queue.pop(0)
    user_id2 = user_queue.pop(0)
    user_game_states[user_id1]['opponent'] = user_id2
    user_game_states[user_id2]['opponent'] = user_id1
    send_options(user_id1, user_id2)  # Sending options to both users
    send_options(user_id2, user_id1)

@bot.callback_query_handler(func=lambda call: call.data in choices)
def query_handler(call):
    """Handle the user's choice from inline buttons."""
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    user_move = call.data
    if user_id in user_game_states:
        user_game_states[user_id]['move_selected'] = True
        opponent_id = user_game_states[user_id]['opponent']
        if opponent_id == 'ai':
            handle_ai_move(user_id, chat_id, user_move)
        else:
            handle_user_move(user_id, chat_id, user_move, opponent_id)

def handle_ai_move(user_id, chat_id, user_move):
    """Handle the AI move and determine the result."""
    opponent_move = random.choice(list(choices.keys()))
    result = determine_winner(user_move, opponent_move)
    update_scores_and_respond(user_id, chat_id, user_move, opponent_move, result)

def handle_user_move(user_id, chat_id, user_move, opponent_id):
    """Handle the user move in user vs user mode."""
    user_game_states[user_id]['user'] = user_move
    if 'user' in user_game_states[opponent_id]:
        opponent_move = user_game_states[opponent_id]['user']
        result = determine_winner(user_move, opponent_move)
        update_scores_and_respond(user_id, chat_id, user_move, opponent_move, result)
        update_scores_and_respond(opponent_id, chat_id, opponent_move, user_move, 'opponent' if result == 'user' else 'user')
    else:
        bot.send_message(chat_id, "Move recorded. Waiting for the opponent...", parse_mode='HTML')

def determine_winner(user_move, opponent_move):
    """Determine the winner based on moves."""
    if user_move == opponent_move:
        return 'tie'
    elif (user_move == "Rock" and opponent_move == "Scissors") or \
         (user_move == "Paper" and opponent_move == "Rock") or \
         (user_move == "Scissors" and opponent_move == "Paper"):
        return 'user'
    else:
        return 'opponent'

def update_scores_and_respond(user_id, chat_id, user_move, opponent_move, result):
    """Update scores, send result messages, and handle round end."""
    user_score = user_game_states[user_id]['user_score']
    opponent_score = user_game_states[user_id]['opponent_score']
    message = f"Your choice: {choices[user_move]} vs Opponent's choice: {choices[opponent_move]}\n"
    if result == 'user':
        user_game_states[user_id]['user_score'] += 1
        message += "You win this round!"
    elif result == 'opponent':
        user_game_states[user_id]['opponent_score'] += 1
        message += "You lose this round!"
    else:
        message += "It's a tie!"
    bot.send_message(chat_id, message, parse_mode='HTML')
    handle_round_end(user_id, chat_id)

def handle_round_end(user_id, chat_id):
    """Check game progress and handle end of the game."""
    if user_game_states[user_id]['round'] >= 5:  # Assuming 5 rounds per game
        end_game(user_id, chat_id)
    else:
        user_game_states[user_id]['round'] += 1
        send_options(chat_id, user_id)


def end_game(user_id, chat_id):
    """Handle the end of the game, report results, and clean up."""
    user_state = user_game_states.pop(user_id, None)
    if user_state:
        user_score = user_state['user_score']
        opponent_score = user_state['opponent_score']
        if user_score > opponent_score:
            result = "You win!"
        elif user_score < opponent_score:
            result = "You lose!"
        else:
            result = "It's a tie!"

        result_message = (f"Game Over! Final Score:\n"
                          f"User: {user_score} - Opponent: {opponent_score}\n"
                          f"{result}")

        bot.send_message(chat_id, result_message, parse_mode='HTML')

        if user_state['opponent'] != 'ai':  # Update both players if it's not an AI opponent
            opponent_id = user_state['opponent']
            opponent_chat_id = opponent_id  # Assuming chat ID is the same as user ID
            opponent_state = user_game_states.get(opponent_id)
            if opponent_state:
                bot.send_message(opponent_chat_id, result_message, parse_mode='HTML')
                user_game_states.pop(opponent_id, None)  # Clean up opponent's game state too


# Handlers for records and analytics
@bot.message_handler(func=lambda message: message.text == "Show Records 📊")
def handle_show_records(message):
    """Show game records from the database."""
    if connection.is_connected():
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM game_results ORDER BY game_no DESC LIMIT 10")  # Show last 10 records
        records = cursor.fetchall()
        records_text = "<b>Recent Game Records:</b>\n"
        for record in records:
            records_text += f"Game No: {record[0]}, Username: {record[1]}, Winner: {record[2]}, Scores: {record[3]}-{record[4]}, Tie: {record[5]}, Time: {record[6]}\n"
        bot.send_message(message.chat.id, records_text if records else "No records found.", parse_mode='HTML')
        cursor.close()

@bot.message_handler(func=lambda message: message.text == "Show Analytics 📈")
def handle_show_analytics(message):
    """Calculate and show analytics from the game results."""
    if connection.is_connected():
        cursor = connection.cursor()
        cursor.execute("SELECT COUNT(*) FROM game_results")
        total_games = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM game_results WHERE winner = username")
        games_won_by_users = cursor.fetchone()[0]
        analytics_text = (f"<b>Game Analytics:</b>\n"
                          f"Total Games Played: {total_games}\n"
                          f"Games Won by Users: {games_won_by_users}")
        bot.send_message(message.chat.id, analytics_text, parse_mode='HTML')
        cursor.close()

bot.infinity_polling()
