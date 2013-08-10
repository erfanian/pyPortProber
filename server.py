#!/bin/python2.7
# Adapted from http://docs.python.org/2/library/socket.html
import socket
from threading import Thread

class extended_thread(Thread):
	PORT = None
	HOST = ''
	def run(self):
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.bind((self.HOST, self.PORT))
		s.listen(1)
		conn, addr = s.accept()
		print 'Connected by', addr
		while 1:
		    data = conn.recv(1024)
		    if not data: break
		    conn.sendall(data)
		conn.close()

PORTS = range(50000, 52000)              # Arbitrary non-privileged port
for PORT in PORTS:
    thread = extended_thread()
    thread.PORT = PORT
    thread.start()