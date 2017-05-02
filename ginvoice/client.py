import os.path
import socket
import sys
import json

host, port = "localhost", 9090
socket_file = './ginvoice.sock'

if __name__ == '__main__':
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

        with open("example/supplier_defaults.json", "rb") as f:
            try:
                # sock.connect(socket_file)
                sock.connect((host, port))
                sock.send(f.read())
                print("Message sent")
                response = sock.recv(1024)
                print("Result", repr(response))
            except socket.gaierror:
                print("Error resolving host")
                exit(1)
            finally:
                sock.close()
    except socket.error as err:
        print("Socket error because of %s" % err)
        exit(1)
