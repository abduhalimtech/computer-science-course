import csv

def reset_password():
    username = input("Enter your username: ")

    with open('user-data.csv', mode='r') as csvfile:
        reader = csv.DictReader(csvfile)
        users = list(reader)
        for row in users:
            if row['User_name'] == username:
                print(row['Special_question'])
                answer = input("Answer: ")
                if row['Special_answer'].lower() == answer.lower():
                    new_password = input("Enter new password: ")
                    row['Password'] = new_password
                    print("Password has been updated successfully.")
                    break
        else:
            print("User not found.")
            return

    with open('user-data.csv', mode='w', newline='') as csvfile:
        fieldnames = ['User_id', 'User_name', 'Password', 'Special_question', 'Special_answer']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(users)

if __name__ == "__main__":
    reset_password()
