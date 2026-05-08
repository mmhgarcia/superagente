import socket, threading, sys, os, time

PID_FILE = "/tmp/ollama_forward.pid"

def relay(src, dst):
    try:
        while True:
            data = src.recv(4096)
            if not data: break
            dst.sendall(data)
    except: pass
    finally:
        try: src.close()
        except: pass
        try: dst.close()
        except: pass

def handle(conn):
    up = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    up.connect(("127.0.0.1", 11434))
    t = threading.Thread(target=relay, args=(conn, up), daemon=True)
    t.start()
    relay(up, conn)

def serve():
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("0.0.0.0", 11435))
    srv.listen(5)
    with open(PID_FILE, "w") as f:
        f.write(str(os.getpid()))
    print("Forwarding 0.0.0.0:11435 -> 127.0.0.1:11434", flush=True)
    while True:
        try:
            conn, addr = srv.accept()
            threading.Thread(target=handle, args=(conn,), daemon=True).start()
        except Exception as e:
            print(f"accept error: {e}", flush=True)
            time.sleep(1)

if __name__ == "__main__":
    while True:
        try:
            serve()
        except Exception as e:
            print(f"forwarder crashed: {e}, restarting in 2s", flush=True)
            time.sleep(2)
