import socket, threading, sys, os

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
    threading.Thread(target=relay, args=(conn, up), daemon=True).start()
    relay(up, conn)

if __name__ == "__main__":
    with open(PID_FILE, "w") as f:
        f.write(str(os.getpid()))
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("0.0.0.0", 11435))
    srv.listen(5)
    print("Forwarding 0.0.0.0:11435 -> 127.0.0.1:11434", flush=True)
    while True:
        conn, _ = srv.accept()
        threading.Thread(target=handle, args=(conn,), daemon=True).start()
