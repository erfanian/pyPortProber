# Adapted from http://docs.python.org/2/library/socket.html
import socket

HOST = '127.0.0.1'    # The remote host
PORTS = range(50000, 50100)            # The same port as used by the server

for PORT in PORTS:
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((HOST, PORT))
	s.sendall('Probing ' + str(PORT))
	data = s.recv(1024)
	s.close()
	print 'Received', repr(data)