"""
Webhook Server to Receive Emails from Power Automate
This server receives email data from Power Automate and processes it with AI
"""

from flask import Flask, request, jsonify
# from anthropic import Anthropic
import json
from datetime import datetime
import os

app = Flask(__name__)

# Configuration
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "your_api_ke_here")
# ai_client = Anthropic(api_key=ANTHROPIC_API_KEY)

# Store processed emails (in production, use a database)
processed_emails = []


def analyze_email_with_ai(email_data):
    """Analyze email using Claude AI"""
    
    prompt = f"""Analyze this university email and provide:

1. **Summary** (1-2 sentences)
2. **Priority Level**: High / Medium / Low
3. **Category**: Academic / Administrative / Social / Newsletter / Spam
4. **Action Required**: Yes/No - if yes, what action and by when?
5. **Key Information**: Important dates, deadlines, links, or requirements

Email Details:
From: {email_data.get('from', 'Unknown')}
Subject: {email_data.get('subject', 'No Subject')}
Date: {email_data.get('date', 'Unknown')}
Importance: {email_data.get('importance', 'Normal')}

Body Preview:
{email_data.get('body', 'No preview available')}

Keep your response concise and actionable."""

    try:
        message = ai_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=800,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text
    except Exception as e:
        return f"Error analyzing email: {e}"


@app.route('/')
def home():
    """Home page showing server status"""
    return jsonify({
        "status": "running",
        "message": "KBTU Email AI Webhook Server",
        "emails_processed": len(processed_emails),
        "endpoints": {
            "webhook": "/webhook",
            "status": "/status",
            "emails": "/emails"
        }
    })


@app.route('/webhook', methods=['POST'])
def webhook():
    """
    Webhook endpoint to receive emails from Power Automate
    Power Automate will POST email data here
    """
    try:
        # Get email data from Power Automate
        email_data = request.json
        
        print("\n" + "="*70)
        print("📧 NEW EMAIL RECEIVED")
        print("="*70)
        print(f"From: {email_data.get('from', 'Unknown')}")
        print(f"Subject: {email_data.get('subject', 'No Subject')}")
        print(f"Date: {email_data.get('date', 'Unknown')}")
        print(f"Importance: {email_data.get('importance', 'Normal')}")
        print("="*70)
        
        # Analyze with AI
        print("\n🤖 Analyzing with AI...")
        # analysis = analyze_email_with_ai(email_data)
        analysis = "Analysis not implemented yet"
        print("\n" + "="*70)
        print("📊 AI ANALYSIS")
        print("="*70)
        print(analysis)
        print("="*70 + "\n")
        
        # Store result
        result = {
            "email": email_data,
            "analysis": analysis,
            "processed_at": datetime.now().isoformat(),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        processed_emails.append(result)
        
        # Save to file (optional)
        save_to_file(result)
        
        # Return success response to Power Automate
        return jsonify({
            "status": "success",
            "message": "Email received and analyzed",
            "subject": email_data.get('subject', 'No Subject')
        }), 200
        
    except Exception as e:
        print(f"\n❌ Error processing webhook: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/status')
def status():
    """Check server status and see processed email count"""
    return jsonify({
        "status": "running",
        "emails_processed": len(processed_emails),
        "last_processed": processed_emails[-1]["timestamp"] if processed_emails else "None"
    })


@app.route('/emails')
def get_emails():
    """View all processed emails and their analysis"""
    return jsonify({
        "total": len(processed_emails),
        "emails": processed_emails
    })


@app.route('/test', methods=['POST'])
def test_webhook():
    """Test endpoint to verify webhook is working"""
    data = request.json
    print(f"\n✅ Test webhook received: {data}")
    return jsonify({"status": "success", "received": data})


def save_to_file(result):
    """Save analysis to JSON file"""
    filename = "email_analyses.json"
    
    try:
        # Load existing data
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = []
        
        # Append new result
        data.append(result)
        
        # Save back
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved to {filename}")
        
    except Exception as e:
        print(f"⚠️ Could not save to file: {e}")


if __name__ == '__main__':
    print("\n" + "="*70)
    print("🚀 Starting KBTU Email AI Webhook Server")
    print("="*70)
    print("\nEndpoints:")
    print("  - Webhook: POST /webhook")
    print("  - Status: GET /status")
    print("  - View emails: GET /emails")
    print("  - Test: POST /test")
    print("\n" + "="*70)
    
    # Check if API key is set
    if ANTHROPIC_API_KEY == "your_api_key_here":
        print("\n⚠️  WARNING: ANTHROPIC_API_KEY not set!")
        print("Set it with: export ANTHROPIC_API_KEY='your-key-here'")
        print("Or edit the script directly")
    
    print("\n")
    
    # Run server
    # For local testing: host='localhost', port=5000
    # For production: host='0.0.0.0', port=5000
    app.run(host='0.0.0.0', port=8000, debug=True)