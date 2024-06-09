import telebot
from telebot import types
import random

API_TOKEN = '7157356565:AAESsm7iMul-b14o8DhwIBYmsM1HuWqTzag'
bot = telebot.TeleBot(API_TOKEN)

# Game choices
choices = {"Rock": "🪨", "Paper": "📄", "Scissors": "✂️"}

# User state and queue
user_game_states = {}
user_queue = []

# Utility functions
def start_timer(user_id, chat_id):
    """Start a timer for the user to make a move."""
    pass  # Timer implementation can be added here

def timeout(user_id, chat_id):
    """Handle user timeout by ending the round as a loss."""
    pass  # Timeout implementation can be added here

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

# Game handlers
@bot.message_handler(func=lambda message: message.text in ['User vs AI 🤖', 'User vs User 👥'])
def handle_game_start(message):
    """Handle game start for both AI and user vs user modes."""
    user_id = message.from_user.id
    chat_id = message.chat.id
    if message.text == 'User vs AI 🤖':
        user_game_states[user_id] = {'opponent': 'ai', 'user_score': 0, 'opponent_score': 0, 'round': 1, 'chat_id': chat_id}
        send_options(chat_id, user_id)
    elif message.text == 'User vs User 👥':
        if user_id not in user_queue:
            user_queue.append(user_id)
            user_game_states[user_id] = {'opponent': None, 'user_score': 0, 'opponent_score': 0, 'round': 1, 'chat_id': chat_id}
            bot.send_message(chat_id, "👥 You've joined the queue! Waiting for an opponent...", parse_mode='HTML')
            match_users_for_game()
        else:
            bot.send_message(chat_id, "👥 You're already in the queue or in a game! Please wait...", parse_mode='HTML')

def match_users_for_game():
    if len(user_queue) < 2:
        return
    user_id1 = user_queue.pop(0)
    user_id2 = user_queue.pop(0)
    if user_id1 in user_game_states and user_id2 in user_game_states:
        user_game_states[user_id1]['opponent'] = user_id2
        user_game_states[user_id2]['opponent'] = user_id1
        chat_id1 = user_game_states[user_id1]['chat_id']
        chat_id2 = user_game_states[user_id2]['chat_id']
        bot.send_message(chat_id1, f"🎮 You've been matched with {user_id2}! Get ready to play... 💥", parse_mode='HTML')
        bot.send_message(chat_id2, f"🎮 You've been matched with {user_id1}! Get ready to play... 💥", parse_mode='HTML')
        send_options(chat_id1, user_id1)
        send_options(chat_id2, user_id2)
    else:
        # Handle the case where one of the users is not in the user_game_states dictionary
        if user_id1 not in user_game_states:
            user_queue.append(user_id1)  # Put the user back into the queue
        if user_id2 not in user_game_states:
            user_queue.append(user_id2)  # Put the user back into the queue

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
    opponent_game_state = user_game_states[opponent_id]
    if 'user' in opponent_game_state:
        opponent_move = opponent_game_state['user']
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

        opponent_id = user_state['opponent']
        opponent_chat_id = opponent_id  # Assuming chat ID is the same as user ID
        opponent_state = user_game_states.get(opponent_id)
        if opponent_state:
            bot.send_message(opponent_chat_id, result_message, parse_mode='HTML')
            user_game_states.pop(opponent_id, None)  # Clean up opponent's game state too

bot.polling()
