import tkinter as tk
from tkinter import messagebox
import threading
import socket
import chat
import base64

class ChatGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Chat App")
        self.geometry("400x500")
        
        self.sock = None
        self.conn = None
        self.key = None

        self.create_welcome_page()

    def create_welcome_page(self):
        for widget in self.winfo_children():
            widget.destroy()

        welcome_label = tk.Label(self, text="Welcome to Chat", font=("Arial", 16))
        welcome_label.pack(pady=20)

        host_button = tk.Button(self, text="Host Room", command=self.host_room)
        host_button.pack(pady=10)

        join_button = tk.Button(self, text="Join Room", command=self.join_room)
        join_button.pack(pady=10)

    def host_room(self):
        threading.Thread(target=self.start_server, daemon=True).start()

    def join_room(self):
        threading.Thread(target=self.start_client, daemon=True).start()

    def start_server(self):
        try:
            self.sock = socket.socket()
            self.sock.bind(('localhost', 9999))
            self.sock.listen(1)
            print("Waiting for connection...")
            self.conn, addr = self.sock.accept()
            print(f"Connected to {addr}")
            
            self.key = chat.server.start_server(self.conn)
            self.key = chat.AES_encoder.derive_key(self.key)
            chat.AES_encoder.save_key(self.key)
            
            self.setup_chat_page()
            
            threading.Thread(target=self.receive_loop, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("Connection Error", str(e))

    def start_client(self):
        try:
            self.conn = socket.socket()
            self.conn.connect(('localhost', 9999))
            print("Connected to server")

            self.key = chat.client.start_client(self.conn)
            self.key = chat.AES_encoder.derive_key(self.key)
            chat.AES_encoder.save_key(self.key)

            self.setup_chat_page()
            
            threading.Thread(target=self.receive_loop, daemon=True).start()
        except Exception as e:
            messagebox.showerror("Connection Error", str(e))

    def setup_chat_page(self):
        for widget in self.winfo_children():
            widget.destroy()

        self.text_area = tk.Text(self, state='disabled')
        self.text_area.pack(expand=True, fill='both', padx=10, pady=10)

        self.entry = tk.Entry(self)
        self.entry.pack(fill='x', padx=10, pady=10)
        self.entry.bind("<Return>", lambda event: self.send_message())

        self.send_button = tk.Button(self, text="Send", command=self.send_message)
        self.send_button.pack(pady=5)

    def receive_loop(self):
        while True:
            try:
                data = self.conn.recv(16)
                if not data:
                    break
                decrypted = chat.AES_decoder.aes_decrypt_block(data, self.key)
                message = decrypted.rstrip(b'\x00').decode(errors='ignore')
                self.display_message("Peer", message)
            except Exception as e:
                self.display_message("System", f"Connection error: {e}")
                break

    def send_message(self):
        if not self.conn:
            messagebox.showwarning("Warning", "Not connected to a peer.")
            return

        message = self.entry.get()
        if not message.strip():
            return

        try:
            msg_bytes = message.encode('utf-8').ljust(16, b'\x00')[:16]
            encrypted = chat.AES_encoder.aes_encrypt_block(msg_bytes, self.key)
            
            print(f"Sending message (plaintext): {message}")
            print(f"Sending message (encrypted bytes): {encrypted}")
            print(f"Encrypted (hex): {encrypted.hex()}")
            print(f"Sending message (encrypted base64): {base64.b64encode(encrypted).decode()}")


            self.conn.sendall(encrypted)
            self.display_message("You", message)
            self.entry.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Send Error", str(e))

    def display_message(self, sender, message):
        self.text_area.config(state='normal')
        self.text_area.insert(tk.END, f"{sender}: {message}\n")
        self.text_area.config(state='disabled')
        self.text_area.see(tk.END)

if __name__ == "__main__":
    app = ChatGUI()
    app.mainloop()
