import telebot
from telebot import types
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import os
import matplotlib.pyplot as plt

# non-interactive backend
plt.switch_backend('Agg')

# Environment variables for API tokens and spreadsheet ID
TELEGRAM_BOT_TOKEN = os.getenv('6244649557:AAEpEjiL3AGbAOWysrNUdW1BE4FprV3KcHg')
SAMPLE_SPREADSHEET_ID = os.getenv('1Ogcwmh2_1ahSh1Se5seGAe6j9s8_q-f37SWFMqkbjVw')
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

bot = telebot.TeleBot('6244649557:AAEpEjiL3AGbAOWysrNUdW1BE4FprV3KcHg')

def google_sheets_api_setup():
    """Set up the Google Sheets API client."""
    if os.path.exists('token.json'):
        credentials = Credentials.from_authorized_user_file('token.json', SCOPES)
    else:
        raise FileNotFoundError("Missing 'token.json'. Please follow the setup instructions.")
    return build('sheets', 'v4', credentials=credentials)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    markup.add('Search By Name', 'Search By Group')
    msg = bot.reply_to(message, "Choose an option:", reply_markup=markup)
    bot.register_next_step_handler(msg, process_option)

def process_option(message):
    if message.text == 'Search By Name':
        msg = bot.reply_to(message, "Enter a name:")
        bot.register_next_step_handler(msg, handle_name_search)
    elif message.text == 'Search By Group':
        display_groups(message)

def handle_name_search(message):
    name = message.text.strip().lower()
    service = google_sheets_api_setup()
    data = look_up_in_sheet(name, service)

    if data != "Name not found.":
        bot.reply_to(message, data)
        present, absent = look_up_and_count_attendance(name, service)
        filename = generate_pie_chart(present, absent)
        with open(filename, 'rb') as chart:
            bot.send_photo(message.chat.id, chart)
        os.remove(filename)
    else:
        bot.reply_to(message, "Name not found.")

def generate_pie_chart(present, absent, filename='attendance_pie_chart.png'):
    labels = 'Present', 'Absent'
    sizes = [present, absent]
    colors = ['blue', 'red']

    plt.figure()
    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', shadow=False, startangle=140)
    plt.axis('equal')
    plt.savefig(filename)
    plt.close()
    return filename

def look_up_and_count_attendance(name: str, service) -> tuple:
    result = service.spreadsheets().values().batchGet(
        spreadsheetId='1Ogcwmh2_1ahSh1Se5seGAe6j9s8_q-f37SWFMqkbjVw',
        ranges=['Copy of 201!A1:H28', 'Copy of 202!A1:H31', 'Copy of 203!A1:H29', 'Copy of 204!A1:I25',
                'Copy of 205!A1:I24']
    ).execute()

    total_present = 0
    total_absent = 0

    for valueRange in result.get('valueRanges', []):
        values = valueRange.get('values', [])

        for row in values:
            if row and row[0].strip().lower() == name:
                total_present += row[1:].count('1')
                total_absent += len([cell for cell in row[1:] if cell == '0' or cell == ''])

    return total_present, total_absent

def look_up_in_sheet(name: str, service) -> str:
    result = service.spreadsheets().values().batchGet(
        spreadsheetId='1Ogcwmh2_1ahSh1Se5seGAe6j9s8_q-f37SWFMqkbjVw',
        ranges=['Copy of 201!A1:H28', 'Copy of 202!A1:H31', 'Copy of 203!A1:H29', 'Copy of 204!A1:I25',
                'Copy of 205!A1:I24']
    ).execute()

    for valueRange in result.get('valueRanges', []):
        if 'values' in valueRange:
            for row in valueRange['values']:
                if row and row[0].strip().lower() == name:
                    return ' * '.join(row)
    return "Name not found."

def display_groups(message):
    # service = google_sheets_api_setup()
    groups = fetch_groups()
    markup = types.InlineKeyboardMarkup()
    for group in groups:
        markup.add(types.InlineKeyboardButton(group, callback_data=f"group_{group}"))
    bot.send_message(message.chat.id, "Select a group:", reply_markup=markup)

def fetch_groups():
    return ["201", "202", "203", "204", "205"]

@bot.callback_query_handler(func=lambda call: call.data.startswith('group_'))
def handle_group_selection(call):
    group_name = call.data.split('_')[1]
    display_students_in_group(call.message, group_name)

def display_students_in_group(message, group_name):
    service = google_sheets_api_setup()
    students = fetch_students_in_group(service, group_name)
    markup = types.InlineKeyboardMarkup()
    for student in students:
        markup.add(types.InlineKeyboardButton(student, callback_data=f"student_{student}"))
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=f"Select a student from {group_name}:", reply_markup=markup)

def fetch_students_in_group(service, group_name):
    range_name = f'Copy of {group_name}!A2:A'
    result = service.spreadsheets().values().get(spreadsheetId='1Ogcwmh2_1ahSh1Se5seGAe6j9s8_q-f37SWFMqkbjVw', range=range_name).execute()
    values = result.get('values', [])

    students = [row[0] for row in values if row]

    return students

@bot.callback_query_handler(func=lambda call: call.data.startswith('student_'))
def handle_student_selection(call):
    student_name = call.data.split('_')[1]
    service = google_sheets_api_setup()
    data = look_up_in_sheet(student_name.lower(), service)
    if data != "Name not found.":
        bot.answer_callback_query(call.id, "Fetching data...")
        # Displaying the fetched data as a text message
        bot.send_message(call.message.chat.id, data)

        present, absent = look_up_and_count_attendance(student_name.lower(), service)
        filename = generate_pie_chart(present, absent)
        with open(filename, 'rb') as chart:
            bot.send_photo(call.message.chat.id, chart)
        os.remove(filename)
    else:
        bot.answer_callback_query(call.id, "Student not found.")


if __name__ == '__main__':
    bot.polling(none_stop=True)
