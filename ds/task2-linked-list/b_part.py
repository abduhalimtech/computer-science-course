class Node:
    def __init__(self, x):
        self.info = x
        self.next = None
        self.prev = None

class Deque:
    def __init__(self):
        self.front = None
        self.rear = None

    def isEmpty(self):
        return self.front is None

    def addFront(self, item):
        newNode = Node(item)
        if self.isEmpty():
            self.front = self.rear = newNode
        else:
            newNode.next = self.front
            self.front.prev = newNode  # Set the previous link
            self.front = newNode

    def addRear(self, item):
        newNode = Node(item)
        if self.isEmpty():
            self.front = self.rear = newNode
        else:
            self.rear.next = newNode
            newNode.prev = self.rear  # Set the previous link
            self.rear = newNode

    def removeRear(self):
        if self.isEmpty():
            print("Deque is empty, cannot remove")
            return
        info = self.rear.info
        if self.front == self.rear:  # Only one element
            self.front = self.rear = None
        else:
            self.rear = self.rear.prev
            self.rear.next = None
        return info

    def display(self):
        current = self.front
        while current:
            print(current.info, end=" ")
            current = current.next
        print()

# Use the Deque
deque = Deque()
elements = [1, 2, 3, 4, 5, 6, 7, 8]  # The elements we want to add

for i, element in enumerate(elements):
    if i % 2 == 0:
        deque.addFront(element)
    else:
        deque.addRear(element)

print("Deque before removing from rear:")
deque.display()

#remove an element from the rear
removed = deque.removeRear()
print(f"Removed element: {removed}")

print("Deque after removing from rear:")
deque.display()
