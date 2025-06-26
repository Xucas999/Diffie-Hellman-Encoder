import tkinter as tk
from tkinter import messagebox, scrolledtext
import socket
import threading
import chat

class ChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Secure Chat")
        self.root.geometry("600x500")
        self.root.minsize(400, 400)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        self.init_welcome_page()

    def init_welcome_page(self):
        self.clear_window()
        tk.Label(self.root, text="Welcome to Secure Chat", font=("Arial", 16)).pack(pady=10)

        tk.Button(self.root, text="Host Room", command=self.host_room).pack(pady=5)
        tk.Button(self.root, text="Join Room", command=self.join_room).pack(pady=5)

    def host_room(self):
        self.clear_window()
        tk.Label(self.root, text="Host a Room", font=("Arial", 14)).pack(pady=10)

        tk.Label(self.root, text="Enter Port to Host On:").pack()
        self.port_entry = tk.Entry(self.root)
        self.port_entry.insert(0, "9999")
        self.port_entry.pack(pady=5)

        tk.Button(self.root, text="Start Hosting", command=self.start_hosting).pack(pady=10)

    def start_hosting(self):
        port_str = self.port_entry.get().strip()
        if not port_str.isdigit():
            messagebox.showerror("Error", "Please enter a valid port number")
            return

        self.port = int(port_str)
        self.clear_window()

        ip = socket.gethostbyname(socket.gethostname())
        tk.Label(self.root, text="Waiting for client to connect...", font=("Arial", 14)).pack(pady=10)
        tk.Label(self.root, text=f"Your IP: {ip}\nPort: {self.port}", font=("Arial", 12)).pack(pady=5)

        threading.Thread(target=self.wait_for_client, daemon=True).start()

    def wait_for_client(self):
        try:
            self.sock, self.chat_key = chat.start_peer_gui(is_server=True, port=self.port)
            self.root.after(0, self.init_chat_page)
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Hosting Error", str(e)))

    def join_room(self):
        self.clear_window()
        tk.Label(self.root, text="Enter Server IP:").pack()
        self.ip_entry = tk.Entry(self.root)
        self.ip_entry.pack(pady=5)

        tk.Label(self.root, text="Enter Port:").pack()
        self.join_port_entry = tk.Entry(self.root)
        self.join_port_entry.insert(0, "9999")
        self.join_port_entry.pack(pady=5)

        tk.Button(self.root, text="Connect", command=self.connect_to_server).pack(pady=5)

    def connect_to_server(self):
        ip = self.ip_entry.get().strip()
        port_str = self.join_port_entry.get().strip()

        if not ip or not port_str.isdigit():
            messagebox.showerror("Error", "Please enter valid IP and port")
            return

        port = int(port_str)
        try:
            self.sock, self.chat_key = chat.start_peer_gui(is_server=False, ip=ip, port=port)
            self.init_chat_page()
        except Exception as e:
            messagebox.showerror("Connection Failed", str(e))

    def init_chat_page(self):
        self.clear_window()
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        frame = tk.Frame(self.root)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        self.text_area = scrolledtext.ScrolledText(frame, state='disabled', wrap='word')
        self.text_area.grid(row=0, column=0, columnspan=3, sticky="nsew", padx=10, pady=10)

        self.entry = tk.Entry(frame)
        self.entry.grid(row=1, column=0, sticky="ew", padx=(10, 5), pady=10)
        frame.columnconfigure(0, weight=1)

        send_btn = tk.Button(frame, text="Send", command=self.send_message)
        send_btn.grid(row=1, column=1, sticky="ew", padx=(5, 5), pady=10)

        exit_btn = tk.Button(frame, text="Exit", command=self.exit_chat)
        exit_btn.grid(row=1, column=2, sticky="ew", padx=(5, 10), pady=10)

        threading.Thread(target=self.receive_messages, daemon=True).start()

    def exit_chat(self):
        try:
            if self.sock:
                self.sock.close()
        except Exception as e:
            print(f"Error closing socket: {e}")
        self.root.destroy()

    def send_message(self):
        msg = self.entry.get()
        if msg:
            try:
                chat.send_encrypted(self.sock, msg, self.chat_key)
                self.display_message("You", msg)
                self.entry.delete(0, tk.END)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to send: {e}")

    def receive_messages(self):
        while True:
            try:
                msg = chat.receive_encrypted(self.sock, self.chat_key)
                if msg:
                    self.display_message("Peer", msg)
            except Exception:
                break

    def display_message(self, sender, msg):
        self.text_area.config(state='normal')
        self.text_area.insert(tk.END, f"{sender}: {msg}\n")
        self.text_area.config(state='disabled')
        self.text_area.yview(tk.END)

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = ChatApp(root)
    root.mainloop()
