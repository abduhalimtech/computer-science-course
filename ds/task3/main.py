from linkedList import LinkedList

def common_products(a, b):
    common = LinkedList()
    current = a.head
    while current:
        if b.search(current.info) != 'Not Found':
            common.append(current.info)
        current = current.next
    return common

bosch = LinkedList()
bosch.append("olma")
bosch.append("anor")
bosch.append("behi")

philip = LinkedList()
philip.append("olcha")
philip.append("anor")
philip.append("olma")
philip.append("tarvuz")

common = common_products(bosch, philip)
common.print()
