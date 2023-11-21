# Import socket module
from socket import *

serverSocket = socket(AF_INET, SOCK_STREAM)

# Prepare a sever socket
# Bind the socket to a port 12000
serverPort = 12000
serverSocket.bind(('127.0.0.1', serverPort))

# Listen for incoming connections
serverSocket.listen(1)
print(f'Server is listening on port {serverPort}...')

while True:
    # Establish the connection
    print('Ready to serve...')
    connectionSocket, addr = serverSocket.accept()

    try: 
        message = connectionSocket.recv(1024).decode()

        filename = message.split()[1]
        with open(filename[1:], 'rb') as f:
            outputdata = f.read()

        # Send one HTTP header line into socket
        connectionSocket.send("HTTP/1.1 200 OK\r\n\r\n".encode())

        # Send the content of the requested file to the client
        connectionSocket.sendall(outputdata)

    except IOError:
        # Send response message for file not found
        error_message = "HTTP/1.1 404 Not Found\r\n\r\nFile Not Found"
        connectionSocket.send(error_message.encode())

    # Close client socket
    connectionSocket.close()

serverSocket.close()
