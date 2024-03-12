import telebot
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import os
import matplotlib

matplotlib.use('Agg')  # Use a non-interactive backend for Matplotlib
import matplotlib.pyplot as plt

# Fetch environment variables correctly
TELEGRAM_BOT_TOKEN = os.getenv('6244649557:AAEpEjiL3AGbAOWysrNUdW1BE4FprV3KcHg')
SAMPLE_SPREADSHEET_ID = os.getenv('1Ogcwmh2_1ahSh1Se5seGAe6j9s8_q-f37SWFMqkbjVw')

# Google Sheets API Configuration
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# Initialize the bot with your token
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
    bot.reply_to(message, 'Hi! Send me a name to look it up in the Google Sheet.')


@bot.message_handler(func=lambda message: True)
def handle_text(message):
    bot.reply_to(message, "Wait a moment, I'm fetching the data for you.")
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
    labels = 'Present ', 'Absent'
    sizes = [present, absent]
    colors = ['blue', 'red']  # Update colors here

    plt.figure()
    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', shadow=True, startangle=140)
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
                # Count '1' as present
                total_present += row[1:].count('1')
                # Count as absent if the cell is explicitly marked with '0' or is empty
                # Note: This assumes that an empty string ('') represents an absence
                # If your data uses a different marker for absence, adjust accordingly
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
                    return ' | '.join(row)
    return "Name not found."


if __name__ == '__main__':
    bot.polling(none_stop=True)
