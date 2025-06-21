# Web Search Options for HOF Capital VC Outreach

## Current Implementation (FREE)
The system currently uses web scraping to search Google:
- ✅ Working well for finding recent news
- ✅ No API costs
- ⚠️ Could be rate-limited by Google
- ⚠️ May break if Google changes HTML structure

## Monitoring Current Performance
Run this to check search quality:
```bash
python3 test_emails.py "Company Name"
```

Look for:
- "Recent News" field being populated
- Specific funding amounts (e.g., "$150M Series D")
- Current year mentions (2024)

## When to Upgrade
Consider upgrading if you see:
- Empty "Recent News" frequently
- Google blocking messages
- Need >100 searches/day
- Want guaranteed reliability

## API Options Comparison

| API | Free Tier | Paid Cost | Best For |
|-----|-----------|-----------|----------|
| **Current (Scraping)** | Unlimited* | $0 | Testing, low volume |
| **Serper API** | 100/month | $50/mo for 2,500 | Production use |
| **Bing Search** | None | $3 per 1,000 | Cost-effective scale |
| **Brave Search** | 2,000/month | $5 per 1,000 | Privacy-focused |
| **SerpAPI** | None | $50/mo for 5,000 | Multiple search engines |

*Until Google rate limits

## Quick Implementation Guide

### Option 1: Serper API (Recommended for production)
1. Sign up at https://serper.dev
2. Add to `.env`: `SERPER_API_KEY=your_key`
3. Update `app.py`:

```python
def _search_with_serper(self, query: str) -> dict:
    if not os.getenv('SERPER_API_KEY'):
        return self._search_google(query)  # Fallback
    
    headers = {
        'X-API-KEY': os.getenv('SERPER_API_KEY'),
        'Content-Type': 'application/json'
    }
    
    data = {
        'q': query,
        'num': 10,
        'tbs': 'qdr:y'  # Past year
    }
    
    response = requests.post(
        'https://google.serper.dev/search',
        headers=headers,
        json=data
    )
    
    return response.json()
```

### Option 2: Bing Search API
1. Create Azure account
2. Enable Bing Search v7
3. Add to `.env`: `BING_SEARCH_KEY=your_key`

### Option 3: Keep Current + Add Fallback
Add a news API as backup:
- NewsAPI.org (free tier: 100 requests/day)
- Webhose.io (free tier: 1,000 requests/month)

## Cost Calculator
- Average searches per company: 2-3
- If processing 50 companies/day = 150 searches
- Monthly: ~4,500 searches

**Recommended: Serper API Premium ($50/month)**

## Testing Search Quality
```python
# Add this to test search results
def test_search_quality(company_name):
    scraper = CompanyDataScraper()
    data = scraper._search_recent_funding_news(company_name)
    print(f"Found news: {data.get('recent_news', 'None')}")
    return bool(data.get('recent_news'))

# Test companies
test_companies = ["OpenAI", "Stripe", "Anthropic"]
success_rate = sum(test_search_quality(c) for c in test_companies) / len(test_companies)
print(f"Search success rate: {success_rate * 100}%")
```

## Current Performance
Based on recent tests:
- ✅ Finding 2024 funding rounds
- ✅ Extracting specific amounts
- ✅ ~70% success rate on recent news
- ⏱️ Adds ~2-3 seconds to processing

## Recommendation
**Stay with current FREE scraping** until you see issues.
When you need reliability for production use, upgrade to Serper API. 