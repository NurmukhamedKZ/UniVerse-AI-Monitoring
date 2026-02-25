# KBTU Outlook Email Monitor with AI Agent

A Python script to monitor your KBTU Outlook email and analyze messages using AI.

## Setup Instructions

### 1. Enable IMAP on Your KBTU Email

First, you need to enable IMAP access on your Outlook account:

1. Go to https://outlook.office365.com
2. Click Settings (gear icon) → View all Outlook settings
3. Go to Mail → Sync email
4. Under POP and IMAP, make sure IMAP is enabled
5. Save changes

**Note:** If you don't see this option, your KBTU IT department may have disabled it. You'll need to contact them or use Microsoft Graph API instead.

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configuration

#### Basic Email Monitoring (No AI)

Edit `email_monitor.py` and replace:
```python
EMAIL = "your.name@example.kbtu.kz"
PASSWORD = "your_password"
```

Run:
```bash
python email_monitor.py
```

#### With AI Agent Integration

1. Get an Anthropic API key from https://console.anthropic.com/
2. Edit `email_monitor_with_ai.py` and set:
```python
KBTU_EMAIL = "your.name@example.kbtu.kz"
KBTU_PASSWORD = "your_password"
ANTHROPIC_API_KEY = "your_anthropic_api_key"
```

3. Run:
```bash
python email_monitor_with_ai.py
```

### 4. Using Environment Variables (More Secure)

Instead of hardcoding credentials, use environment variables:

**Linux/Mac:**
```bash
export KBTU_EMAIL="your.name@example.kbtu.kz"
export KBTU_PASSWORD="your_password"
export ANTHROPIC_API_KEY="your_api_key"
python email_monitor_with_ai.py
```

**Windows (PowerShell):**
```powershell
$env:KBTU_EMAIL="your.name@example.kbtu.kz"
$env:KBTU_PASSWORD="your_password"
$env:ANTHROPIC_API_KEY="your_api_key"
python email_monitor_with_ai.py
```

## Features

### Basic Monitor (`email_monitor.py`)
- Connect to KBTU Outlook via IMAP
- Fetch unseen (unread) emails
- Extract sender, subject, date, and body
- Continuous monitoring mode (checks every 60 seconds)

### AI-Powered Monitor (`email_monitor_with_ai.py`)
- All basic features plus:
- AI analysis of each email using Claude
- Automatic categorization (Academic/Administrative/Social/Spam)
- Priority detection (High/Medium/Low)
- Action item extraction
- Summary generation

## Usage Examples

### One-time Email Check
```python
from email_monitor import OutlookEmailMonitor

monitor = OutlookEmailMonitor("your.name@example.kbtu.kz", "password")
if monitor.connect():
    emails = monitor.fetch_unseen_emails()
    # Process emails
    monitor.disconnect()
```

### Continuous Monitoring
```python
monitor = OutlookEmailMonitor("your.name@example.kbtu.kz", "password")
if monitor.connect():
    monitor.monitor_continuous(check_interval=60)  # Check every 60 seconds
```

### AI Analysis
```python
from email_monitor_with_ai import AIEmailAnalyzer

analyzer = AIEmailAnalyzer("your_anthropic_api_key")
analysis = analyzer.analyze_email(email_data)
print(analysis)
```

## Customization

### Change Check Interval
```python
monitor.monitor_continuous(check_interval=300)  # Check every 5 minutes
```

### Filter Specific Emails
Modify the search criteria in `fetch_unseen_emails()`:
```python
# Only unseen emails from specific sender
status, messages = self.connection.search(None, 'UNSEEN FROM "professor@kbtu.kz"')

# Unseen emails with specific subject
status, messages = self.connection.search(None, 'UNSEEN SUBJECT "Assignment"')

# Emails from last 7 days
status, messages = self.connection.search(None, 'SINCE "01-Jan-2024"')
```

### Customize AI Analysis
Edit the prompt in `AIEmailAnalyzer.analyze_email()` to change what the AI analyzes.

## Troubleshooting

### "Authentication failed" error
- Check your email and password are correct
- Make sure IMAP is enabled in Outlook settings
- Try logging into webmail first to ensure account is active
- If using 2FA, you may need an app-specific password

### "Connection refused" error
- Check your internet connection
- KBTU network might be blocking IMAP port (993)
- Try from a different network

### IMAP not available
- Contact KBTU IT support to enable IMAP
- Alternative: Use Microsoft Graph API (requires app registration)

## Security Notes

- **Never commit credentials to Git!** Use environment variables or config files (add to .gitignore)
- Consider using app-specific passwords if available
- The script only reads emails, it doesn't delete or modify them
- Mark emails as read if you want to avoid processing them again

## Next Steps

You can extend this to:
- Store analysis results in a database
- Send notifications for high-priority emails
- Auto-respond to certain email types
- Generate daily email summaries
- Integrate with task management tools
- Create custom filters and rules

## License

Free to use for personal and educational purposes.
