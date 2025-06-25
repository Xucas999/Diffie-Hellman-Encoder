import socket
import threading
import AES_decoder
import AES_encoder
import DH_encoder as enc
import server
import client

def start_peer(is_server):
    s = socket.socket()
    if is_server:
        s.bind(('localhost', 9999))
        s.listen(1)
        print("Waiting for connection...")
        conn, addr = s.accept()
        print(f"Connected to {addr}")
        key = server.start_server(conn)
        key = AES_encoder.derive_key(key)
        AES_encoder.save_key(key)
    else:
        s.connect(('localhost', 9999))
        conn = s
        key = client.start_client(conn)
        key = AES_encoder.derive_key(key)
        AES_encoder.save_key(key)

    return conn, key

