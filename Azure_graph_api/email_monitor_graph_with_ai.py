"""
Email Monitor with AI Agent - Microsoft Graph API Version
Works with Office 365 accounts that have Basic Auth blocked
"""

import requests
import json
from datetime import datetime
import webbrowser
from anthropic import Anthropic

class GraphEmailMonitor:
    """Same as email_monitor_graph.py - included here for completeness"""
    
    def __init__(self, client_id, tenant_id="common"):
        self.client_id = client_id
        self.tenant_id = tenant_id
        self.access_token = None
        self.graph_endpoint = "https://graph.microsoft.com/v1.0"
        self.scopes = ["Mail.Read", "offline_access"]
    
    def get_auth_url(self):
        from urllib.parse import urlencode
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
        print("\n=== Microsoft Authentication Required ===")
        print("\n1. Your browser will open with Microsoft login page")
        print("2. Sign in with your KBTU credentials")
        print("3. Grant permissions to read your emails")
        print("4. Copy the ENTIRE URL from your browser after redirect")
        print("\nPress Enter to open browser...")
        input()
        
        auth_url = self.get_auth_url()
        webbrowser.open(auth_url)
        
        print("\nAfter signing in, paste the FULL redirect URL here:")
        redirect_response = input("URL: ").strip()
        
        if "code=" in redirect_response:
            code = redirect_response.split("code=")[1].split("&")[0]
            return self.get_token_from_code(code)
        else:
            print("❌ No authorization code found in URL")
            return False
    
    def get_token_from_code(self, code):
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
            return False
    
    def get_headers(self):
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    def fetch_unread_emails(self, max_emails=10):
        if not self.access_token:
            print("❌ Not authenticated")
            return []
        
        url = f"{self.graph_endpoint}/me/messages"
        params = {
            "$filter": "isRead eq false",
            "$top": max_emails,
            "$select": "id,subject,from,receivedDateTime,bodyPreview,body",
            "$orderby": "receivedDateTime DESC"
        }
        
        try:
            response = requests.get(url, headers=self.get_headers(), params=params)
            response.raise_for_status()
            messages = response.json().get("value", [])
            
            print(f"\n📧 Found {len(messages)} unread email(s)")
            
            emails = []
            for msg in messages:
                # Remove HTML tags from body for cleaner AI analysis
                body_content = msg.get("body", {}).get("content", "")
                if msg.get("body", {}).get("contentType") == "html":
                    import re
                    body_content = re.sub('<[^<]+?>', '', body_content)
                
                email_data = {
                    "id": msg.get("id"),
                    "subject": msg.get("subject", "No Subject"),
                    "from": msg.get("from", {}).get("emailAddress", {}).get("address", "Unknown"),
                    "from_name": msg.get("from", {}).get("emailAddress", {}).get("name", "Unknown"),
                    "date": msg.get("receivedDateTime"),
                    "body_preview": msg.get("bodyPreview", ""),
                    "body": body_content[:3000]  # Limit to 3000 chars for AI
                }
                emails.append(email_data)
            
            return emails
        except Exception as e:
            print(f"❌ Failed to fetch emails: {e}")
            return []


class AIEmailAnalyzer:
    """AI-powered email analyzer using Claude"""
    
    def __init__(self, api_key):
        self.client = Anthropic(api_key=api_key)
    
    def analyze_email(self, email_data):
        """Analyze a single email with AI"""
        
        prompt = f"""Analyze this university email and provide:

1. **Summary** (1-2 sentences)
2. **Priority Level**: High / Medium / Low
3. **Category**: Academic / Administrative / Social / Newsletter / Spam
4. **Action Required**: Yes/No - if yes, what action and by when?
5. **Key Information**: Important dates, deadlines, links, or requirements

Email Details:
From: {email_data['from_name']} ({email_data['from']})
Subject: {email_data['subject']}
Date: {email_data['date']}

Body:
{email_data['body']}

Keep your response concise and actionable."""

        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=800,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text
        except Exception as e:
            return f"Error analyzing email: {e}"
    
    def batch_analyze(self, emails):
        """Analyze multiple emails and return results"""
        results = []
        
        print(f"\n🤖 Analyzing {len(emails)} email(s) with AI...\n")
        
        for i, email_data in enumerate(emails, 1):
            print(f"[{i}/{len(emails)}] Analyzing: {email_data['subject'][:50]}...")
            
            analysis = self.analyze_email(email_data)
            
            result = {
                "email": email_data,
                "analysis": analysis,
                "analyzed_at": datetime.now().isoformat()
            }
            
            results.append(result)
            
            # Print formatted result
            print(f"\n{'='*70}")
            print(f"📧 {email_data['subject']}")
            print(f"From: {email_data['from_name']}")
            print(f"{'='*70}")
            print(analysis)
            print()
        
        return results
    
    def generate_daily_summary(self, results):
        """Generate a summary of all analyzed emails"""
        
        if not results:
            return "No emails to summarize."
        
        emails_text = "\n\n".join([
            f"Email {i+1}:\nSubject: {r['email']['subject']}\nFrom: {r['email']['from_name']}\nAnalysis: {r['analysis']}"
            for i, r in enumerate(results)
        ])
        
        prompt = f"""Create a brief daily email summary for a university student. 

Here are today's {len(results)} unread emails with AI analysis:

{emails_text}

Provide:
1. High priority items that need immediate attention
2. Important deadlines or dates mentioned
3. Quick overview of other emails

Keep it concise and actionable."""

        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text
        except Exception as e:
            return f"Error generating summary: {e}"


def save_analysis_report(results, filename=None):
    """Save analysis results to JSON file"""
    if not filename:
        filename = f"email_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Analysis saved to: {filename}")
    return filename


def main():
    print("="*70)
    print("KBTU Email AI Agent - Microsoft Graph API Version")
    print("="*70)
    
    # Configuration
    CLIENT_ID = "YOUR_CLIENT_ID_HERE"
    ANTHROPIC_API_KEY = "YOUR_ANTHROPIC_API_KEY"
    
    # Check configuration
    if CLIENT_ID == "YOUR_CLIENT_ID_HERE":
        print("\n❌ Error: CLIENT_ID not set!")
        print("Please follow SETUP_GUIDE.md to register Azure AD app")
        return
    
    if ANTHROPIC_API_KEY == "YOUR_ANTHROPIC_API_KEY":
        print("\n❌ Error: ANTHROPIC_API_KEY not set!")
        print("Get your API key from: https://console.anthropic.com/")
        return
    
    # Initialize components
    email_monitor = GraphEmailMonitor(CLIENT_ID)
    ai_analyzer = AIEmailAnalyzer(ANTHROPIC_API_KEY)
    
    # Step 1: Authenticate
    print("\nStep 1: Authenticating with Microsoft...")
    if not email_monitor.authenticate_interactive():
        print("❌ Authentication failed")
        return
    
    # Step 2: Fetch emails
    print("\nStep 2: Fetching unread emails...")
    emails = email_monitor.fetch_unread_emails(max_emails=10)
    
    if not emails:
        print("\n✅ No unread emails - inbox is clean!")
        return
    
    # Step 3: Analyze with AI
    print("\nStep 3: AI Analysis...")
    results = ai_analyzer.batch_analyze(emails)
    
    # Step 4: Generate summary
    print("\n" + "="*70)
    print("📊 DAILY EMAIL SUMMARY")
    print("="*70)
    summary = ai_analyzer.generate_daily_summary(results)
    print(summary)
    
    # Step 5: Save results
    save_analysis_report(results)
    
    print("\n" + "="*70)
    print("✅ Analysis complete!")
    print("="*70)


if __name__ == "__main__":
    main()
