#!/bin/python2.7
# Adapted from http://docs.python.org/2/library/socket.html
import socket
from threading import Thread
from threading import active_count
import argparse
from time import sleep

parser = argparse.ArgumentParser(description='A utility to test port blocking or utilization.')
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('--server', action='store_true', dest='server', help='Act as a server.')
group.add_argument('--client', action='store_true', dest='client', help='Act as a client.')
parser.add_argument('--host', default='127.0.0.1', nargs='+', dest='host', help='The target host.')
parser.add_argument('--ports', default='', nargs='+', dest='ports', required=True, help='The target port(s).')
args = parser.parse_args()

def extract(x):
    result = []
    for part in x.split(','):
        if '-' in part:
            a, b = part.split('-')
            a, b = int(a), int(b)
            result.extend(range(a, b + 1))
        else:
            a = int(part)
            result.append(a)
    return result

PORTS = extract(str(args.ports[0]))

class extended_thread(Thread):
	PORT = None
	HOST = ''
	def run(self):
		try:
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.bind((self.HOST, self.PORT))
			s.listen(1)
			s.settimeout(120)
			conn, addr = s.accept()
			print 'Connected by', addr
			while 1:
			    data = conn.recv(1024)
			    if not data: break
			    conn.sendall(data)
			conn.close()
			server_welcome.socket_success.append(self.PORT)
		except socket.timeout as msg:
			s.close()
			s = None
			print "Socket " + str(self.PORT) + " timed out after two minutes."
			server_welcome.local_socket_exceptions.append(self.PORT)
		except socket.error as msg:
			s.close()
			s = None
			server_welcome.local_socket_exceptions.append(self.PORT)

class handshake():

	def __init__(self, ports):
		self.target_port = 60100
		self.received_port_list = []
		self.local_port_list = ports
		self.local_socket_exceptions = []
		self.remote_socket_exceptions = []
		self.socket_success = []

	def server_shake(self, payload):
		try:
			if self.target_port <= 60200:
				s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				s.bind(('', self.target_port))
				s.listen(1)
				s.settimeout(120)
				conn, addr = s.accept()
				while 1:
					print "Receiving data..."
					data = conn.recv(1024)
					print "sending data..."
					conn.sendall(str(payload))
					break
				conn.close()
				return list(data)
			else:
				print "I never heard from the client, or I couldn't secure a port."
		except socket.timeout as msg:
			s.close()
			s = None
			print "Socket " + str(self.target_port) + " timed out after two minutes."
		except socket.error as msg:
			s.close()
			s = None
			self.target_port += 1
			self.server_shake(payload)
	
	def client_shake(self, payload):
		try:
			if self.target_port <= 60200:
				s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				s.connect((args.host, self.target_port))
				s.settimeout(120)
				print "Sending data..."
				s.sendall(str(payload))
				print "Receiving data..."
				data = s.recv(1024)
				s.close()
				return list(data)
			else:
				print "I never heard from the server, or I couldn't secure a port."
		except socket.timeout as msg:
			s.close()
			s = None
			print "Socket " + str(self.target_port) + " timed out after two minutes."
		except socket.error as msg:
			s.close()
			s = None
			self.target_port += 1
			self.client_shake(payload)
	
	def port_diff(self, local_ports, received_ports):
		return set(local_ports).symmetric_difference_update(set(received_ports))

if args.server is True:

	print "Shaking hands..."
	server_welcome = handshake(PORTS)
	server_welcome.received_port_list = server_welcome.server_shake(server_welcome.local_port_list)

	if len(PORTS) > 100:
		while len(PORTS) > 0:
			if active_count() <= 50:			
				port_buffer = PORTS[:100]
				del PORTS[:100]
				for PORT in port_buffer:
				    thread = extended_thread()
				    thread.PORT = PORT
				    thread.start()
	else:
		for PORT in PORTS:
			thread = extended_thread()
			thread.PORT = PORT
			thread.start()

	while active_count() > 1:
		pass
	
	print "Saying goodbye..."
	server_welcome.remote_socket_exceptions = server_welcome.server_shake(server_welcome.local_socket_exceptions)

	print "These ports were not shared by the client and server: " + str(server_welcome.port_diff(server_welcome.local_port_list, server_welcome.received_port_list))
	print "I successfully received data on: " + str(server_welcome.socket_success)
	print "I experienced errors on ports: " + str(server_welcome.local_socket_exceptions)
	if server_welcome.remote_socket_exceptions is not None:
		print "These errors were not shared: " + str(server_welcome.port_diff(server_welcome.local_socket_exceptions, server_welcome.remote_socket_exceptions))

elif args.client is True:

	print "Shaking hands..."
	client_welcome = handshake(PORTS)
	client_welcome.received_port_list = client_welcome.client_shake(client_welcome.local_port_list)

	sleep(.05)

	for PORT in PORTS:
		try:
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.settimeout(.5)
			s.connect((args.host, PORT))
			s.sendall('Probing ' + str(PORT))
			data = s.recv(1024)
			s.close()
			print 'Received', repr(data)
			client_welcome.socket_success.append(PORT)
		except socket.timeout as msg:
			s.close()
			s = None
			print "Socket " + str(PORT) + " timed out after .5 seconds."
			client_welcome.local_socket_exceptions.append(PORT)
		except socket.error as msg:
			s.close()
			s = None
			client_welcome.local_socket_exceptions.append(PORT)
	
	print "Saying goodbye..."
	client_welcome.remote_socket_exceptions = client_welcome.client_shake(client_welcome.local_socket_exceptions)
		
	print "These ports were not shared by the client and server: " + str(client_welcome.port_diff(client_welcome.local_port_list, client_welcome.received_port_list))
	print "I successfully received data on: " + str(client_welcome.socket_success)
	print "I experienced errors on ports: " + str(client_welcome.local_socket_exceptions)
	if client_welcome.remote_socket_exceptions is not None:
		print "These errors were not shared: " + str(client_welcome.port_diff(client_welcome.local_socket_exceptions, client_welcome.remote_socket_exceptions))