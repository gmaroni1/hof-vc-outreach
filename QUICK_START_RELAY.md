# Quick Start: HOF VC Outreach + Relay.app

## 🚀 3-Step Setup

### Step 1: Deploy Your API
Choose one option:

**Option A - Render (Easiest):**
1. Push code to GitHub
2. Connect repo to [Render.com](https://render.com)
3. Add environment variables:
   - `OPENAI_API_KEY`: Your OpenAI key
   - `HOF_API_KEY`: Generate with `python -c "import secrets; print(secrets.token_urlsafe(32))"`

**Option B - Heroku:**
```bash
heroku create hof-vc-outreach
heroku config:set OPENAI_API_KEY=your-key HOF_API_KEY=your-api-key
git push heroku main
```

### Step 2: Test Your API
```bash
curl -X POST https://your-api.com/api/generate-outreach \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"company_name": "OpenAI"}'
```

### Step 3: Connect to Relay.app

1. **Create Workflow:**
   - Trigger: Google Sheets (new row)
   - Action 1: HTTP Request
   - Action 2: Send Email

2. **Configure HTTP Request:**
   ```
   URL: https://your-api.com/api/generate-outreach
   Method: POST
   Headers:
     Authorization: Bearer YOUR_API_KEY
     Content-Type: application/json
   Body:
     {
       "company_name": "{{company_name_from_sheet}}"
     }
   ```

3. **Map Response to Email:**
   - Subject: `{{response.data.subject_line}}`
   - Body: `{{response.data.email_content}}`
   - To: CEO email (from another source)

## 📊 Example Workflow

```
Google Sheet Structure:
| Company | Status | CEO Email |
|---------|--------|-----------|
| OpenAI  | Pending| sam@openai.com |

Relay Workflow:
1. Trigger when Status = "Pending"
2. Call HOF API with Company name
3. Send email with generated content
4. Update Status to "Sent"
```

## 🔒 Security Reminder
- Keep your `HOF_API_KEY` secret
- Use HTTPS only
- Set up rate limiting if needed

## 📧 Response Format
```json
{
  "data": {
    "email_content": "Hi Sam,\n\nHope you're doing well...",
    "subject_line": "HOF Capital - Partnership Opportunity",
    "ceo_name": "Sam Altman"
  }
}
```

That's it! Your VC outreach is now automated. 🎉 