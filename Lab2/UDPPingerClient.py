import time
from socket import *

# Create the client socket and connect to server
clientSocket = socket(AF_INET, SOCK_DGRAM)
serverPort = 12000
address = ("localhost", serverPort)
clientSocket.settimeout(1)
print("Connected to server")

# Declarations for round-trip times and number of packet losses
rttList = []
packetLossNum = 0

# Attempt to ping 10 times
for i in range(1, 11):
    try: 
        # Get start time
        startTime = time.time()

        # Assign and send ping message
        sendMessage = (f"Ping {i} {startTime}")
        clientSocket.sendto(sendMessage.encode(), address)

        # Receive response and get end time
        recvMessage, address = clientSocket.recvfrom(1024)
        endTime = time.time()
        recvMessage = recvMessage.decode()

        # Print response
        print("Message from server: ", recvMessage)

        # Calculate round-trip time and add it to the list
        rtt = endTime - startTime
        rttList.append(rtt)

        # Print round-trip time
        print("Round-trip time: ", rtt)
    
    # If the client socket times out
    except timeout:
        # Add to the number of packets lost
        packetLossNum += 1
        print("Request timed out")


clientSocket.close()

minRTT = min(rttList)
maxRTT = max(rttList)
avgRTT = sum(rttList) / len(rttList)
packetLossRate = (packetLossNum / 10) * 100
print(f'\nMinimum RTT: {minRTT} s')
print(f'Maximum RTT: {maxRTT} s')
print(f'Average RTT: {avgRTT} s')
print(f'Packet Loss Rate: {packetLossRate}%')
