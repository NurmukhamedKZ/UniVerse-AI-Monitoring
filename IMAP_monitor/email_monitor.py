import imaplib
import email
from email.header import decode_header
import time
from datetime import datetime
from typing import Dict, List

class OutlookEmailMonitor:
    def __init__(self, email_address, password):
        """
        Initialize the email monitor
        
        Args:
            email_address: Your KBTU email (e.g., username@example.kbtu.kz)
            password: Your email password
        """
        self.email_address = email_address
        self.password = password
        self.imap_server = "outlook.office365.com"  # Standard Outlook IMAP server
        self.imap_port = 993
        self.connection = None
        
    def connect(self):
        """Connect to the IMAP server"""
        try:
            print(f"Connecting to {self.imap_server}...")
            self.connection = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            self.connection.login(self.email_address, self.password)
            print("✓ Successfully connected!")
            return True
        except Exception as e:
            print(f"✗ Connection failed: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from the IMAP server"""
        if self.connection:
            self.connection.logout()
            print("Disconnected from server")
    
    def decode_subject(self, subject):
        """Decode email subject line"""
        decoded_parts = decode_header(subject)
        decoded_subject = ""
        for part, encoding in decoded_parts:
            if isinstance(part, bytes):
                decoded_subject += part.decode(encoding or 'utf-8', errors='ignore')
            else:
                decoded_subject += part
        return decoded_subject
    
    def fetch_unseen_emails(self) -> List[Dict]:
        """
        Fetch all unseen (unread) emails from inbox
        
        Returns:
            List of email dictionaries with parsed information
        """
        try:
            # Select the inbox
            self.connection.select("INBOX")
            
            # Search for unseen emails
            status, messages = self.connection.search(None, 'UNSEEN')
            
            if status != "OK":
                print("Error searching for emails")
                return []
            
            email_ids = messages[0].split()
            
            if not email_ids:
                print("No new unseen emails")
                return []
            
            print(f"Found {len(email_ids)} unseen email(s)")
            
            emails = []
            
            for email_id in email_ids:
                # Fetch the email
                status, msg_data = self.connection.fetch(email_id, '(RFC822)')
                
                if status != "OK":
                    continue
                
                # Parse the email
                raw_email = msg_data[0][1]
                email_message = email.message_from_bytes(raw_email)
                
                # Extract email details
                subject = self.decode_subject(email_message.get("Subject", ""))
                from_address = email_message.get("From", "")
                date = email_message.get("Date", "")
                
                # Extract email body
                body = self.get_email_body(email_message)
                
                email_data = {
                    "id": email_id.decode(),
                    "subject": subject,
                    "from": from_address,
                    "date": date,
                    "body": body
                }
                
                emails.append(email_data)
                
                print(f"\n--- Email {email_id.decode()} ---")
                print(f"From: {from_address}")
                print(f"Subject: {subject}")
                print(f"Date: {date}")
                print(f"Body preview: {body[:100]}...")
            
            return emails
            
        except Exception as e:
            print(f"Error fetching emails: {e}")
            return []
    
    def get_email_body(self, email_message):
        """Extract email body text"""
        body = ""
        
        if email_message.is_multipart():
            # Handle multipart emails
            for part in email_message.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                
                # Look for plain text or HTML content
                if content_type == "text/plain" and "attachment" not in content_disposition:
                    try:
                        body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        break
                    except:
                        pass
                elif content_type == "text/html" and not body and "attachment" not in content_disposition:
                    try:
                        body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    except:
                        pass
        else:
            # Handle simple emails
            try:
                body = email_message.get_payload(decode=True).decode('utf-8', errors='ignore')
            except:
                body = str(email_message.get_payload())
        
        return body
    
    def monitor_continuous(self, check_interval=60):
        """
        Continuously monitor for new emails
        
        Args:
            check_interval: Seconds between checks (default: 60)
        """
        print(f"\nStarting continuous monitoring (checking every {check_interval} seconds)")
        print("Press Ctrl+C to stop\n")
        
        try:
            while True:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Checking for new emails...")
                
                emails = self.fetch_unseen_emails()
                
                if emails:
                    # Here you would send emails to your AI agent
                    print(f"\n✓ Retrieved {len(emails)} new email(s)")
                    print("TODO: Send to AI agent for analysis")
                    # self.send_to_ai_agent(emails)
                
                print(f"Waiting {check_interval} seconds until next check...\n")
                time.sleep(check_interval)
                
        except KeyboardInterrupt:
            print("\n\nMonitoring stopped by user")
            self.disconnect()


def send_to_ai_agent(emails):
    """
    Placeholder function to send emails to your AI agent
    
    Args:
        emails: List of email dictionaries
    """
    # TODO: Implement your AI agent integration here
    # This could be:
    # - API call to Claude/GPT
    # - Call to local AI model
    # - Queue for processing
    # - Database storage
    
    for email_data in emails:
        print(f"\n--- Processing with AI ---")
        print(f"Subject: {email_data['subject']}")
        print(f"From: {email_data['from']}")
        # Your AI processing logic here
        pass


# Example usage
if __name__ == "__main__":
    # Replace with your KBTU credentials
    EMAIL = "n_ashekei@kbtu.kz"
    PASSWORD = "555999Www"
    
    # Create monitor instance
    monitor = OutlookEmailMonitor(EMAIL, PASSWORD)
    
    # Connect to server
    if monitor.connect():
        # Option 1: Fetch unseen emails once
        # emails = monitor.fetch_unseen_emails()
        # send_to_ai_agent(emails)
        # monitor.disconnect()
        
        # Option 2: Continuous monitoring
        monitor.monitor_continuous(check_interval=60)  # Check every 60 seconds
