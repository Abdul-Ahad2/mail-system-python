import pytest
import os
import sys
from pathlib import Path
from datetime import datetime
import uuid

# Add project root to Python path
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)

from server.email_manager import EmailManager
from server.data_manager import DataManager

class TestEmailManager:
    @pytest.fixture
    def email_manager(self):
        """Create a fresh EmailManager for each test"""
        # Create a temporary test data directory
        test_data_dir = Path(base_dir) / "tests" / "test_data"
        test_data_dir.mkdir(exist_ok=True)
        
        # Create test file paths
        test_emails_file = test_data_dir / "emails.json"
        
        # Patch DataManager to use test file
        data_manager = DataManager()
        data_manager.emails_file = test_emails_file
        
        # Clear any existing test data
        if test_emails_file.exists():
            os.remove(test_emails_file)
        
        # Create email manager with test data manager
        email_manager = EmailManager()
        email_manager.data_manager = data_manager
        
        yield email_manager
        
        # Cleanup
        if test_emails_file.exists():
            os.remove(test_emails_file)
    
    def create_test_email(self, sender="testuser", recipient="recipient"):
        """Helper method to create a test email"""
        return {
            'id': str(uuid.uuid4()),
            'sender': sender,
            'recipient': recipient,
            'subject': "Test Subject",
            'body': "Test Body",
            'timestamp': datetime.now().isoformat(),
            'status': 'sent'
        }
    
    def test_save_email(self, email_manager):
        """Test saving an email"""
        test_email = self.create_test_email()
        
        # Use queue mechanism to save email
        email_manager.email_queue.put(("send_email", test_email))
        
        # Process the queue
        email_manager.process_queue()
        

        
        # Retrieve emails for sender and recipient
        sender_emails = email_manager.get_user_emails(test_email['sender'])
        recipient_emails = email_manager.get_user_emails(test_email['recipient'])
        
        assert len(sender_emails) > 0, "Sender's sent emails should not be empty"
        assert len(recipient_emails) > 0, "Recipient's inbox should not be empty"
        
        # Check email details
        sender_email = sender_emails[0]
        recipient_email = recipient_emails[0]
        
        assert sender_email['subject'] == test_email['subject']
        assert recipient_email['subject'] == test_email['subject']
        assert sender_email['status'] == 'sent'
        assert recipient_email['status'] == 'inbox'
    
    def test_get_user_emails_by_folder(self, email_manager):
        """Test retrieving emails by folder"""
        # Create multiple emails with different statuses
        emails = [
            self.create_test_email(status='inbox'),
            self.create_test_email(status='sent'),
            self.create_test_email(status='draft'),
            self.create_test_email(status='deleted')
        ]
        
        # Save emails
        for email in emails:
            email_manager.email_queue.put(("send_email", email))
            email_manager.process_queue()
        
        # Check folder-specific retrievals
        inbox_emails = email_manager.get_user_emails("testuser", "inbox")
        sent_emails = email_manager.get_user_emails("testuser", "sent")
        draft_emails = email_manager.get_user_emails("testuser", "draft")
        deleted_emails = email_manager.get_user_emails("testuser", "deleted")
        
        assert len(inbox_emails) == 1, "Should have 1 inbox email"
        assert len(sent_emails) == 1, "Should have 1 sent email"
        assert len(draft_emails) == 1, "Should have 1 draft email"
        assert len(deleted_emails) == 1, "Should have 1 deleted email"
    
    def test_move_to_trash(self, email_manager):
        """Test moving an email to trash"""
        test_email = self.create_test_email()
        
        # Save email first
        email_manager.email_queue.put(("send_email", test_email))
        email_manager.process_queue()
        
        # Move to trash
        result = email_manager.move_to_trash(test_email['recipient'], test_email['id'])
        
        assert result is True, "Move to trash should succeed"
        
        # Check email status
        user_emails = email_manager.get_user_emails(test_email['recipient'], "deleted")
        assert len(user_emails) == 1, "Email should be in deleted folder"
    
    def test_unread_count(self, email_manager):
        """Test getting unread email count"""
        # Create multiple unread and read emails
        unread_emails = [
            self.create_test_email(recipient="testuser"),
            self.create_test_email(recipient="testuser")
        ]
        read_email = self.create_test_email(recipient="testuser")
        
        # Save emails
        for email in unread_emails + [read_email]:
            email_manager.email_queue.put(("send_email", email))
            email_manager.process_queue()
        
        # Mark one email as read
        email_manager.mark_as_read("testuser", read_email['id'])
        
        # Check unread count
        unread_count = email_manager.get_unread_count("testuser")
        assert unread_count == 2, "Unread count should be 2"
    
    def test_save_draft(self, email_manager):
        """Test saving a draft email"""
        draft_email = {
            'id': str(uuid.uuid4()),
            'sender': 'testuser',
            'recipient': 'recipient',
            'subject': 'Draft Subject',
            'body': 'Draft Body',
            'timestamp': datetime.now().isoformat(),
            'status': 'draft'
        }
        
        # Save draft
        result = email_manager.save_draft(draft_email)
        
        assert result is True, "Draft should be saved successfully"
        
        # Retrieve drafts
        drafts = email_manager.get_user_emails('testuser', 'draft')
        assert len(drafts) == 1, "Should have 1 draft"
        assert drafts[0]['subject'] == 'Draft Subject'
    
    def test_delete_draft(self, email_manager):
        """Test deleting a draft email"""
        draft_email = {
            'id': str(uuid.uuid4()),
            'sender': 'testuser',
            'recipient': 'recipient',
            'subject': 'Draft Subject',
            'body': 'Draft Body',
            'timestamp': datetime.now().isoformat(),
            'status': 'draft'
        }
        
        # Save draft
        email_manager.save_draft(draft_email)
        # Implement delete draft logic here
        # Example: email_manager.delete_draft(draft_email['id'])
