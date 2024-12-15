import threading
import queue
from datetime import datetime
from server.data_manager import DataManager


class EmailManager:
    def __init__(self):
        try:
            self.data_manager = DataManager()
            self.email_queue = queue.Queue(maxsize=5)
            self.lock = threading.Lock()
            self.start_consumers()
        except Exception as e:
            print(f"Error initializing EmailManager: {e}")

    def start_consumers(self):
        try:
            for _ in range(2):  # Start 2 consumer threads
                thread = threading.Thread(target=self.process_queue)
                thread.daemon = True  # Exit when main program exits
                thread.start()
        except Exception as e:
            print(f"Error starting consumer threads: {e}")

    def process_queue(self):
        while True:
            try:
                task = self.email_queue.get(timeout=10)  # Wait for a task for 10 seconds
                if task is None:  # Exit signal
                    break
                action, *args = task
                if action == "send_email":
                    self.save_email(*args)
                elif action == "move_to_trash":
                    self.move_to_trash(*args)
                elif action == "save_draft":
                    self.save_draft(*args)
                self.email_queue.task_done()
            except queue.Empty:
                print("Queue is empty. Waiting for tasks.")
            except Exception as e:
                print(f"Error processing queue task: {e}")

    def save_email(self, email_data):
        try:
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
        except Exception as e:
            print(f"Error saving email: {e}")

    def get_user_emails(self, username, folder=None):
        try:
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
        except Exception as e:
            print(f"Error retrieving emails for {username}: {e}")
            return []

    def move_to_trash(self, username, email_id):
        try:
            with self.lock:  # Ensure thread-safe access to emails
                emails = self.data_manager.load_data(self.data_manager.emails_file) or {}
                user_emails = emails.get(username, [])

                for email in user_emails:
                    if email['id'] == email_id:
                        email['status'] = 'deleted'
                        self.data_manager.save_data(self.data_manager.emails_file, emails)
                        return True
                return False
        except Exception as e:
            print(f"Error moving email to trash for {username}: {e}")
            return False

    def get_unread_count(self, username):
        try:
            emails = self.data_manager.load_data(self.data_manager.emails_file) or {}
            user_emails = emails.get(username, [])

            return len([
                email for email in user_emails
                if email['status'] == 'inbox' and not email.get('read', False)
            ])
        except Exception as e:
            print(f"Error getting unread count for {username}: {e}")
            return 0

    def mark_as_read(self, username, email_id):
        try:
            with self.lock:
                emails = self.data_manager.load_data(self.data_manager.emails_file) or {}
                user_emails = emails.get(username, [])

                for email in user_emails:
                    if email['id'] == email_id:
                        email['read'] = True
                        self.data_manager.save_data(self.data_manager.emails_file, emails)
                        return True
                return False
        except Exception as e:
            print(f"Error marking email as read for {username}: {e}")
            return False

    def save_draft(self, email_data):
        try:
            with self.lock:
                emails = self.data_manager.load_data(self.data_manager.emails_file) or {}

            if email_data['sender'] not in emails:
                emails[email_data['sender']] = []

            # Limit the number of drafts to 3
            max_drafts = 3
            drafts = [email for email in emails[email_data['sender']] if email['status'] == 'draft']

            if len(drafts) >= max_drafts:
                # Optionally, delete the oldest draft or show an error message
                oldest_draft = min(drafts, key=lambda x: datetime.fromisoformat(x['timestamp']))
                emails[email_data['sender']].remove(oldest_draft)

            # Set status as draft
            email_data['status'] = 'draft'
            emails[email_data['sender']].append(email_data)

            self.data_manager.save_data(self.data_manager.emails_file, emails)
            return True
        except Exception as e:
            print(f"Error saving draft: {e}")
            return False

    def delete_draft(self, username, email_id):
        try:
            with self.lock:
                emails = self.data_manager.load_data(self.data_manager.emails_file) or {}
                user_emails = emails.get(username, [])

                emails[username] = [
                    email for email in user_emails
                    if not (email['id'] == email_id and email['status'] == 'draft')
                ]

                self.data_manager.save_data(self.data_manager.emails_file, emails)
                return True
        except Exception as e:
            print(f"Error deleting draft for {username}: {e}")
            return False
