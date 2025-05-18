import socket
import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

HOST = '127.0.0.1'
PORT_RANGE = range(1, 65536)
MAX_THREADS = 100

# Shared flag to stop all threads once a success is found
from threading import Event
stop_event = Event()

def attack_port(port, entropy, message):
	if stop_event.is_set():
		return None
	try:
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
			s.settimeout(0.1)
			s.connect((HOST, port))
			s.sendall(message.encode())
			response = s.recv(1024)
			stop_event.set()  # signal success to stop other threads
			return (port, entropy, response.decode())
	except Exception:
		return None

def main():
	entropy = round(random.uniform(1.0, 5.0), 2)
	message = f"ATTACK|E:{entropy}"

	with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
		futures = [executor.submit(attack_port, port, entropy, message) for port in PORT_RANGE]
		for future in as_completed(futures):
			res = future.result()
			if res:
				port, entropy_sent, resp = res
				print(f"[Attacker] SUCCESS! Port {port}: Sent E={entropy_sent}, got: {resp}")
				break  # Exit loop on first success

if __name__ == "__main__":
	main()