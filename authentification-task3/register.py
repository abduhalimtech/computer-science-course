import csv
import re

def validate_password(password):
    if (len(password) < 8 or
            not re.search("[a-z]", password) or
            not re.search("[A-Z]", password) or
            not re.search("[0-9]", password) or
            not re.search("[_@$]", password)):
        return False
    return True

def check_user_exists(username):
    with open('user-data.csv', mode='r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['User_name'] == username:
                return True
    return False

def register_user():
    username = input("Enter username: ")
    if check_user_exists(username):
        print("Username already exists. Try a different one.")
        return
    password = input("Enter password: ")
    if not validate_password(password):
        print("Password must be at least 8 characters long, include an uppercase letter, a number, and a symbol (_@$).")
        return
    special_question = "What's your pet's name?"
    special_answer = input("What's your pet's name? ")

    with open('user-data.csv', mode='a', newline='') as csvfile:
        fieldnames = ['User_id', 'User_name', 'Password', 'Special_question', 'Special_answer']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        last_id = 0
        with open('user-data.csv', mode='r') as f:
            last_line = list(f)[-1]
            last_id = int(last_line.split(',')[0])

        writer.writerow({
            'User_id': last_id + 1,
            'User_name': username,
            'Password': password,
            'Special_question': special_question,
            'Special_answer': special_answer
        })
    print("Registration successful!")

if __name__ == "__main__":
    register_user()
