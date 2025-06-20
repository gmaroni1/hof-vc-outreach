# HOF Capital Outreach System - Enhanced Setup Guide

## 🔐 Security Setup (IMPORTANT!)

### Step 1: Create Environment Variables File

1. Create a `.env` file in the project directory:
```bash
touch .env
```

2. Add your API keys (NEVER commit this file to git):
```
# OpenAI API Key - Get yours from https://platform.openai.com/api-keys
OPENAI_API_KEY=your-openai-api-key-here
```

### Step 2: Secure Your API Keys

1. **NEVER share API keys** in messages, code, or public repositories
2. Add `.env` to your `.gitignore` file:
```bash
echo ".env" >> .gitignore
```

3. **Revoke any exposed keys immediately** at https://platform.openai.com/api-keys

## 🚀 Enhanced Features

### OpenAI Integration

With OpenAI API configured, the system now:

1. **Enhances Company Research**
   - Uses GPT-4 to provide accurate company descriptions
   - Identifies key technologies and innovations
   - Verifies and corrects CEO/founder names

2. **Improves Email Quality**
   - Generates more compelling descriptions
   - Adds technology focus to make emails more relevant
   - Ensures accuracy of company information

### How It Works

1. **Initial Web Scraping**: Searches for company website and basic info
2. **OpenAI Enhancement**: If API key is provided, enhances the data with:
   - Better company descriptions
   - Verified leadership names
   - Technology and innovation focus
3. **Email Generation**: Creates personalized outreach using enhanced data

## 📋 Alternative Data Sources

Instead of scraping LinkedIn (which violates their ToS), consider these legitimate alternatives:

### 1. **Clearbit API** (https://clearbit.com)
- Company enrichment data
- Leadership information
- Technology stack data

### 2. **Hunter.io** (https://hunter.io)
- Find email addresses
- Verify email validity
- Company domain search

### 3. **Crunchbase API** (https://www.crunchbase.com/api)
- Funding information
- Leadership data
- Company descriptions

### 4. **RapidAPI Company Data** (https://rapidapi.com)
- Various company data APIs
- Leadership information
- Industry insights

## 🎨 Updated Color Scheme

The interface now uses HOF Capital's brand colors:
- Primary: #990001 (HOF Red)
- Gradient: #990001 to #660001
- All UI elements updated to match

## 📦 Installation

1. Install the updated dependencies:
```bash
pip3 install -r requirements.txt
```

2. Create your `.env` file with API keys

3. Run the application:
```bash
python3 app.py
```

4. Open http://localhost:5000

## 🔧 Configuration Options

### Environment Variables

```bash
# Required for enhanced features
OPENAI_API_KEY=your-key-here

# Optional: Additional data sources
CLEARBIT_API_KEY=your-key-here
HUNTER_API_KEY=your-key-here

# Optional: Customize behavior
OPENAI_MODEL=gpt-4  # or gpt-3.5-turbo for faster/cheaper
MAX_RETRIES=3
TIMEOUT_SECONDS=30
```

## 💡 Best Practices

1. **API Key Security**
   - Use environment variables
   - Rotate keys regularly
   - Monitor usage

2. **Rate Limiting**
   - The app includes delays between requests
   - Monitor your API usage
   - Consider caching results

3. **Data Accuracy**
   - Always verify generated content
   - Cross-reference important details
   - Edit emails before sending

## 🚨 Important Notes

1. **DO NOT** scrape LinkedIn - it violates their Terms of Service
2. **DO NOT** share API keys publicly
3. **DO** verify all generated information before sending emails
4. **DO** respect rate limits and terms of service for all APIs

## 📧 Support

For questions or issues:
- Check API key configuration
- Verify internet connectivity
- Review error messages in terminal
- Ensure all dependencies are installed

Remember: This tool is meant to assist, not replace, human judgment in outreach efforts. 