import socket

def start_udp_server():
    # create udp
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # bind the socket to a port
    server_address = 'localhost'
    server_port = 12000
    server_socket.bind((server_address, server_port))

    print("UDP server is up and listening")

    # Handle incoming messages
    while True:
        message, client_address = server_socket.recvfrom(2048)
        print(f"Recieved message: {message.decode()} from {client_address}")

        #Echo the message back to the client
        server_socket.sendto(message, client_address)

start_udp_server()
