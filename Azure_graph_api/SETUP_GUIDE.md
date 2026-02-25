# Setup Guide: Microsoft Graph API for KBTU Email

Since KBTU has blocked basic authentication (IMAP), you need to use Microsoft Graph API instead. This requires a one-time setup in Azure.

## Step 1: Register an Application in Azure AD

### Option A: Personal Microsoft Account (Easiest)

1. Go to: https://portal.azure.com/#view/Microsoft_AAD_RegisteredApps/ApplicationsListBlade
2. Click **"New registration"**
3. Fill in:
   - **Name**: "KBTU Email Monitor" (or any name you like)
   - **Supported account types**: Select "Accounts in any organizational directory (Any Azure AD directory - Multitenant)"
   - **Redirect URI**: 
     - Type: **Web**
     - URL: `http://localhost:8080`
4. Click **"Register"**

### Option B: Ask KBTU IT Department

If you can't access Azure Portal, you need to ask KBTU IT to:
- Register an application for you
- Grant it `Mail.Read` permission
- Provide you with the Client ID

## Step 2: Configure API Permissions

1. After registration, you'll see your app's overview page
2. **COPY the "Application (client) ID"** - you'll need this!
3. In the left menu, click **"API permissions"**
4. Click **"+ Add a permission"**
5. Select **"Microsoft Graph"**
6. Select **"Delegated permissions"**
7. Search for and check **"Mail.Read"**
8. Click **"Add permissions"**
9. (Optional) If you have admin rights, click **"Grant admin consent for [organization]"**

## Step 3: Update Your Script

Open `email_monitor_graph.py` and replace:

```python
CLIENT_ID = "YOUR_CLIENT_ID_HERE"
```

With your actual Client ID from Step 2.

## Step 4: Install Dependencies

```bash
pip install requests
```

## Step 5: Run the Script

```bash
python email_monitor_graph.py
```

### What Will Happen:

1. Script opens your browser
2. You'll see Microsoft login page
3. Sign in with your KBTU credentials (n_ashekei@kbtu.kz)
4. Microsoft will ask to grant permissions - click **Accept**
5. Browser redirects to `http://localhost:8080/?code=...` (this will fail to load - that's OK!)
6. **COPY THE ENTIRE URL** from your browser address bar
7. Paste it back in the terminal
8. Script will fetch your unread emails!

## Troubleshooting

### "The reply URL specified in the request does not match..."

Make sure redirect URI in Azure is exactly: `http://localhost:8080` (no trailing slash)

### "AADSTS65001: The user or administrator has not consented..."

You need to grant admin consent in Azure Portal, or just accept permissions when logging in.

### "AADSTS50020: User account from identity provider does not exist..."

Make sure you selected "Accounts in any organizational directory (Multitenant)" when registering the app.

### Still can't register app?

Contact KBTU IT department and ask them to:
1. Enable app registration for students, OR
2. Register the app for you and provide the Client ID

## Alternative: Use Client Credentials Flow (Advanced)

If KBTU IT can create a service account for you, they can set up "application permissions" instead of "delegated permissions". This doesn't require user login but needs higher permissions.

## Security Notes

- The access token expires after 1 hour
- For production use, implement token refresh (requires client secret)
- Never share your Client ID publicly if it has a client secret
- This app can only read your emails, cannot send or delete

## Next Steps

Once you get it working, you can:
- Save the token for reuse (add refresh token logic)
- Integrate with your AI agent
- Set up continuous monitoring
- Add webhook subscriptions for real-time notifications

---

## Quick Reference: Key URLs

- **Azure App Registration**: https://portal.azure.com/#view/Microsoft_AAD_RegisteredApps/ApplicationsListBlade
- **Graph API Docs**: https://learn.microsoft.com/en-us/graph/api/user-list-messages
- **Permission Reference**: https://learn.microsoft.com/en-us/graph/permissions-reference#mail-permissions
