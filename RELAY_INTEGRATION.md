# HOF Capital VC Outreach - Relay.app Integration Guide

## Overview
This guide explains how to integrate the HOF Capital VC Outreach system with Relay.app for automated workflow automation.

## Prerequisites
1. Your Flask API must be publicly accessible (deployed to a cloud service)
2. You need to set up an API key for authentication
3. Relay.app account with API/webhook capabilities

## Deployment Options

### Option 1: Deploy to Render.com (Recommended)
1. Create a `render.yaml` file:
```yaml
services:
  - type: web
    name: hof-vc-outreach
    env: python
    buildCommand: "pip install -r requirements.txt"
    startCommand: "gunicorn app:app"
    envVars:
      - key: OPENAI_API_KEY
        sync: false
      - key: HOF_API_KEY
        generateValue: true
```

2. Push to GitHub and connect to Render
3. Your API will be available at: `https://hof-vc-outreach.onrender.com`

### Option 2: Deploy to Heroku
1. Create a `Procfile`:
```
web: gunicorn app:app
```

2. Deploy using Heroku CLI:
```bash
heroku create hof-vc-outreach
heroku config:set OPENAI_API_KEY=your-key
heroku config:set HOF_API_KEY=your-secure-api-key
git push heroku main
```

### Option 3: Deploy to Railway
Simply connect your GitHub repo to Railway and it will auto-deploy.

## API Endpoints

### 1. Health Check
```
GET https://your-api-url.com/api/health
```

### 2. Generate Outreach Email
```
POST https://your-api-url.com/api/generate-outreach
Headers:
  Authorization: Bearer YOUR_HOF_API_KEY
  Content-Type: application/json

Body:
{
  "company_name": "OpenAI"
}

Response:
{
  "success": true,
  "data": {
    "company_name": "OpenAI",
    "ceo_name": "Sam Altman",
    "email_content": "Hi Sam,\n\nHope you're doing well...",
    "subject_line": "HOF Capital - Partnership Opportunity with OpenAI",
    "company_details": {
      "description": "OpenAI is an AI research company...",
      "technology_focus": "large language models and AI safety",
      "recent_news": "launching GPT-4o...",
      "impressive_metric": "over 100 million weekly active users"
    }
  },
  "metadata": {
    "generated_at": "2025-01-20 12:00:00 UTC",
    "api_version": "1.0"
  }
}
```

## Relay.app Integration Steps

### Step 1: Create HTTP Request Action
1. In Relay.app, add a new "HTTP Request" action
2. Configure:
   - Method: `POST`
   - URL: `https://your-api-url.com/api/generate-outreach`
   - Headers:
     ```
     Authorization: Bearer YOUR_HOF_API_KEY
     Content-Type: application/json
     ```
   - Body:
     ```json
     {
       "company_name": "{{company_name}}"
     }
     ```

### Step 2: Parse Response
1. Add a "Parse JSON" action after the HTTP request
2. Extract fields:
   - `email_content` → For the email body
   - `subject_line` → For the email subject
   - `ceo_name` → For personalization

### Step 3: Send Email
1. Add a "Gmail" or "Outlook" action
2. Configure:
   - To: `{{ceo_email}}` (you'll need to source this separately)
   - Subject: `{{parsed_response.data.subject_line}}`
   - Body: `{{parsed_response.data.email_content}}`

## Complete Relay.app Workflow Example

```yaml
Trigger: New row in Google Sheets
  ↓
Action 1: HTTP Request to HOF API
  - Input: Company name from sheet
  - Output: Email content and metadata
  ↓
Action 2: Find CEO Email (using Hunter.io or similar)
  - Input: Company name + CEO name
  - Output: Email address
  ↓
Action 3: Send Email via Gmail
  - To: CEO email
  - Subject: Generated subject line
  - Body: Generated email content
  ↓
Action 4: Update Google Sheet
  - Mark as "Outreach Sent"
  - Add timestamp
```

## Security Best Practices

1. **API Key Management**:
   - Never expose your API key in client-side code
   - Use environment variables
   - Rotate keys regularly

2. **Rate Limiting** (add to your Flask app):
   ```python
   from flask_limiter import Limiter
   limiter = Limiter(app, key_func=lambda: request.headers.get('Authorization'))
   
   @limiter.limit("10 per minute")
   @app.route('/api/generate-outreach', methods=['POST'])
   ```

3. **Webhook Security**:
   - Implement request signing
   - Validate webhook payloads

## Advanced Integration Features

### Batch Processing
Send multiple companies at once:
```json
{
  "companies": ["OpenAI", "Stripe", "Anthropic"],
  "batch": true
}
```

### Custom Templates
Pass template parameters:
```json
{
  "company_name": "OpenAI",
  "template_vars": {
    "sender_name": "Tahseen Rashid",
    "sender_title": "Investor",
    "calendar_link": "https://calendly.com/tahseen-hof"
  }
}
```

## Monitoring & Debugging

1. Check API health: `GET /api/health`
2. View logs in your deployment platform
3. Test with curl:
   ```bash
   curl -X POST https://your-api-url.com/api/generate-outreach \
     -H "Authorization: Bearer YOUR_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"company_name": "OpenAI"}'
   ```

## Support
For issues or questions, please check the Flask app logs or contact the development team. 