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
        secret, shared_secret = server.start_server(conn)
    else:
        s.connect((ip, port))
        conn = s
        secret, shared_secret = client.start_client(conn)

    key = AES_encoder.derive_key(shared_secret)
    AES_encoder.save_key(key)
    return conn, key, secret, shared_secret

def send_encrypted(conn, message, key, return_encrypted=False):
    padded = message.encode().ljust(16, b'\x00')[:16]
    encrypted = AES_encoder.aes_encrypt_block(padded, key)
    conn.sendall(encrypted)
    if return_encrypted:
        return encrypted

def receive_encrypted(conn, key, return_encrypted=False):
    encrypted = conn.recv(16)
    decrypted = AES_decoder.aes_decrypt_block(encrypted, key).rstrip(b'\x00').decode(errors='ignore')
    if return_encrypted:
        return encrypted, decrypted
    return decrypted

