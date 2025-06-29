import socket
import AES_encoder
import AES_decoder
import server
import client

def start_peer_gui(is_server, ip='localhost', port=9999, username="User", approval_callback=None):
    s = socket.socket()
    
    if is_server:
        s.bind(('', port))
        s.listen(1)
        print("Waiting for a client to connect...")

        conn, addr = s.accept()
        print(f"Client attempting to connect from {addr}")

        # First receive client's username
        client_username_raw = conn.recv(32)
        client_username = client_username_raw.rstrip(b'\x00').decode('utf-8')

        # Ask host for approval
        if approval_callback:
            approved = approval_callback(client_username, addr)
            if not approved:
                conn.sendall(b"DENIED")
                conn.close()
                return None, None, None, None, None
        else:
            approved = True

        conn.sendall(username.encode('utf-8').ljust(32, b'\x00'))

        secret, shared_secret = server.start_server(conn)

    else:
        try:
            s.connect((ip, port))
        except Exception as e:
            raise ConnectionError(f"Failed to connect to host at {ip}:{port}: {e}")

        conn = s
        conn.sendall(username.encode('utf-8').ljust(32, b'\x00'))

        # Wait to receive host's response or denial
        response = conn.recv(32)
        if response.startswith(b"DENIED"):
            raise ConnectionAbortedError("Connection was denied by the host.")

        peer_username = response.rstrip(b'\x00').decode('utf-8')
        secret, shared_secret = client.start_client(conn)

        return conn, AES_encoder.derive_key(shared_secret), secret, shared_secret, peer_username

    key = AES_encoder.derive_key(shared_secret)
    AES_encoder.save_key(key)

    return conn, key, secret, shared_secret, client_username

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


