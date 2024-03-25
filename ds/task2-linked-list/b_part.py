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

    def removeRight(self, value):
        if self.isEmpty():
            print("Deque is empty.")
            return
        temp = []
        found = False
        # Start from the rear
        while self.rear and not found:
            if self.rear.info == value:
                found = True
                # Remove the found node
                if self.rear == self.front:  # If it's the only node
                    self.front = self.rear = None
                else:
                    self.rear = self.rear.prev
                    self.rear.next = None
            else:
                # store the value and remove the node from the rear
                temp.append(self.rear.info)
                # remove the current rear node
                self.rear = self.rear.prev
                if self.rear:
                    self.rear.next = None
                else:
                    self.front = None  # whenthe deque becomes empty

        if not found:
            print("Item not found in the deque.")
            for val in temp[::-1]:  # the temp list - original order
                self.addRear(val)
        else:
            for val in temp[::-1]:
                self.addRear(val)

deque = Deque()
elements = [1, 2, 3, 4, 5, 6, 7, 8]

for i, element in enumerate(elements):
    if i % 2 == 0:
        deque.addFront(element)  # Add to left
    else:
        deque.addRear(element)  # Add to right

print("Deque before removing an item from the right side:")
deque.display()

user_specified_item = int(input('enter an element to be removed: '))
deque.removeRight(user_specified_item)

print(f"Deleted {user_specified_item} ")
deque.display()
