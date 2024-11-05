import threading
import queue
from datetime import datetime
from server.data_manager import DataManager

class EmailManager:
    def __init__(self):
        self.data_manager = DataManager()
        self.email_queue = queue.Queue(maxsize=5)
        self.lock = threading.Lock()
        self.start_consumers()
        
    def start_consumers(self):
        for _ in range(2):  # Start 2 consumer threads
            thread = threading.Thread(target=self.process_queue)
            thread.daemon = True  # Exit when main program exits
            thread.start()
    
    def process_queue(self):
        while True:
            task = self.email_queue.get()
            if task is None:  # Exit signal
                break
            action, *args = task
            if action == "send_email":
                self.save_email(*args)
            elif action == "move_to_trash":
                self.move_to_trash(*args)
            self.email_queue.task_done()
    
    def save_email(self, email_data):
        with self.lock:  # Ensure thread-safe access to emails
            emails = self.data_manager.load_data(self.data_manager.emails_file) or {}
            
            # Initialize user entries if they don't exist
            if email_data['sender'] not in emails:
                emails[email_data['sender']] = []
            if email_data['recipient'] not in emails:
                emails[email_data['recipient']] = []
            
            # Create sent copy for sender
            sent_copy = email_data.copy()
            sent_copy['status'] = 'sent'
            emails[email_data['sender']].append(sent_copy)
            
            # Create inbox copy for recipient
            inbox_copy = email_data.copy()
            inbox_copy['status'] = 'inbox'
            emails[email_data['recipient']].append(inbox_copy)
            
            # Save updates
            self.data_manager.save_data(self.data_manager.emails_file, emails)
    
    def get_user_emails(self, username, folder=None):
        """
        Get emails for a user based on folder type
        
        Args:
            username (str): The user's username
            folder (str): One of 'inbox', 'sent', 'deleted', or None for all emails
            
        Returns:
            list: List of email dictionaries matching the criteria
        """
        emails = self.data_manager.load_data(self.data_manager.emails_file) or {}
        user_emails = emails.get(username, [])
        
        if folder:
            filtered_emails = [
                email for email in user_emails 
                if email['status'] == folder
            ]
            # Sort by timestamp, newest first
            return sorted(
                filtered_emails,
                key=lambda x: datetime.fromisoformat(x['timestamp']),
                reverse=True
            )
        return user_emails
    
    def move_to_trash(self, username, email_id):
        """
        Move an email to trash for a specific user
        
        Args:
            username (str): The user's username
            email_id (str): The ID of the email to move to trash
            
        Returns:
            bool: True if successful, False if email not found
        """
        with self.lock:  # Ensure thread-safe access to emails
            emails = self.data_manager.load_data(self.data_manager.emails_file) or {}
            user_emails = emails.get(username, [])
            
            for email in user_emails:
                if email['id'] == email_id:
                    email['status'] = 'deleted'
                    self.data_manager.save_data(self.data_manager.emails_file, emails)
                    return True
            return False
    
    def get_unread_count(self, username):
        """
        Get count of unread emails in user's inbox
        
        Args:
            username (str): The user's username
            
        Returns:
            int: Number of unread emails
        """
        emails = self.data_manager.load_data(self.data_manager.emails_file) or {}
        user_emails = emails.get(username, [])
        
        return len([
            email for email in user_emails 
            if email['status'] == 'inbox' and not email.get('read', False)
        ])
    
    def mark_as_read(self, username, email_id):
        """
        Mark an email as read
        
        Args:
            username (str): The user's username
            email_id (str): The ID of the email to mark as read
            
        Returns:
            bool: True if successful, False if email not found
        """
        with self.lock:
            emails = self.data_manager.load_data(self.data_manager.emails_file) or {}
            user_emails = emails.get(username, [])
            
            for email in user_emails:
                if email['id'] == email_id:
                    email['read'] = True
                    self.data_manager.save_data(self.data_manager.emails_file, emails)
                    return True
            return False
        
    def save_draft(self, email_data):
        """Save email as draft with a limit on the number of drafts"""
        with self.lock:
            emails = self.data_manager.load_data(self.data_manager.emails_file) or {}

        if email_data['sender'] not in emails:
            emails[email_data['sender']] = []
        
        # Limit the number of drafts to 10
        max_drafts = 3
        drafts = [email for email in emails[email_data['sender']] if email['status'] == 'draft']
        
        if len(drafts) >= max_drafts:
            # Optionally, delete the oldest draft or show an error message
            # For example, remove the oldest draft:
            oldest_draft = min(drafts, key=lambda x: datetime.fromisoformat(x['timestamp']))
            emails[email_data['sender']].remove(oldest_draft)

        # Set status as draft
        email_data['status'] = 'draft'
        emails[email_data['sender']].append(email_data)

        self.data_manager.save_data(self.data_manager.emails_file, emails)
        return True

    
    def delete_draft(self, username, email_id):
        """Delete a draft email"""
        with self.lock:
            emails = self.data_manager.load_data(self.data_manager.emails_file) or {}
            user_emails = emails.get(username, [])
            
            emails[username] = [
                email for email in user_emails 
                if not (email['id'] == email_id and email['status'] == 'draft')
            ]
            
            self.data_manager.save_data(self.data_manager.emails_file, emails)
            return True