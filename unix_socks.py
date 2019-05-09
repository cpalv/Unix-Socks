#!/usr/bin/env python3
import asyncio
import socket
import time
import os

UNX_SOCK = './temp.sock'
MAX_BYTES = 256
MAX_TRIES = 5

async def server():
	sock_loop = asyncio.get_event_loop()
	with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM | socket.SOCK_NONBLOCK) as sock:
		try:
			sock.bind(UNX_SOCK)
		except OSError:
			exit()
		sock.listen(5)
		print("Waiting for connection")
		while True:
			conn, addr = await sock_loop.sock_accept(sock)
			conn.setblocking(False)
			print("Server Connected with", addr)
			echo = b'Hello from Server!'
			data = await sock_loop.sock_recv(conn, MAX_BYTES)
			print("Data:", data)
			await sock_loop.sock_sendall(conn, echo)
			conn.close()

def client():
	time.sleep(5)
	for _ in range(MAX_TRIES):
		with socket.socket(family=socket.AF_UNIX, type=socket.SOCK_STREAM) as sock:
			try:
				sock.connect(UNX_SOCK)
			except socket.error as e:
				print("Client error", e)

			msg = b'This is the client'
			sock.sendall(msg)
			res = sock.recv(MAX_BYTES)
			print("Client recv'd:", res)

def main():
	try:
		os.unlink(UNX_SOCK)
	except OSError as e:
		print("OSError:", e)

	pid = os.fork()

	if pid:
		loop = asyncio.get_event_loop()
		loop.create_task(server())
		try:
			loop.run_forever()
		except KeyboardInterrupt:
			exit()
	else:
		client()
	exit()

if __name__ == '__main__':
	main()