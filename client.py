import socket
import random
import DH_encoder as enc

def start_client(client):
    # Bob's private key
    secret_value = random.randint(5,20)

    # Step 1: Receive p, g, A
    data = client.recv(1024).decode()
    p, g, server_public_key = map(int, data.split(','))
    print(f"Received p={p}, g={g}, public_value={server_public_key}")

    # Step 2: Compute B and send it
    client_public_key = enc.calculate_public_shared_values(secret_value, g, p)
    client.sendall(str(client_public_key).encode())

    # Step 3: Compute shared secret
    shared_secret = enc.calculate_shared_secret(server_public_key, secret_value, p)
    print(f"Bob's Shared Secret: {shared_secret}")
    return shared_secret
    