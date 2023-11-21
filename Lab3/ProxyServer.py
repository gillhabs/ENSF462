import sys
from socket import *

if len(sys.argv) <= 1:
    print('Usage : "python ProxyServer.py server_ip"\t[server_ip : It is the IP Address Of Proxy Server]')
    sys.exit(2)

# Create a server socket, bind it to a port, and start listening
port = 8888
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind(("localhost", port))
serverSocket.listen(1)
print(f"Server is listening on port {port}...")


while True:
    # Accept connection from server
    print("Ready to serve...")
    clientSocket, addr = serverSocket.accept()
    print("Received a connection from:", addr)

    # Receive message 
    message = clientSocket.recv(1024).decode()
    print("Message is: ", message)

    if " " in message:
        filename = message.split()[1]
        request_lines = message.split("\r\n")

        if not request_lines[0].startswith("GET"):
            clientSocket.send(b"HTTP/1.0 400 Bad Request\r\n")
            clientSocket.close()
            exit(2)

        if filename == "/favicon.ico":
            response = "HTTP/1.0 200 OK\r\nContent-Type: image/x-icon\r\n\r\n"
            response += "Binary data for favicon.ico"
            clientSocket.send(response.encode())


        else:    
            url = filename.partition("/")
            filetouse = url[2]

            if (filetouse.find("/"))!= -1:
                file = "/" + filetouse[:filetouse.rfind(".")]
                path = filetouse[filetouse.find("/"):]
                filetouse = filetouse[:filetouse.find("/")]
                file_exists = False

            else:
                path = "/"
                file = "/" + filetouse
                file_exists = False

            try:
                tmp_file_to_use = file.replace("/", "-")
                with open(tmp_file_to_use[1:], "rb") as f:
                    output_data = f.read()
                    file_exists = True
                    clientSocket.send(output_data)
                    print('Cache hit')

            except IOError:
                if file_exists == False:
                    connectionSocket = socket(AF_INET, SOCK_STREAM)
                    hostn = filetouse.replace("www.", "", 1)
                    print(hostn)
 
                    try:
                        connectionSocket.connect((hostn, 80))
                        request = f"GET {path} HTTP/1.0\r\nHost: {hostn}\r\n\r\n"
                        connectionSocket.send(request.encode())
                        buffer = b""

                        while (1):
                            data = connectionSocket.recv(1024)
                            if not data:
                                break
                            buffer += data

                        clientSocket.send(buffer)

                        temp = file.replace("/", "-")
                        print(temp)
                        with open("./" + temp[1:], "wb") as tmp_file:
                            tmp_file.write(buffer)

                    except:
                        print("Illegal request")


    else:
        print("Invalid request")

    # Close the client and the server sockets
    clientSocket.close()

serverSocket.close()
