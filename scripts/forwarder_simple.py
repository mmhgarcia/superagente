import socketserver, threading, socket

class Proxy(socketserver.StreamRequestHandler):
    def handle(self):
        up = socket.create_connection(("127.0.0.1", 11434))
        def relay(src, dst):
            try:
                while True:
                    d = src.recv(4096)
                    if not d: break
                    dst.sendall(d)
            except: pass
            finally:
                try: src.close(); dst.close()
                except: pass
        threading.Thread(target=relay, args=(up, self.request), daemon=True).start()
        relay(self.request, up)

srv = socketserver.ThreadingTCPServer(("0.0.0.0", 11435), Proxy)
srv.allow_reuse_address = True
print("Forwarder 0.0.0.0:11435 -> 127.0.0.1:11434", flush=True)
srv.serve_forever()
