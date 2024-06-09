import socket

def start_udp_client():
    # Create a UPD client
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    #server address and port
    server_address = 'localhost'
    server_port = 12000

    # Message to send
    message = 'Hello, From client!'.encode()

    # Send the message
    client_socket.sendto(message, (server_address, server_port))

    # Recieve the server's response
    response, server = client_socket.recvfrom(2048)
    print(f"Servers response: {response.decode()}")

    client_socket.close()

start_udp_client()
