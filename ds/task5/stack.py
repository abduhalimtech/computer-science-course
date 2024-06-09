class Stack:
    def __init__(self):
        self.items = []

    def push(self, item):
        """Element qo'shadi"""
        self.items.append(item)

    def pop(self):
        """Oxirgi elementni olib tashlaydi va uni qaytaradi"""
        if not self.isEmpty():
            return self.items.pop()

    def top(self):
        """Oxirgi elementni qaytaradi, lekin uni o'chirmaydi"""
        if not self.isEmpty():
            return self.items[-1]

    def isEmpty(self):
        """Stack bo'sh yoki yo'qligini qaytaradi"""
        return len(self.items) == 0
