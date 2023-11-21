from socket import *

# Get input for user 2's name
user2Name = input("Please enter user 2's name: ")

# Create server socket
serverSocket = socket(AF_INET,SOCK_STREAM)

# Bind the socket to the port
serverPort = 12000
serverSocket.bind(("localhost", serverPort))

# Start listening for connections
serverSocket.listen(1)
print("The server is ready to receive")

# Connect with client
clientSocket, client_address = serverSocket.accept()
print(f"Connection made with {client_address}")

# Receive user 1's name from client
user1Name = clientSocket.recv(1024).decode()
print(f"From Client: {user1Name}")

# Send user 2's name to client
clientSocket.send(user2Name.encode())
print(f"Sent user 2's name to client\n{user1Name} is sending... ", end = "")

# Start chatting
turn = user1Name

while True:
    if turn == user2Name:
        message = input(f"Enter message for {user2Name} to send: ")
        clientSocket.send(message.encode())
        if message.lower() == 'bye':
            break
        print(f"Sent message to {user1Name}\n{user1Name} is sending... ", end = "")
        turn = user1Name

    else:
        message = clientSocket.recv(1024).decode()
        print(f"{message}")
        if message.lower() == 'bye':
            break
        turn = user2Name

# Close the sockets
clientSocket.close()
serverSocket.close()
