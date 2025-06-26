import socket
import AES_encoder
import AES_decoder
import server
import client

def start_peer_gui(is_server, ip='localhost', port=9999):
    s = socket.socket()
    if is_server:
        s.bind(('', port))
        s.listen(1)
        conn, _ = s.accept()
        key = server.start_server(conn)
    else:
        s.connect((ip, port))
        conn = s
        key = client.start_client(conn)

    key = AES_encoder.derive_key(key)
    AES_encoder.save_key(key)
    return conn, key

def send_encrypted(sock, msg, key):
    padded = msg.encode().ljust(16, b'\x00')[:16]
    encrypted = AES_encoder.aes_encrypt_block(padded, key)
    sock.sendall(encrypted)

def receive_encrypted(sock, key):
    data = sock.recv(16)
    if not data:
        return None
    decrypted = AES_decoder.aes_decrypt_block(data, key)
    return decrypted.rstrip(b'\x00').decode(errors='ignore')

