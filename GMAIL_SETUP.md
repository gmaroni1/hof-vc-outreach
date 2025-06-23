# Gmail Integration Setup Guide

## Prerequisites

To enable Gmail integration, you need to set up Google OAuth2 credentials. Follow these steps:

## 1. Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Gmail API:
   - Go to "APIs & Services" > "Library"
   - Search for "Gmail API"
   - Click on it and press "Enable"

## 2. Create OAuth2 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. If prompted, configure the OAuth consent screen first:
   - Choose "External" user type
   - Fill in the required fields (app name, user support email, etc.)
   - Add your email to test users
   - Add scope: `https://www.googleapis.com/auth/gmail.send`

4. Create OAuth client ID:
   - Application type: "Web application"
   - Name: "HOF VC Outreach"
   - Authorized redirect URIs:
     - `http://localhost:5001/api/gmail/callback` (for development)
     - `https://hof-vc-outreach.onrender.com/api/gmail/callback` (for production)

## 3. Configure Environment Variables

Add these to your `.env` file:

```
GOOGLE_CLIENT_ID=your_client_id_here
GOOGLE_CLIENT_SECRET=your_client_secret_here
```

## 4. React App Configuration

Create a `.env` file in the React app directory:

```
REACT_APP_API_URL=http://localhost:5001
```

For production, update to:
```
REACT_APP_API_URL=https://hof-vc-outreach.onrender.com
```

## Usage

1. Click "Connect Gmail" button in the email section
2. Authorize the app to send emails on your behalf
3. Once connected, you can send emails directly from the platform
4. Your authentication will be saved for future use

## Security Notes

- The `gmail_token.pickle` file contains your OAuth tokens - keep it secure
- Never commit this file to version control (it's in .gitignore)
- Tokens are refreshed automatically when they expire
- You can disconnect Gmail at any time using the logout button

## Troubleshooting

- If authentication fails, check that redirect URIs match exactly
- Ensure Gmail API is enabled in Google Cloud Console
- For production, update the frontend URL in `app.py` (line 1415) 