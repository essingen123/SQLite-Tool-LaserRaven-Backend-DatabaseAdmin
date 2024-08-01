
import socket

def find_available_port():
    port = 8000
    while not is_port_available(port):
        port += 1
    return port

def is_port_available(port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', port))
    if result == 0:
        return False
    else:
        return True
