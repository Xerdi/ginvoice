import socket
import os
import json


max_connections = 5
buf_size = 1024
host, port = "localhost", 9090
# socket_file = "/run/ginvoice.sock"
socket_file = "./ginvoice.sock"


if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        sock.bind((host, port))
        # sock.bind(socket_file)
        sock.listen(max_connections)

        # print("Listening on %s:%d" % (host, port))
        while True:
            chunks = []
            c, addr = sock.accept()
            print("incoming connection", c, addr)
            # print("Incoming connection from %s:%d" % addr)

            while True:
                chunk = c.recv(buf_size)
                if not chunk:
                    break
                chunks.append(chunk)
                if len(chunk) < buf_size:
                    break
            print(b''.join(chunks))

            try:
                c.send(b"OK")
            except BrokenPipeError as err:
                print("Already gone?")
    finally:
        sock.close()
        if os.path.exists(socket_file):
            os.remove(socket_file)
