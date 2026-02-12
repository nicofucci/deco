import tkinter as tk
from tkinter import messagebox, ttk
import threading
import logging
import sys
from modules.agent_id import AgentIdentity
from modules.secure_storage import SecureStorage
from agent_main import DecoAgent
from config import ORCHESTRATOR_URL

# Configure Logging to file only for GUI (to keep console clean if visible, though we use noconsole)
logging.basicConfig(filename='agent_gui.log', level=logging.INFO)
logger = logging.getLogger("AgentGUI")

class AgentGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Deco-Security Agent Setup")
        self.root.geometry("400x350")
        self.root.resizable(False, False)
        
        # Style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Header
        header_frame = tk.Frame(root, bg="#1e293b", height=60)
        header_frame.pack(fill=tk.X)
        tk.Label(header_frame, text="Deco-Security", font=("Helvetica", 16, "bold"), bg="#1e293b", fg="white").pack(pady=15)

        # Content
        content_frame = tk.Frame(root, padx=20, pady=20)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Server URL
        tk.Label(content_frame, text="Server URL:", font=("Helvetica", 10)).pack(anchor=tk.W, pady=(0, 5))
        self.url_entry = ttk.Entry(content_frame, width=40)
        self.url_entry.insert(0, ORCHESTRATOR_URL)
        self.url_entry.pack(fill=tk.X, pady=(0, 15))

        # API Key
        tk.Label(content_frame, text="Client API Key:", font=("Helvetica", 10)).pack(anchor=tk.W, pady=(0, 5))
        self.key_entry = ttk.Entry(content_frame, width=40, show="*")
        self.key_entry.pack(fill=tk.X, pady=(0, 15))

        # Status Label
        self.status_label = tk.Label(content_frame, text="Ready to connect", fg="gray")
        self.status_label.pack(pady=(0, 15))

        # Connect Button
        self.connect_btn = tk.Button(content_frame, text="Connect & Start Agent", command=self.connect, bg="#2563eb", fg="white", font=("Helvetica", 10, "bold"), padx=10, pady=5, relief=tk.FLAT)
        self.connect_btn.pack(fill=tk.X)

        # Storage
        self.storage = SecureStorage()
        
        # Pre-fill if exists
        saved_key = self.storage.get("client_api_key")
        if saved_key:
            self.key_entry.insert(0, saved_key)
            
        # Check if already registered
        if self.storage.get("agent_id"):
            self.status_label.config(text="Agent already registered", fg="green")
            self.connect_btn.config(text="Start Agent Service")

    def connect(self):
        api_key = self.key_entry.get().strip()
        server_url = self.url_entry.get().strip()

        if not api_key:
            messagebox.showerror("Error", "API Key is required")
            return

        if not server_url:
            messagebox.showerror("Error", "Server URL is required")
            return

        # Save Config
        self.storage.set("client_api_key", api_key)
        # We might need to update config.py dynamically or store URL in storage and have http_client read it
        # For now, let's assume http_client reads from config.py constants, which is hardcoded.
        # We need to modify http_client to read URL from storage if available.
        self.storage.set("orchestrator_url", server_url)

        self.status_label.config(text="Connecting...", fg="blue")
        self.connect_btn.config(state=tk.DISABLED)

        # Run registration in thread
        threading.Thread(target=self.perform_registration, daemon=True).start()

    def perform_registration(self):
        try:
            identity = AgentIdentity()
            # Force reload of URL from storage (we need to update http_client for this to work)
            # For this MVP, we will patch config at runtime or rely on http_client update
            
            if identity.register():
                self.root.after(0, self.on_success)
            else:
                self.root.after(0, lambda: self.on_failure("Registration failed. Check API Key and URL."))
        except Exception as e:
            self.root.after(0, lambda: self.on_failure(str(e)))

    def on_success(self):
        self.status_label.config(text="Connected! Agent Running...", fg="green")
        messagebox.showinfo("Success", "Agent registered and running successfully!\nYou can minimize this window.")
        
        # Start Agent Loop
        self.agent = DecoAgent()
        threading.Thread(target=self.agent.run, daemon=True).start()
        
        # Disable button
        self.connect_btn.config(text="Agent Running", state=tk.DISABLED)

    def on_failure(self, error_msg):
        self.status_label.config(text="Connection Failed", fg="red")
        self.connect_btn.config(state=tk.NORMAL)
        messagebox.showerror("Connection Error", error_msg)

if __name__ == "__main__":
    root = tk.Tk()
    app = AgentGUI(root)
    root.mainloop()
