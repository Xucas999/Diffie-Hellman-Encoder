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
        self.sidebar = None
        self.secret = None
        self.shared_secret = None
        self.encrypted_log = []
        self.sidebar_visible = False

        self.init_welcome_page()

    def init_welcome_page(self):
        self.clear_window()
        tk.Label(self.root, text="Welcome to Secure Chat", font=("Arial", 16)).pack(pady=10)

        tk.Label(self.root, text="Enter your name:").pack()
        self.name_entry = tk.Entry(self.root)
        self.name_entry.pack(pady=5)


        tk.Button(self.root, text="Host Room", command=self.host_room).pack(pady=5)
        tk.Button(self.root, text="Join Room", command=self.join_room).pack(pady=5)

    def host_room(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Missing Name", "Please enter your name.")
            return
        self.username = name
        self.clear_window()
        tk.Label(self.root, text="Host a Room", font=("Arial", 14)).pack(pady=10)

        tk.Label(self.root, text="Enter Port to Host On:").pack()
        self.port_entry = tk.Entry(self.root)
        self.port_entry.insert(0, "9999")
        self.port_entry.pack(pady=5)

        tk.Button(self.root, text="Start Hosting", command=self.start_hosting).pack(pady=10)
        tk.Button(self.root, text="Back", command=self.init_welcome_page).pack(pady=5)

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

        tk.Button(self.root, text="Back", command=self.init_welcome_page).pack(pady=10)

        threading.Thread(target=self.wait_for_client, daemon=True).start()

    def wait_for_client(self):
        def approve(username, addr):
            return messagebox.askyesno(
                "Connection Request",
                f"{username} wants to join from {addr[0]}.\nDo you want to accept?"
            )

        try:
            result = chat.start_peer_gui(
                is_server=True,
                ip="localhost",
                port=self.port,
                username=self.username,
                approval_callback=approve
            )

            if result[0] is None:
                self.root.after(0, lambda: messagebox.showinfo("Connection Denied", "You denied the client request."))
                self.root.after(0, self.init_welcome_page)
                return

            self.sock, self.chat_key, self.secret, self.shared_secret, self.peer_username = result
            self.root.after(0, self.init_chat_page)

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Hosting Error", str(e)))

    def join_room(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Missing Name", "Please enter your name.")
            return
        self.username = name
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
            self.sock, self.chat_key, self.secret, self.shared_secret, self.peer_username = chat.start_peer_gui(is_server=False, ip=ip, port=port, username=self.username)
            self.init_chat_page()
        except Exception as e:
            messagebox.showerror("Connection Failed", str(e))

    def init_chat_page(self):
        self.clear_window()
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        # Main frame for chat
        frame = tk.Frame(self.root)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        tk.Label(frame, text=f"Connected with: {self.peer_username}", font=("Arial", 12)).grid(
            row=0, column=0, columnspan=3, sticky="ew", padx=10
        )

        # Text display area
        self.text_area = scrolledtext.ScrolledText(frame, state='disabled', wrap='word')
        self.text_area.grid(row=0, column=0, columnspan=3, sticky="nsew", padx=10, pady=10)

        # Message entry
        self.entry = tk.Entry(frame)
        self.entry.grid(row=1, column=0, sticky="ew", padx=(10, 5), pady=10)
        frame.columnconfigure(0, weight=1)

        # Send button
        send_btn = tk.Button(frame, text="Send", command=self.send_message)
        send_btn.grid(row=1, column=1, sticky="ew", padx=(5, 5), pady=10)

        # Exit button
        exit_btn = tk.Button(frame, text="Exit", command=self.exit_chat)
        exit_btn.grid(row=1, column=2, sticky="ew", padx=(5, 10), pady=10)

        # Toggle Encryption Info Sidebar
        sidebar_btn = tk.Button(frame, text="Encryption Info", command=self.toggle_sidebar)
        sidebar_btn.grid(row=2, column=0, columnspan=3, pady=(0, 10))

        # Sidebar initial setup (hidden to the right)
        self.sidebar_visible = False
        self.sidebar_width = 250
        self.sidebar = tk.Frame(self.root, width=self.sidebar_width, bg="lightgray", height=self.root.winfo_height())
        self.sidebar.place(x=self.root.winfo_width(), y=0, height=self.root.winfo_height())

        self.root.bind("<Configure>", lambda e: self.sidebar.place_configure(height=self.root.winfo_height()))

        # Message log (optional encrypted log list)
        self.encrypted_log = []

        # Start receiving messages
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
                encrypted = chat.send_encrypted(self.sock, msg, self.chat_key, return_encrypted=True)
                self.encrypted_log.append(f"{self.username} → {encrypted.hex()}")
                self.display_message(self.username, msg)
                self.entry.delete(0, tk.END)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to send: {e}")

    def receive_messages(self):
        while True:
            try:
                encrypted, decrypted = chat.receive_encrypted(self.sock, self.chat_key, return_encrypted=True)
                self.encrypted_log.append(f"{self.peer_username} → {encrypted.hex()}")
                if decrypted:
                    self.display_message(self.peer_username, decrypted)
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

    def toggle_sidebar(self):
        if self.sidebar_visible:
            self.animate_sidebar(closing=True)
        else:
            self.populate_sidebar()
            self.animate_sidebar(closing=False)

    def animate_sidebar(self, closing=False):
        current_x = self.sidebar.winfo_x()
        target_x = self.root.winfo_width() if closing else self.root.winfo_width() - self.sidebar_width
        step = 20 if not closing else -20

        def slide():
            nonlocal current_x
            current_x += step
            if (not closing and current_x <= target_x) or (closing and current_x >= target_x):
                self.sidebar.place(x=current_x, y=0)
                self.root.after(10, slide)
            else:
                self.sidebar.place(x=target_x, y=0)
                self.sidebar_visible = not closing
                if closing:
                    self.sidebar.place_forget()

        slide()

    def populate_sidebar(self):
        for widget in self.sidebar.winfo_children():
            widget.destroy()

        tk.Label(self.sidebar, text="Encryption Info", font=("Arial", 12, "bold"), bg="lightgray").pack(pady=10)
        tk.Label(self.sidebar, text="⚠ DO NOT SHARE THIS INFORMATION", fg="red", font=("Arial", 8, "bold")).pack(pady=(10, 5))

        if hasattr(self, "secret"):
            tk.Label(self.sidebar, text=f"Secret Number:\n{self.secret}", bg="lightgray", anchor="w", justify="left", wraplength=180).pack(pady=5)

        if hasattr(self, "shared_secret"):
            tk.Label(self.sidebar, text=f"Shared Secret:\n{self.shared_secret}", bg="lightgray", anchor="w", justify="left", wraplength=180).pack(pady=5)

        if hasattr(self, "encrypted_log") and self.encrypted_log:
            tk.Label(self.sidebar, text="Encrypted Messages:", bg="lightgray").pack(pady=5)
            log_box = scrolledtext.ScrolledText(self.sidebar, width=25, height=10, state='normal', wrap='word')
            log_box.pack(padx=10, pady=5)
            for enc in self.encrypted_log:
                log_box.insert(tk.END, enc + '\n')
            log_box.config(state='disabled')

        # Add Back button
        tk.Button(self.sidebar, text="Back", command=self.toggle_sidebar).pack(pady=10)

    

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatApp(root)
    root.mainloop()
