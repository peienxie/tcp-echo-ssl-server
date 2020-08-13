import socket
import ssl

# SET VARIABLES
packet = b"somedata"
HOST, PORT = 'localhost', 8787

# CREATE SOCKET
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(30)

# WRAP SOCKET
wrappedSocket = ssl.wrap_socket(sock, ssl_version=ssl.PROTOCOL_TLSv1_2)

# CONNECT AND PRINT REPLY
wrappedSocket.connect((HOST, PORT))
wrappedSocket.send(packet)
print(wrappedSocket.recv(1280))

# CLOSE SOCKET CONNECTION
wrappedSocket.close()
