# 🚀 Deploy Your HOF VC Outreach System - Simple Steps

## Option 1: Deploy to Render (Recommended - FREE)

### Step 1: Create GitHub Repository
1. Go to [github.com](https://github.com) and create a new repository
2. Name it: `hof-vc-outreach`
3. Keep it public (for free deployment)

### Step 2: Push Your Code to GitHub
Run these commands in your terminal:
```bash
cd /Users/giacomo/vc-outreach-system
git remote add origin https://github.com/YOUR_USERNAME/hof-vc-outreach.git
git branch -M main
git push -u origin main
```

### Step 3: Deploy on Render
1. Go to [render.com](https://render.com) and sign up (free)
2. Click "New +" → "Web Service"
3. Connect your GitHub account
4. Select your `hof-vc-outreach` repository
5. Render will auto-detect the settings from `render.yaml`
6. Click "Create Web Service"

### Step 4: Add Environment Variables
In Render dashboard:
1. Go to "Environment" tab
2. Add these variables:
   - `OPENAI_API_KEY` = Your OpenAI key
   - `HOF_API_KEY` = Generate one: 
     ```bash
     python3 -c "import secrets; print(secrets.token_urlsafe(32))"
     ```
   Copy and save this HOF_API_KEY - you'll need it for Relay!

### Step 5: Wait for Deployment
- Takes about 5-10 minutes
- Once green checkmark appears, your API is live!
- Your URL will be: `https://hof-vc-outreach.onrender.com`

### Step 6: Test Your API
```bash
curl -X POST https://hof-vc-outreach.onrender.com/api/generate-outreach \
  -H "Authorization: Bearer YOUR_HOF_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"company_name": "OpenAI"}'
```

## Option 2: Deploy to Heroku (Also Free)

### Prerequisites
Install Heroku CLI: `brew install heroku/brew/heroku`

### Deploy Steps
```bash
cd /Users/giacomo/vc-outreach-system
heroku create hof-vc-outreach
heroku config:set OPENAI_API_KEY="your-openai-key"
heroku config:set HOF_API_KEY="your-generated-api-key"
git push heroku main
```

## 🎯 Next: Connect to Relay.app

1. In Relay.app, create new workflow
2. Add HTTP Request action:
   - URL: `https://your-app.onrender.com/api/generate-outreach`
   - Headers: `Authorization: Bearer YOUR_HOF_API_KEY`
   - Body: `{"company_name": "{{company_name}}"}`
3. Use the response to send emails!

## 🆘 Troubleshooting

**If deployment fails:**
- Check logs in Render dashboard
- Make sure all files are committed to git
- Verify Python version in runtime.txt

**If API returns errors:**
- Check your OPENAI_API_KEY is valid
- Ensure HOF_API_KEY matches what you're using

That's it! Your API is now live and ready for automation! 🎉 