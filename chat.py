import socket
import threading
import AES_decoder
import AES_encoder
import DH_encoder as enc
import server
import client

# Dummy AES stubs — use your real functions here

def send_loop(conn, key):
    while True:
        msg = input("You: ").encode().ljust(16, b'\x00')[:16]
        encrypted = AES_encoder.aes_encrypt_block(msg, key)
        conn.sendall(encrypted)

def receive_loop(conn, key):
    while True:
        data = conn.recv(16)
        if not data:
            break
        decrypted = AES_decoder.aes_decrypt_block(data, key)
        print("\nPeer:", decrypted.rstrip(b'\x00').decode(errors='ignore'))
        print("You: ", end='', flush=True)

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

    key = AES_encoder.load_key()
    threading.Thread(target=send_loop, args=(conn, key), daemon=True).start()
    receive_loop(conn, key)

