"""
Email Monitor using Microsoft Graph API
This works with Office 365 accounts that have Basic Auth blocked
"""

import requests
import json
from datetime import datetime
import webbrowser
from urllib.parse import urlencode, parse_qs

class GraphEmailMonitor:
    def __init__(self, client_id, tenant_id="common"):
        """
        Initialize Graph API email monitor
        
        Args:
            client_id: Your Azure AD application client ID
            tenant_id: Your tenant ID (default: "common" for multi-tenant)
        """
        self.client_id = client_id
        self.tenant_id = tenant_id
        self.access_token = None
        self.graph_endpoint = "https://graph.microsoft.com/v1.0"
        
        # Permissions needed: Mail.Read
        self.scopes = ["Mail.Read", "offline_access"]
    
    def get_auth_url(self):
        """Generate the authorization URL for user to visit"""
        auth_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/authorize"
        
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": "http://localhost:8080",
            "scope": " ".join(self.scopes),
            "response_mode": "query"
        }
        
        return f"{auth_url}?{urlencode(params)}"
    
    def authenticate_interactive(self):
        """
        Interactive authentication flow
        User will be directed to login via browser
        """
        print("\n=== Microsoft Authentication Required ===")
        print("\n1. Your browser will open with Microsoft login page")
        print("2. Sign in with your KBTU credentials")
        print("3. Grant permissions to read your emails")
        print("4. You'll be redirected to localhost - COPY THE ENTIRE URL from your browser")
        print("\nPress Enter to open browser...")
        input()
        
        auth_url = self.get_auth_url()
        webbrowser.open(auth_url)
        
        print("\nAfter signing in, paste the FULL redirect URL here:")
        redirect_response = input("URL: ").strip()
        
        # Extract authorization code from URL
        if "code=" in redirect_response:
            code = redirect_response.split("code=")[1].split("&")[0]
            return self.get_token_from_code(code)
        else:
            print("❌ No authorization code found in URL")
            return False
    
    def get_token_from_code(self, code):
        """Exchange authorization code for access token"""
        token_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        
        data = {
            "client_id": self.client_id,
            "scope": " ".join(self.scopes),
            "code": code,
            "redirect_uri": "http://localhost:8080",
            "grant_type": "authorization_code"
        }
        
        try:
            response = requests.post(token_url, data=data)
            response.raise_for_status()
            token_data = response.json()
            
            self.access_token = token_data.get("access_token")
            print("✅ Authentication successful!")
            return True
            
        except Exception as e:
            print(f"❌ Token exchange failed: {e}")
            if hasattr(e, 'response'):
                print(f"Response: {e.response.text}")
            return False
    
    def set_access_token(self, token):
        """Manually set access token if you already have one"""
        self.access_token = token
    
    def get_headers(self):
        """Get headers for API requests"""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    def fetch_unread_emails(self, max_emails=10):
        """
        Fetch unread emails from inbox
        
        Args:
            max_emails: Maximum number of emails to fetch
            
        Returns:
            List of email dictionaries
        """
        if not self.access_token:
            print("❌ Not authenticated. Call authenticate_interactive() first")
            return []
        
        # Graph API endpoint for messages
        url = f"{self.graph_endpoint}/me/messages"
        
        params = {
            "$filter": "isRead eq false",
            "$top": max_emails,
            "$select": "id,subject,from,receivedDateTime,bodyPreview,body,toRecipients",
            "$orderby": "receivedDateTime DESC"
        }
        
        try:
            response = requests.get(url, headers=self.get_headers(), params=params)
            response.raise_for_status()
            
            data = response.json()
            messages = data.get("value", [])
            
            print(f"\n📧 Found {len(messages)} unread email(s)")
            
            emails = []
            for msg in messages:
                email_data = {
                    "id": msg.get("id"),
                    "subject": msg.get("subject", "No Subject"),
                    "from": msg.get("from", {}).get("emailAddress", {}).get("address", "Unknown"),
                    "from_name": msg.get("from", {}).get("emailAddress", {}).get("name", "Unknown"),
                    "date": msg.get("receivedDateTime"),
                    "body_preview": msg.get("bodyPreview", ""),
                    "body": msg.get("body", {}).get("content", ""),
                    "body_type": msg.get("body", {}).get("contentType", "text")
                }
                
                emails.append(email_data)
                
                print(f"\n--- Email ---")
                print(f"From: {email_data['from_name']} ({email_data['from']})")
                print(f"Subject: {email_data['subject']}")
                print(f"Date: {email_data['date']}")
                print(f"Preview: {email_data['body_preview'][:100]}...")
            
            return emails
            
        except requests.exceptions.HTTPError as e:
            print(f"❌ Failed to fetch emails: {e}")
            if e.response.status_code == 401:
                print("Token expired or invalid. Please re-authenticate.")
            return []
        except Exception as e:
            print(f"❌ Error: {e}")
            return []
    
    def mark_as_read(self, email_id):
        """Mark an email as read"""
        url = f"{self.graph_endpoint}/me/messages/{email_id}"
        
        data = {"isRead": True}
        
        try:
            response = requests.patch(url, headers=self.get_headers(), json=data)
            response.raise_for_status()
            print(f"✅ Marked email {email_id} as read")
            return True
        except Exception as e:
            print(f"❌ Failed to mark as read: {e}")
            return False
    
    def search_emails(self, query, max_results=10):
        """
        Search emails with a query
        
        Args:
            query: Search query string
            max_results: Maximum results to return
        """
        url = f"{self.graph_endpoint}/me/messages"
        
        params = {
            "$search": f'"{query}"',
            "$top": max_results,
            "$select": "id,subject,from,receivedDateTime,bodyPreview"
        }
        
        try:
            response = requests.get(url, headers=self.get_headers(), params=params)
            response.raise_for_status()
            
            return response.json().get("value", [])
        except Exception as e:
            print(f"❌ Search failed: {e}")
            return []


# Example usage
if __name__ == "__main__":
    print("=== KBTU Email Monitor - Graph API Version ===\n")
    
    # STEP 1: You need to register an app in Azure AD first
    # Instructions are in the setup guide
    
    # Replace with your Azure AD app client ID
    CLIENT_ID = "4c8f231b-1afe-4887-9c65-8478f564a30e"
    TENANT_ID = "57081b5e-e66a-4993-8eaf-15b0b309293f"
    
    # Initialize monitor
    monitor = GraphEmailMonitor(CLIENT_ID, TENANT_ID)
    
    # Authenticate
    if monitor.authenticate_interactive():
        # Fetch unread emails
        emails = monitor.fetch_unread_emails(max_emails=10)
        
        if emails:
            print(f"\n✅ Successfully fetched {len(emails)} unread email(s)")
            
            # Example: Process with AI (you can integrate your AI agent here)
            # for email in emails:
            #     analyze_with_ai(email)
            print(emails)
        else:
            print("\n📭 No unread emails found")
