import socket
import threading

HOST = ''  # Listen on all interfaces
PORT_RANGE = range(1, 65536)  # Full port range
MAX_PORTS = 500  # Prevent "Too many open files" error

def handle_client(conn, addr, port):
    try:
        data = conn.recv(1024).decode().strip()
        if data.startswith("ATTACK|E:"):
            try:
                entropy = float(data.split("E:")[1])
                decision = "BLOCKED" if entropy > 3.2 else "ALLOWED"
                conn.send(decision.encode())
                print(f"[Defender] Port {port} | From {addr} | E={entropy:.2f} | {decision}")
            except ValueError:
                conn.send(b"ERROR")
        else:
            conn.send(b"INVALID")
    except Exception as e:
        print(f"[Defender] Error on port {port} from {addr}: {e}")
    finally:
        conn.close()

def listen_on_port(port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((HOST, port))
            s.listen()
            while True:
                conn, addr = s.accept()
                threading.Thread(target=handle_client, args=(conn, addr, port), daemon=True).start()
    except OSError as e:
        print(f"[Defender] Could not bind to port {port}: {e}")

def main():
    print("[Defender] Starting listener...")
    active_ports = 0

    for port in PORT_RANGE:
        if active_ports >= MAX_PORTS:
            break
        threading.Thread(target=listen_on_port, args=(port,), daemon=True).start()
        active_ports += 1

    print(f"[Defender] Listening on {active_ports} ports.")
    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        print("\n[Defender] Shutting down...")

if __name__ == "__main__":
    main()
