import telebot
import json
import random
import mysql.connector
from telebot import types
import os


TOKEN = '6927864805:AAHUXDLgt649w-fQT2jqkS1ykNjkAZIUA7M'
bot = telebot.TeleBot(TOKEN)

db_config = {
    'host': "localhost",
    'user': "root",
    'password': "root",
    'database': "cs_quiz"
}

user_data = {}

@bot.message_handler(commands=['start'])
def start(message):
    user_telegram_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name if message.from_user.last_name is not None else ''

    insert_user_record(user_telegram_id, username, first_name, last_name)

    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add('rus', 'uzkiril', 'uzlotin')
    msg = bot.send_message(message.chat.id, "Choose your language:", reply_markup=markup)
    bot.register_next_step_handler(msg, quiz_setup)

@bot.message_handler(commands=['global_records'])
def show_global_records(message):
    db = mysql.connector.connect(**db_config)
    cursor = db.cursor()

    query = """
    SELECT username, MAX(score) AS top_score
    FROM Quizzes
    JOIN Users ON Quizzes.user_id = Users.user_id
    GROUP BY Users.user_id
    ORDER BY top_score DESC
    LIMIT 10
    """
    cursor.execute(query)
    records = cursor.fetchall()

    records_message = "Top Scores:\n"
    for index, record in enumerate(records, start=1):
        username = record[0] or "Anonymous"
        top_score = record[1]
        records_message += f"{index}. {username}: {top_score}\n"

    bot.send_message(message.chat.id, records_message)
    cursor.close()
    db.close()


@bot.message_handler(commands=['my_records'])
def show_my_records(message):
    telegram_id = message.from_user.id
    db = mysql.connector.connect(**db_config)
    cursor = db.cursor()

    cursor.execute("""
    SELECT score, correct_answers, incorrect_answers, timestamp
    FROM Quizzes
    JOIN Users ON Quizzes.user_id = Users.user_id
    WHERE Users.telegram_id = %s
    ORDER BY timestamp DESC
    """, (telegram_id,))

    quizzes = cursor.fetchall()
    if quizzes:
        records_message = "📜 Your Quiz Records:\n\n"
        for quiz in quizzes:
            score, correct, incorrect, timestamp = quiz
            date_str = timestamp.strftime("%Y-%m-%d %H:%M")
            records_message += (f"🗓 Date: {date_str}\n"
                                f"✅ Correct: {correct}\n"
                                f"❌ Incorrect: {incorrect}\n"
                                f"🔢 Score: {score}\n\n")
    else:
        records_message = "You do not have any quiz records yet. 🤷‍♂️"

    bot.send_message(message.chat.id, records_message)
    cursor.close()
    db.close()


def quiz_setup(message):
    lang = message.text
    user_data[message.chat.id] = {'language': lang, 'score': 0, 'correct': 0, 'incorrect': 0}
    bot.send_message(message.chat.id, "How many questions do you want in the quiz?")
    bot.register_next_step_handler(message, start_quiz)


def start_quiz(message):
    try:
        count = int(message.text)
        user_data[message.chat.id]['questions'] = load_questions(user_data[message.chat.id]['language'], count)
        ask_question(message.chat.id)
    except ValueError:
        bot.send_message(message.chat.id, "Please enter a valid number.")


def ask_question(chat_id):
    if not user_data[chat_id]['questions']:
        finish_quiz(chat_id)
        return

    question = user_data[chat_id]['questions'].pop()
    user_data[chat_id]['current_question'] = question

    # Sending question image if exists
    if question.get('media', {}).get('exist', False):
        image_name = question['media']['name']
        photo_path = os.path.join('Autotest', f'{image_name}.png')
        with open(photo_path, 'rb') as photo:
            bot.send_photo(chat_id, photo)

    # Sending question text and choices
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    choices = question['choices']
    random.shuffle(choices)
    for choice in choices:
        markup.add(choice['text'])
    markup.add('Skip')
    bot.send_message(chat_id, question['question'], reply_markup=markup)
    bot.register_next_step_handler_by_chat_id(chat_id, handle_answer)



def handle_answer(message):
    chat_id = message.chat.id
    current_question = user_data[chat_id]['current_question']
    correct_answer = next((choice for choice in current_question['choices'] if choice['answer']), None)

    if correct_answer and message.text == correct_answer['text']:
        user_data[chat_id]['score'] += 1
        user_data[chat_id]['correct'] += 1
    elif message.text == "Skip":
        # No score change for skip
        pass
    else:
        user_data[chat_id]['score'] -= 0.25
        user_data[chat_id]['incorrect'] += 1

    ask_question(chat_id)


def finish_quiz(chat_id):
    user = user_data[chat_id]
    summary = f"Quiz finished!\nScore: {user['score']}\nCorrect answers: {user['correct']}\nIncorrect answers: {user['incorrect']} \n\n /my_records - to show your records \n\n /global_records - all records"
    bot.send_message(chat_id, summary)

    insert_quiz_summary(chat_id, user['score'], user['correct'], user['incorrect'])

    del user_data[chat_id]


def load_questions(language, count):
    filename = f'{language}.json'
    with open(os.path.join('Autotest', filename), 'r', encoding='utf-8') as file:
        questions = json.load(file)
    return random.sample(questions, count)


def insert_user_record(telegram_id, username, first_name, last_name):
    db = mysql.connector.connect(**db_config)
    cursor = db.cursor()

    try:
        db.start_transaction()
        cursor.execute("SELECT user_id FROM Users WHERE telegram_id = %s", (telegram_id,))
        result = cursor.fetchone()

        if result:
            cursor.execute("UPDATE Users SET username=%s, first_name=%s, last_name=%s WHERE telegram_id=%s",
                           (username, first_name, last_name, telegram_id))
        else:
            cursor.execute("INSERT INTO Users (telegram_id, username, first_name, last_name) VALUES (%s, %s, %s, %s)",
                           (telegram_id, username, first_name, last_name))
        db.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        db.rollback()
    finally:
        cursor.close()
        db.close()


def insert_quiz_summary(telegram_id, score, correct_answers, incorrect_answers):
    db = mysql.connector.connect(**db_config)
    cursor = db.cursor()

    try:
        db.start_transaction()
        cursor.execute("SELECT user_id FROM Users WHERE telegram_id = %s", (telegram_id,))
        result = cursor.fetchone()

        if result:
            user_id = result[0]
            cursor.execute(
                "INSERT INTO Quizzes (user_id, score, correct_answers, incorrect_answers) VALUES (%s, %s, %s, %s)",
                (user_id, score, correct_answers, incorrect_answers))
            db.commit()
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        db.rollback()
    finally:
        cursor.close()
        db.close()


if __name__ == '__main__':
    bot.polling(none_stop=True)

