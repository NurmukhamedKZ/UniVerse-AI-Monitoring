"""
Example: Email Monitor with AI Agent Integration

This example shows how to integrate the email monitor with Claude API
for automated email analysis.
"""

import os
from email_monitor import OutlookEmailMonitor
from anthropic import Anthropic

class AIEmailAnalyzer:
    def __init__(self, api_key):
        """Initialize the AI analyzer with Anthropic API"""
        self.client = Anthropic(api_key=api_key)
    
    def analyze_email(self, email_data):
        """
        Analyze a single email using Claude
        
        Args:
            email_data: Dictionary with email information
            
        Returns:
            Analysis results from Claude
        """
        prompt = f"""
Please analyze this email and provide:
1. Brief summary
2. Priority level (High/Medium/Low)
3. Required action (if any)
4. Category (Academic/Administrative/Social/Spam)

Email Details:
From: {email_data['from']}
Subject: {email_data['subject']}
Date: {email_data['date']}

Body:
{email_data['body'][:2000]}  # Limit body to first 2000 chars
"""
        
        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return message.content[0].text
            
        except Exception as e:
            return f"Error analyzing email: {e}"
    
    def process_emails(self, emails):
        """
        Process multiple emails with AI analysis
        
        Args:
            emails: List of email dictionaries
        """
        results = []
        
        for email_data in emails:
            print(f"\n{'='*60}")
            print(f"Analyzing: {email_data['subject']}")
            print(f"{'='*60}")
            
            analysis = self.analyze_email(email_data)
            
            result = {
                "email": email_data,
                "analysis": analysis
            }
            
            results.append(result)
            
            print(analysis)
            print()
        
        return results


def main():
    # Configuration
    KBTU_EMAIL = "your.name@example.kbtu.kz"
    KBTU_PASSWORD = "your_password"
    ANTHROPIC_API_KEY = "your_anthropic_api_key"  # Get from https://console.anthropic.com/
    
    # Alternative: Read from environment variables (more secure)
    # KBTU_EMAIL = os.getenv("KBTU_EMAIL")
    # KBTU_PASSWORD = os.getenv("KBTU_PASSWORD")
    # ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    
    # Initialize components
    email_monitor = OutlookEmailMonitor(KBTU_EMAIL, KBTU_PASSWORD)
    ai_analyzer = AIEmailAnalyzer(ANTHROPIC_API_KEY)
    
    # Connect and fetch emails
    if email_monitor.connect():
        print("Fetching unseen emails...")
        emails = email_monitor.fetch_unseen_emails()
        
        if emails:
            print(f"\nAnalyzing {len(emails)} email(s) with AI...")
            results = ai_analyzer.process_emails(emails)
            
            # Optional: Save results to file
            # save_results_to_file(results)
        else:
            print("No new emails to analyze")
        
        email_monitor.disconnect()


def save_results_to_file(results):
    """Save analysis results to a JSON file"""
    import json
    from datetime import datetime
    
    filename = f"email_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\nResults saved to {filename}")


if __name__ == "__main__":
    main()
