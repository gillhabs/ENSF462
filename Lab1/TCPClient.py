from socket import *

# Get input for user 1's name
user1Name = input("Please enter user 1's name: ")

# Send user 1's name to server 
# Create the client socket
clientSocket = socket(AF_INET, SOCK_STREAM)

# Connect to the server
serverPort = 12000
clientSocket.connect(("localhost", serverPort))
print("Connected to server")

# Send user 1's name to server
clientSocket.send(user1Name.encode())
print("Sent user 1's name to server")

# Get response (user 2's name)
user2Name = clientSocket.recv(1024).decode()
print(f"From Server: {user2Name}")

# Start the chat
turn = user1Name

while True:
    if turn == user1Name:
        message = input(f"Enter message for {user1Name} to send: ")
        clientSocket.send(message.encode())
        if message.lower() == 'bye':
            break
        print(f"Sent message to {user2Name}\n{user2Name} is sending... ", end = "")
        turn = user2Name

    else:
        message = clientSocket.recv(1024).decode()
        print(f"{message}")
        if message.lower() == 'bye':
            break
        turn = user1Name

# Close the socket
clientSocket.close()