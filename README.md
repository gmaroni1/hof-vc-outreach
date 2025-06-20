# HOF Capital - Automated Outreach System

An intelligent web application that automatically generates personalized outreach emails for venture capital purposes. Simply enter a company name, and the system will scrape the internet to find company information and generate a professional outreach email using your template.

## Features

- 🔍 **Intelligent Web Scraping**: Automatically finds company websites and extracts key information
- 👤 **CEO/Founder Detection**: Identifies company leadership through pattern matching
- 📧 **Email Generation**: Creates personalized outreach emails using your HOF Capital template
- 📋 **One-Click Copy**: Copy generated emails to clipboard instantly
- 📱 **Responsive Design**: Beautiful, modern interface that works on all devices
- ⚡ **Fast Processing**: Efficient scraping and data extraction

## How It Works

1. **Input**: Enter a company name in the text field
2. **Research**: The system searches for the company's website and extracts:
   - Company description/what they do
   - CEO or Founder name
   - Business focus and technology usage
3. **Generate**: Creates a personalized outreach email using the HOF Capital template
4. **Copy**: One-click copy to clipboard for immediate use

## Setup Instructions

### Prerequisites

- Python 3.7 or higher
- Internet connection for web scraping

### Installation

1. **Clone or navigate to the project directory**:
   ```bash
   cd vc-outreach-system
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python app.py
   ```

4. **Open your browser** and navigate to:
   ```
   http://localhost:5000
   ```

## Usage

1. Open the web application in your browser
2. Enter the company name you want to research (e.g., "OpenAI", "Stripe")
3. Click "Generate Outreach Email"
4. Wait for the system to research the company (usually 10-30 seconds)
5. Review the generated email and company information
6. Click "Copy to Clipboard" to copy the email
7. Paste into your email client and send!

## Email Template

The system uses your HOF Capital template format:

```
Hi [CEO Name],

Congrats on the impressive progress with [Company Name]! What you're building is extremely compelling – the way [Company Name] is leveraging [Company Description]

For quick context, I'm on the investment team at HOF Capital, a $3B+ AUM multi-stage VC firm that has backed transformative ventures including OpenAI, xAI, Epic Games, UiPath, and Rimac Automobili. Each year, we selectively partner with visionary founders who leverage cutting-edge technology to tackle significant societal and operational challenges, much like [Company Name] is doing in redefining the creative landscape. Additionally, our LP base includes influential leaders across consumer and technology industries, providing extensive strategic value.

I'd love to set up some time to connect and explore how HOF could potentially contribute and accelerate [Company Name]'s journey to becoming a generational company. Here's my calendar.

Looking forward to speaking soon!

Cheers,
Giacomo M.
Analyst | HOF Capital
hofcapital.com
```

## Technical Details

### Architecture

- **Backend**: Python Flask web server
- **Frontend**: HTML, CSS, JavaScript (no framework dependencies)
- **Web Scraping**: BeautifulSoup4 + Requests
- **Pattern Matching**: Regular expressions for CEO/founder detection

### Data Sources

The system attempts to gather information from:
1. Company's official website (meta descriptions, about pages)
2. Google search results (company descriptions, leadership info)
3. Multiple fallback strategies for robust data extraction

### Privacy & Ethics

- Respects robots.txt and rate limiting
- Uses public information only
- Implements delays between requests to be respectful to servers
- Does not store or cache company data

## Troubleshooting

### Common Issues

1. **"Company information not found"**:
   - Try using the full, official company name
   - Some newer companies may have limited online presence

2. **Slow performance**:
   - Initial requests may take longer due to cold start
   - Complex company names may require more research time

3. **Network errors**:
   - Check your internet connection
   - Some corporate firewalls may block web scraping

### Improving Results

- Use official company names (e.g., "OpenAI" instead of "Open AI")
- Include suffixes if needed (e.g., "Stripe Inc" if "Stripe" doesn't work)
- For very new companies, you may need to manually edit the generated email

## Security Notes

- The application runs locally on your machine
- No data is sent to external services except for web scraping
- No API keys or credentials required
- All processing happens on your local system

## License

This project is for internal use at HOF Capital. Please ensure compliance with web scraping best practices and terms of service of target websites.

## Support

For technical issues or feature requests, please contact the development team. 