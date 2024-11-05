import tkinter as tk
from tkinter import messagebox, ttk
import uuid
from datetime import datetime
import sys,os

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if base_dir not in sys.path:
    sys.path.append(base_dir)

from server.auth_manager import AuthManager
from server.email_manager import EmailManager

class ModernEmailClient(tk.Tk):
    def __init__(self):
        super().__init__()
        
        # Initialize managers
        self.auth_manager = AuthManager()
        self.email_manager = EmailManager()
        
        # Setup window
        self.title("Modern Email")
        self.geometry("1000x700")
        
        # Color scheme
        self.colors = {
            'bg': '#f0f4f8',
            'primary': '#2b6cb0',
            'secondary': '#4299e1',
            'accent': '#63b3ed',
            'text': '#2d3748',
            'text_light': '#718096',
            'white': '#ffffff',
            'border': '#e2e8f0',
            'error': '#fc8181',
            'success': '#68d391'
        }
        
        self.configure(bg=self.colors['bg'])
        
        # Initialize state
        self.current_user = None
        
        # Configure styles
        self.setup_styles()
        
        # Start with login screen
        self.show_login_screen()
        
        self.current_draft = None
    
    def setup_styles(self):
        # Configure ttk styles
        style = ttk.Style()
        style.configure('Modern.TEntry',
            fieldbackground=self.colors['white'],
            borderwidth=0,
            relief='flat',
            padding=10
        )
        
        style.configure('Modern.TButton',
            background=self.colors['primary'],
            foreground=self.colors['white'],
            padding=(20, 10),
            font=('Helvetica', 11)
        )
        
    def create_modern_entry(self, parent, placeholder):
        frame = tk.Frame(parent, bg=self.colors['white'], padx=2, pady=2)
        frame.pack(fill=tk.X, pady=8)
        
        entry = ttk.Entry(
            frame,
            style='Modern.TEntry',
            font=('Helvetica', 11)
        )
        entry.pack(fill=tk.X, expand=True)
        
        entry.insert(0, placeholder)
        entry.bind('<FocusIn>', lambda e: self.on_entry_click(entry, placeholder))
        entry.bind('<FocusOut>', lambda e: self.on_focus_out(entry, placeholder))
        
        return entry
    
    def on_entry_click(self, entry, placeholder):
        if entry.get() == placeholder:
            entry.delete(0, tk.END)
    
    def on_focus_out(self, entry, placeholder):
        if entry.get() == '':
            entry.insert(0, placeholder)
    
    def show_login_screen(self):
        self.clear_window()
        
        # Main container with padding
        container = tk.Frame(self, bg=self.colors['bg'], padx=40, pady=40)
        container.pack(expand=True, fill=tk.BOTH)
        
        # Login box
        login_frame = tk.Frame(
            container,
            bg=self.colors['white'],
            padx=40,
            pady=40,
        )
        login_frame.place(relx=0.5, rely=0.5, anchor='center', relwidth=0.4)
        
        # Add subtle shadow effect
        shadow_frame = tk.Frame(
            container,
            bg=self.colors['text_light'],
            padx=40,
            pady=40,
        )
        shadow_frame.place(relx=0.502, rely=0.503, anchor='center', relwidth=0.4)
        login_frame.lift()
        
        # Title
        tk.Label(
            login_frame,
            text="Welcome Back",
            font=('Helvetica', 24, 'bold'),
            bg=self.colors['white'],
            fg=self.colors['text']
        ).pack(pady=(0, 10))
        
        tk.Label(
            login_frame,
            text="Sign in to continue",
            font=('Helvetica', 12),
            bg=self.colors['white'],
            fg=self.colors['text_light']
        ).pack(pady=(0, 30))
        
        # Entries
        self.username_entry = self.create_modern_entry(login_frame, "Username")
        self.password_entry = self.create_modern_entry(login_frame, "Password")
        self.password_entry.configure(show="●")
        
        # Buttons
        button_frame = tk.Frame(login_frame, bg=self.colors['white'])
        button_frame.pack(pady=(20, 0), fill=tk.X)
        
        ttk.Button(
            button_frame,
            text="Sign In",
            style='Modern.TButton',
            command=self.login
        ).pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(
            button_frame,
            text="Create Account",
            style='Modern.TButton',
            command=self.register
        ).pack(fill=tk.X)
    
    def show_main_screen(self):
        self.clear_window()
        
        # Create main container
        main_container = tk.Frame(self, bg=self.colors['bg'])
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Sidebar
        sidebar = tk.Frame(main_container, bg=self.colors['white'], width=200)
        sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 2))
        sidebar.pack_propagate(False)
        
        # Compose button
        ttk.Button(
            sidebar,
            text="✏️ Compose",
            style='Modern.TButton',
            command=self.show_compose
        ).pack(fill=tk.X, padx=10, pady=20)
        
        # Folder buttons
        folders = [
            ("Inbox", "inbox"),
            ("Sent", "sent"),
            ("Drafts", "draft"),
            ("Trash", "deleted"),
        ]
        
        for text, folder in folders:
            tk.Button(
                sidebar,
                text=text,
                command=lambda f=folder: self.show_folder(f),
                font=('Helvetica', 11),
                bg=self.colors['white'],
                fg=self.colors['text'],
                bd=0,
                pady=12,
                padx=20,
                anchor='w',
                activebackground=self.colors['accent'],
                activeforeground=self.colors['white']
            ).pack(fill=tk.X)
        
        # Logout button at bottom of sidebar
        tk.Button(
            sidebar,
            text="Logout",
            command=self.logout,
            font=('Helvetica', 11),
            bg=self.colors['white'],
            fg=self.colors['text_light'],
            bd=0,
            pady=12,
            padx=20,
            anchor='w'
        ).pack(fill=tk.X, side=tk.BOTTOM)
        
        # Content area
        self.content_frame = tk.Frame(main_container, bg=self.colors['bg'])
        self.content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Show inbox by default
        self.show_folder("inbox")
    
    def show_compose(self, draft_data=None):
        self.clear_content()
        
        compose_frame = tk.Frame(self.content_frame, bg=self.colors['white'], padx=30, pady=30)
        compose_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        tk.Label(
            compose_frame,
            text="New Message" if not draft_data else "Edit Draft",
            font=('Helvetica', 20, 'bold'),
            bg=self.colors['white'],
            fg=self.colors['text']
        ).pack(anchor='w', pady=(0, 20))
        
        # Recipients
        recipients_entry = self.create_modern_entry(compose_frame, "To:")
        
        # Subject
        subject_entry = self.create_modern_entry(compose_frame, "Subject:")
        
        # Body
        body_frame = tk.Frame(compose_frame, bg=self.colors['white'], padx=2, pady=2)
        body_frame.pack(fill=tk.BOTH, expand=True, pady=8)
        
        body_text = tk.Text(
            body_frame,
            font=('Helvetica', 11),
            wrap=tk.WORD,
            bd=0,
            padx=10,
            pady=10
        )
        body_text.pack(fill=tk.BOTH, expand=True)
        
        # Fill in draft data if editing a draft
        if draft_data:
            self.current_draft = draft_data['id']
            recipients_entry.delete(0, tk.END)
            recipients_entry.insert(0, draft_data['recipient'])
            
            subject_entry.delete(0, tk.END)
            subject_entry.insert(0, draft_data['subject'])
            
            body_text.delete("1.0", tk.END)
            body_text.insert("1.0", draft_data['body'])
        else:
            self.current_draft = None
        
        # Button frame
        button_frame = tk.Frame(compose_frame, bg=self.colors['white'])
        button_frame.pack(pady=(20, 0), fill=tk.X)
        
        # Save Draft button
        ttk.Button(
            button_frame,
            text="Save as Draft",
            style='Modern.TButton',
            command=lambda: self.save_draft(
                recipients_entry.get(),
                subject_entry.get(),
                body_text.get("1.0", tk.END)
            )
        ).pack(side=tk.LEFT, padx=5)
        
        # Send button
        ttk.Button(
            button_frame,
            text="Send Message",
            style='Modern.TButton',
            command=lambda: self.send_email(
                recipients_entry.get(),
                subject_entry.get(),
                body_text.get("1.0", tk.END)
            )
        ).pack(side=tk.LEFT, padx=5)
    
    def save_draft(self, recipient, subject, body):
        email_data = {
            'id': str(uuid.uuid4()) if not self.current_draft else self.current_draft,
            'sender': self.current_user,
            'recipient': recipient,
            'subject': subject,
            'body': body,
            'timestamp': datetime.now().isoformat(),
            'status': 'draft'
        }
        
        if self.email_manager.save_draft(email_data):
            messagebox.showinfo("Success", "Draft saved successfully!")
            self.show_folder("draft")
        else:
            messagebox.showerror("Error", "Failed to save draft.")
    
    def show_folder(self, folder):
        self.clear_content()
        
        folder_frame = tk.Frame(self.content_frame, bg=self.colors['bg'])
        folder_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title with folder icon
        folder_icons = {
            "inbox": "📥",
            "sent": "📤",
            "draft": "📝",
            "deleted": "🗑️"
        }
        
        title = f"{folder_icons.get(folder, '')} {folder.title()}"
        tk.Label(
            folder_frame,
            text=title,
            font=('Helvetica', 20, 'bold'),
            bg=self.colors['bg'],
            fg=self.colors['text']
        ).pack(anchor='w', pady=(0, 20))
        
        # Get emails
        emails = self.email_manager.get_user_emails(self.current_user, folder)
        
        if not emails:
            # Show empty state message
            tk.Label(
                folder_frame,
                text=f"No emails in {folder}",
                font=('Helvetica', 12),
                bg=self.colors['bg'],
                fg=self.colors['text_light']
            ).pack(pady=20)
            return
        
        # Email list
        for email in emails:
            email_card = tk.Frame(
                folder_frame,
                bg=self.colors['white'],
                padx=20,
                pady=15
            )
            email_card.pack(fill=tk.X, pady=5)
            
            # Sender/Subject
            tk.Label(
                email_card,
                text=email['sender'],
                font=('Helvetica', 12, 'bold'),
                bg=self.colors['white'],
                fg=self.colors['text']
            ).pack(anchor='w')
            
            tk.Label(
                email_card,
                text=email['subject'],
                font=('Helvetica', 11),
                bg=self.colors['white'],
                fg=self.colors['text_light']
            ).pack(anchor='w')
            
            # Action buttons
            button_frame = tk.Frame(email_card, bg=self.colors['white'])
            button_frame.pack(side=tk.RIGHT)
            
            if folder == "draft":
                # Edit button for drafts
                tk.Button(
                    button_frame,
                    text="Edit",
                    command=lambda e=email: self.show_compose(e),
                    font=('Helvetica', 11),
                    bg=self.colors['white'],
                    fg=self.colors['primary'],
                    bd=0,
                    padx=10
                ).pack(side=tk.RIGHT)
            
            # Delete button
            tk.Button(
                button_frame,
                text="Delete",
                command=lambda eid=email['id']: (
                    self.email_manager.delete_draft(self.current_user, eid)
                    if folder == "draft"
                    else self.delete_email(eid)
                ),
                font=('Helvetica', 11),
                bg=self.colors['white'],
                fg=self.colors['text_light'],
                bd=0,
                padx=10
            ).pack(side=tk.RIGHT)
        
    def clear_window(self):
        for widget in self.winfo_children():
            widget.destroy()
        
    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
    def send_email(self, recipient, subject, body):
        if not recipient or not subject or not body:
            messagebox.showerror("Error", "All fields are required.")
            return
        
        email_data = {
            'id': str(uuid.uuid4()),
            'sender': self.current_user,
            'recipient': recipient,
            'subject': subject,
            'body': body,
            'timestamp': datetime.now().isoformat(),
            'status': 'sent'
        }
        
        self.email_manager.email_queue.put(("send_email", email_data))
        messagebox.showinfo("Success", "Email sent successfully!")
        
    def delete_email(self, email_id):
        if self.email_manager.move_to_trash(self.current_user, email_id):
            messagebox.showinfo("Success", "Email moved to trash.")
            self.show_folder("inbox")  # Refresh the inbox
        else:
            messagebox.showerror("Error", "Email not found.")
        
    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if self.auth_manager.login(username, password):
            self.current_user = username
            self.show_main_screen()
        else:
            messagebox.showerror("Error", "Invalid credentials.")
    
    def register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if self.auth_manager.register(username, password):
            messagebox.showinfo("Success", "Registration successful! Please log in.")
        else:
            messagebox.showerror("Error", "Username already exists.")

    def logout(self):
        self.current_user = None
        self.show_login_screen()

if __name__ == "__main__":
    app = ModernEmailClient()
    app.mainloop()
