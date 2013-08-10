#!/bin/python2.7
# Adapted from http://docs.python.org/2/library/socket.html
import socket
from threading import Thread
from threading import active_count
import argparse

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
		
if args.server is True:

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

elif args.client is True:
	for PORT in PORTS:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((args.host, PORT))
		s.sendall('Probing ' + str(PORT))
		data = s.recv(1024)
		s.close()
		print 'Received', repr(data)