class Stack:
    def __init__(self):
        self.items = []

    def isEmpty(self):
        return len(self.items) == 0

    def push(self, item):
        self.items.append(item)

    def pop(self):
        if not self.isEmpty():
            return self.items.pop()
        else:
            raise IndexError("Pop from an empty stack")

    def top(self):
        if not self.isEmpty():
            return self.items[-1]
        else:
            raise IndexError("Top from an empty stack")

def check_brackets(string):
    stack = Stack()  # Use your Stack class
    brackets = {')': '(', '}': '{', ']': '['}  # The matching pairs

    for char in string:  # Look at each character
        if char in '([{':  # If it's an opening bracket
            stack.push(char)  # Put it in the stack
        elif char in ')]}':  # If it's a closing bracket
            if stack.isEmpty() or brackets[char] != stack.pop():  # If it doesn't match or the stack is empty
                return False  #  wrong!

    return stack.isEmpty()  # If the stack is empty, all brackets were matched

# Test with some strings
strings = ["[xxx(x{x}x(x[xx)x])]", '[xxx(x{x}x(xxx)[x])]', '(xx[{x}]xx)', 'Xx{x([x)}x}']
for s in strings:
    if check_brackets(s):
        print(f"{s} correct!")
    else:
        print(f"{s} error")
