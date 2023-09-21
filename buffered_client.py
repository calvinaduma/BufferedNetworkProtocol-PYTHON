# TODO: add any import statements required
from socket import *
from struct import pack, unpack

class BufferedTCPClient:

    def __init__(self, server_host='localhost', server_port=36001, buffer_size=1024):
        self.buffer_size = buffer_size
        self.server_port = server_port
        self.server_host = server_host
        # TODO: Create a socket and establish a TCP connection with server 
        self.tcpClientSocket = socket(AF_INET, SOCK_STREAM)
        self.tcpClientSocket.connect((server_host, server_port))


    # This method is called by the autograder. You must implement it, and you cannot change the method signature. It should accept a message
    # from the user, which is packed according to the format specified for this assignment and then sent into the socket.
    # TODO: * Send a message to the server containing the message passed in to the function. 
    #           * Remember to pack it using the format defined in the instructions. 
    def send_message(self, message):
        print("CLIENT: Attempting to send a message...")

        messageLength = len(message)
        if messageLength > 65535:
            message1 = message[0:65535].encode()
            message2 = message[65535:].encode()
            message1Length = len(message[0:65535])
            message2Length = len(message[65535:])
            formatString1 = "!H" + str(message1Length) + "s"
            formatString2 = "!" + str(message2Length) + "s"
            packedData1 = pack(formatString1, message1Length, message1)
            packedData2 = pack(formatString2, message2Length, message2)
        else:
            message = message.encode()
            formatString = "!H" + str(messageLength) + "s"
            packedData = pack(formatString, messageLength, message)

        try:
            if messageLength > 65535:
                self.tcpClientSocket.send(packedData1)
                self.tcpClientSocket.send(packedData2)
            else:
                self.tcpClientSocket.send(packedData)
        except ConnectionResetError as e:
            self.tcpClientSocket = socket(AF_INET, SOCK_STREAM)
            self.tcpClientSocket.connect((self.server_host, self.server_port))
            if messageLength > 65535:
                self.tcpClientSocket.send(packedData1)
                self.tcpClientSocket.send(packedData2)
            else:
                self.tcpClientSocket.send(packedData)
            


    # This method is called by the autograder. You must implement it, and you cannot change the method signature. It should wait to receive a 
    # message from the socket, which is then returned to the user. It should return two values: the message received and whether or not it was received 
    # successfully. In the event that it was not received successfully, return an empty string for the message.
    # TODO: * Return the *string* sent back by the server. This should be the same string you sent, except that first 10 characters will have been removed
    #           * Be sure to set the bufsize parameter to self.buffer_size when calling the socket's receive function
    #           * Remember that we're sending packed messages back and forth, for the format defined in the assignment instructions. You'll have to unpack
    #             the message and return just the string. Don't return the raw response from the server.
    #       * Handle any errors associated with the server disconnecting
    def receive_message(self):
        print("CLIENT: Attempting to receive a message...")

        loop = True
        while loop:
            loop = False
            try:
                tcpResponseByteArray = self.tcpClientSocket.recv(self.buffer_size)
                if tcpResponseByteArray:
                    formatString = "!H" + str(len(tcpResponseByteArray)-2) + "s"
                    length = unpack(formatString, tcpResponseByteArray)[0]
                    packedMessage = unpack(formatString, tcpResponseByteArray)[1]
                    payloadBuffer = b"" # stores the bytes of message less than buffer size  
                    payloadBuffer += packedMessage 
                    offset = 2
                    while len(payloadBuffer) < (length-offset):
                        bufferSize = min(1024, length - len(payloadBuffer)) # chooses the smallest size for buffer to not get more data than necessary 
                        tcpResponseByteArray = self.tcpClientSocket.recv(bufferSize)
                        formatString = "!" + str(len(tcpResponseByteArray)) + "s"
                        packedMessage = unpack(formatString, tcpResponseByteArray)[0]
                        payloadBuffer += packedMessage
                        if tcpResponseByteArray:
                            pass
                        else:
                            return "", False

                else:
                    return "", False

            except ConnectionResetError as e:
                self.tcpClientSocket.connect((self.server_host, self.server_port))
                loop = True

        message = payloadBuffer.decode()
        return message, True


    # This method is called by the autograder. You must implement it, and you cannot change the method signature. It should close your socket.
    # TODO: Close your socket
    def shutdown(self):
        print("Client: Attempting to shut down...")
        self.tcpClientSocket.close()

        
if __name__ == "__main__":
    l = BufferedTCPClient(server_host="localhost", server_port=36001)

    l.send_message("Four score and seven years ago")
    response = l.receive_message()