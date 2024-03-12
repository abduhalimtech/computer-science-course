class Course:
    def __init__(self, name, credit, semester):
        self.name = name
        self.credit = credit
        self.semester = semester
        self.students = []

    def add_student(self, student):
        if student not in self.students:
            self.students.append(student)
            student.courses.append(self)

    def remove_student(self, student):
        if student in self.students:
            self.students.remove(student)
            student.courses.remove(self)

    def get_info(self):
        print(f"Course Name: {self.name}")
        print(f"Credit: {self.credit}")
        print(f"Semester: {self.semester}")
        print("Students enrolled:")
        for student in self.students:
            print(student.name)


class Student:
    def __init__(self, name, group):
        self.name = name
        self.group = group
        self.courses = []

    def add_course(self, course):
        if course not in self.courses:
            self.courses.append(course)
            course.students.append(self)

    def remove_course(self, course):
        if course in self.courses:
            self.courses.remove(course)
            course.students.remove(self)

    def get_info(self):
        print(f"Student Name: {self.name}")
        print(f"Group: {self.group}")
        print("Courses enrolled:")
        for course in self.courses:
            print(course.name)


def main():
    courses = {}
    students = {}

    while True:
        action = input(
            "Choose an action: [add_course, add_student, enroll, unenroll, student_info, course_info, quit]: ")

        if action == "add_course":
            name = input("Enter course name: ")
            credit = int(input("Enter course credit: "))
            semester = input("Enter semester: ")
            courses[name] = Course(name, credit, semester)

        elif action == "add_student":
            name = input("Enter student name: ")
            group = input("Enter student group: ")
            students[name] = Student(name, group)

        elif action == "enroll":
            student_name = input("Enter student name: ")
            course_name = input("Enter course name: ")
            if student_name in students and course_name in courses:
                students[student_name].add_course(courses[course_name])

        elif action == "unenroll":
            student_name = input("Enter student name: ")
            course_name = input("Enter course name: ")
            if student_name in students and course_name in courses:
                students[student_name].remove_course(courses[course_name])

        elif action == "student_info":
            name = input("Enter student name: ")
            if name in students:
                students[name].get_info()

        elif action == "course_info":
            name = input("Enter course name: ")
            if name in courses:
                courses[name].get_info()

        elif action == "quit":
            break

if __name__ == "__main__":
    main()
