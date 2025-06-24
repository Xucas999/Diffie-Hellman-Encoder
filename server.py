import socket
import random
import DH_encoder as enc

def start_server(conn):
    # Diffie-Hellman Parameters
    p = enc.get_prime(random.randint(23,100)) # Shared Big Prime
    g = enc.get_prime(random.randint(2,19)) # Shared Base Prime
    secret_value = random.randint(5,20)
    server_public_key = enc.calculate_public_shared_values(secret_value, g, p)

    # Step 1: Send Relevant Values
    conn.sendall(f"{p},{g},{server_public_key}".encode())

    # Step 2: Receive Client's public key
    data = conn.recv(1024).decode()
    client_public_key = int(data)

    # Step 3: Compute shared secret
    shared_secret = enc.calculate_shared_secret(client_public_key, secret_value, p)
    print(f"Server's Shared Secret: {shared_secret}")

    return shared_secret
