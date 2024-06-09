class Node:
    def __init__(self, x):
        self.info = x
        self.next = None


class LinkedList:
    def __init__(self):
        self.head = None
        self.last = None

    def append(self, x):
        p = Node(x)
        if self.head is None:
            self.head = p
            self.last = p
        else:
            self.last.next = p
            self.last = p

    # def print(self):
    #     temp = self.head
    #     while temp:
    #         print(temp.info, end='->')
    #         temp = temp.next
    def print(self):
        temp = self.head
        while temp:
            end = '' if temp.next is None else '->'
            print(temp.info, end=end)
            temp = temp.next
        print()

    def addfirst(self, x):
        p = Node(x)
        if self.head is None:
            self.head = p
            self.last = p
        else:
            temp = self.head
            self.head = p
            p.next = temp

    def delfirst(self):
        if self.head:
            temp = self.head
            self.head = temp.next
            del temp

    def delete(self):
        if self.head:
            if self.head == self.last:
                temp = self.head
                self.head = self.last = None
                del temp
            q = self.head
            while q.next != self.last:
                q = q.next
            q.next = None
            self.last = q

    def search(self, x):
        if self.head is None:
            return 'Empty'
        else:
            temp = self.head
            while temp:
                if temp.info == x:
                    return temp
                temp = temp.next
            return 'Not Found'

    def delmiddle(self, x):
        if self.search(x) != 'Empty' and self.search(x) != 'Not Found':
            if self.search(x)[1] == self.head:
                temp = self.head
                self.head = temp.next
                del temp
                return 'Done'
            p = self.search(x)
            q = self.head
            while q.next != p[1]:
                q = q.next
            q.next = p[1].next
            del p
            return 'Done'
        return 'Not Found'

