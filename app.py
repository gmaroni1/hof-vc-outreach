from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import re
import time
import urllib.parse
from typing import Dict, Optional, Any
import os
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed
import functools

# Load environment variables
load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
SPECTER_API_KEY = os.getenv('SPECTER_API_KEY')
HOF_API_KEY = os.getenv('HOF_API_KEY', 'your-secure-api-key-here')
SERPER_API_KEY = os.getenv('SERPER_API_KEY')

# Model Configuration - Easy to switch between models
MODEL_CONFIG = {
    # Current: Fast and cost-effective
    "current": {
        "model": "gpt-3.5-turbo",
        "temperature": 0.3,
        "description": "Fast, cost-effective, good accuracy"
    },
    # Upgrade Option 1: Better accuracy, still fast
    "gpt-3.5-turbo-16k": {
        "model": "gpt-3.5-turbo-16k",
        "temperature": 0.2,
        "description": "Same speed, better context window"
    },
    # Upgrade Option 2: Best accuracy
    "gpt-4": {
        "model": "gpt-4",
        "temperature": 0.2,
        "description": "Best accuracy, 3-5x slower, 10x more expensive"
    },
    # Upgrade Option 3: Good balance
    "gpt-4-turbo": {
        "model": "gpt-4-turbo-preview",
        "temperature": 0.2,
        "description": "Great accuracy, 2x slower, 5x more expensive"
    }
}

# Select which model to use
ACTIVE_MODEL = "gpt-3.5-turbo"  # Switched back to GPT-3.5 for 3x faster responses

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"])  # Enable CORS for all origins for API access

# Check if OpenAI API key is available
print(f"OpenAI API Key configured: {'Yes' if OPENAI_API_KEY else 'No'}")
print(f"Specter API Key configured: {'Yes' if SPECTER_API_KEY else 'No'}")

# Simple in-memory cache for recent searches (last 100 companies)
from collections import OrderedDict
SEARCH_CACHE = OrderedDict()
CACHE_MAX_SIZE = 100

class CompanyDataScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        # Thread pool for concurrent API calls
        self.executor = ThreadPoolExecutor(max_workers=3)
    
    def search_company_info(self, company_name: str) -> Dict[str, Optional[str]]:
        """Search for company information using multiple sources - OPTIMIZED WITH CONCURRENT CALLS"""
        start_time = time.time()
        print(f"\n⏱️ Starting search for {company_name} at {time.strftime('%H:%M:%S')}")
        
        result = {
            'company_name': company_name,
            'description': None,
            'founder_name': None,
            'ceo_name': None
        }
        
        # Common company data (expanded cache to reduce API calls)
        known_companies = {
            'openai': {
                'ceo_name': 'Sam Altman',
                'description': 'OpenAI is an AI research and deployment company that develops and deploys safe and beneficial artificial general intelligence.',
                'technology_focus': 'large language models and AI safety',
                'recent_news': 'launching GPT-4o and securing a $6.6 billion funding round at $157 billion valuation',
                'impressive_metric': 'over 100 million weekly active users on ChatGPT'
            },
            'stripe': {
                'ceo_name': 'Patrick Collison',
                'founder_name': 'Patrick and John Collison',
                'description': 'Stripe is a technology company that builds economic infrastructure for the internet, enabling businesses to accept payments and manage their operations online.',
                'technology_focus': 'payment processing and financial APIs',
                'recent_news': 'reaching $1 trillion in total payment volume processed and launching embedded finance products',
                'impressive_metric': 'processing payments for millions of businesses in over 120 countries'
            },
            'anthropic': {
                'ceo_name': 'Dario Amodei',
                'founder_name': 'Dario Amodei and Daniela Amodei',
                'description': 'Anthropic is an AI safety company that develops reliable, interpretable, and steerable AI systems, including the Claude AI assistant.',
                'technology_focus': 'AI safety and constitutional AI',
                'recent_news': 'raising $2 billion from Google and launching Claude 3 with improved reasoning capabilities',
                'impressive_metric': 'Claude processing billions of tokens daily across enterprise customers'
            },
            'notion': {
                'ceo_name': 'Ivan Zhao',
                'founder_name': 'Ivan Zhao and Simon Last',
                'description': 'Notion is an all-in-one workspace platform that combines notes, databases, kanban boards, wikis, and documents.',
                'technology_focus': 'collaborative productivity software',
                'recent_news': 'introducing Notion AI and surpassing 100 million users globally',
                'impressive_metric': 'over 100 million users across 190+ countries'
            },
            'databricks': {
                'ceo_name': 'Ali Ghodsi',
                'founder_name': 'Ali Ghodsi, Matei Zaharia',
                'description': 'Databricks is a unified analytics platform that provides a cloud-based platform for big data processing and AI workloads.',
                'technology_focus': 'unified data analytics and AI platform',
                'recent_news': 'raising $500M at a $43B valuation and launching Databricks AI to democratize enterprise AI',
                'impressive_metric': 'over 10,000 customers processing exabytes of data daily'
            },
            'canva': {
                'ceo_name': 'Melanie Perkins',
                'founder_name': 'Melanie Perkins, Cliff Obrecht',
                'description': 'Canva is a graphic design platform that enables users to create visual content with drag-and-drop tools and templates.',
                'technology_focus': 'democratizing design through intuitive web-based tools',
                'recent_news': 'achieving $2.3B ARR and launching Magic Studio AI suite for enterprise customers',
                'impressive_metric': 'over 170 million monthly active users creating 250+ designs per second'
            },
            'figma': {
                'ceo_name': 'Dylan Field',
                'founder_name': 'Dylan Field and Evan Wallace',
                'description': 'Figma is a collaborative design platform that enables teams to design, prototype, and gather feedback in one place.',
                'technology_focus': 'browser-based collaborative design and prototyping',
                'recent_news': 'Adobe acquisition blocked by regulators, continuing independent growth with Dev Mode launch',
                'impressive_metric': 'used by over 4 million designers and developers worldwide'
            },
            'discord': {
                'ceo_name': 'Jason Citron',
                'founder_name': 'Jason Citron and Stan Vishnevskiy',
                'description': 'Discord is a communication platform designed for creating communities, offering voice, video, and text chat.',
                'technology_focus': 'real-time communication infrastructure for communities',
                'recent_news': 'expanding beyond gaming with $15B valuation and launching AI-powered features',
                'impressive_metric': 'over 200 million monthly active users across 19 million active servers'
            },
            'plaid': {
                'ceo_name': 'Zach Perret',
                'founder_name': 'Zach Perret and William Hockey',
                'description': 'Plaid is a financial technology company that provides APIs connecting applications to users bank accounts.',
                'technology_focus': 'financial data connectivity and open banking APIs',
                'recent_news': 'powering over 8,000 digital finance apps after Visa acquisition fell through',
                'impressive_metric': 'connecting 12,000+ financial institutions to fintech applications'
            },
            'airtable': {
                'ceo_name': 'Howie Liu',
                'founder_name': 'Howie Liu, Andrew Ofstad, Emmett Nicholas',
                'description': 'Airtable is a cloud-based platform that combines the simplicity of a spreadsheet with the power of a database.',
                'technology_focus': 'low-code database and app development platform',
                'recent_news': 'reaching $11.7B valuation and launching AI-powered workflows for enterprises',
                'impressive_metric': 'over 450,000 organizations building custom applications'
            },
            'whering': {
                'ceo_name': 'Bianca Rangecroft',
                'founder_name': 'Bianca Rangecroft',
                'description': 'Whering is a fashiontech app that helps users digitize their wardrobes and make smarter fashion choices through AI-powered outfit recommendations.',
                'technology_focus': 'AI-powered fashion technology and sustainable wardrobe management',
                'recent_news': 'securing Series A funding and expanding into the US market with celebrity partnerships',
                'impressive_metric': 'over 4 million users actively engaging with their digital closets'
            }
        }
        
        # Check if we have known data for this company
        company_lower = company_name.lower()
        if company_lower in known_companies:
            result.update(known_companies[company_lower])
            print(f"⏱️ Using cached data for {company_name}")
            return result
        
        # Run concurrent operations using ThreadPoolExecutor
        futures = []
        
        # Submit website search
        website_future = self.executor.submit(self._find_and_scrape_website, company_name)
        futures.append(('website', website_future))
        
        # Submit Serper search (if configured)
        if SERPER_API_KEY and SERPER_API_KEY != 'your_serper_api_key_here':
            serper_future = self.executor.submit(self._search_with_serper, company_name)
            futures.append(('serper', serper_future))
        
        # Submit funding news search
        funding_future = self.executor.submit(self._search_recent_funding_news, company_name)
        futures.append(('funding', funding_future))
        
        # Collect results as they complete
        for name, future in futures:
            try:
                if name == 'website':
                    website_data = future.result(timeout=8)  # 8 second timeout
                    if website_data:
                        result.update(website_data)
                    print(f"⏱️ Website search completed")
                    
                elif name == 'serper':
                    serper_info = future.result(timeout=8)  # 8 second timeout
                    print(f"⏱️ Serper API completed")
                    
                    # Log what we got from Serper
                    print(f"📊 SERPER RESULTS:")
                    print(f"  - Description: {'✓' if serper_info.get('description') else '✗'}")
                    print(f"  - CEO: {serper_info.get('ceo_name', 'Not found')}")
                    print(f"  - Funding: {serper_info.get('funding_info', 'Not found')}")
                    print(f"  - Metrics: {serper_info.get('company_metrics', 'Not found')}")
                    
                    if serper_info['description'] and not result['description']:
                        result['description'] = serper_info['description']
                    if serper_info['founder_name'] and not result['founder_name']:
                        result['founder_name'] = serper_info['founder_name']
                    if serper_info['ceo_name'] and not result['ceo_name']:
                        result['ceo_name'] = serper_info['ceo_name']
                    # Add new data from Serper
                    if serper_info.get('funding_info'):
                        result['recent_news'] = serper_info['funding_info']
                    if serper_info.get('company_metrics'):
                        result['impressive_metric'] = serper_info['company_metrics']
                        
                elif name == 'funding':
                    recent_news_info = future.result(timeout=8)  # 8 second timeout
                    if recent_news_info['recent_news']:
                        result['recent_news'] = recent_news_info['recent_news']
                    if recent_news_info['impressive_metric']:
                        result['impressive_metric'] = recent_news_info['impressive_metric']
                    print(f"⏱️ Funding news search completed")
                    
            except Exception as e:
                print(f"⚠️ {name} search failed or timed out: {e}")
        
        total_time = time.time() - start_time
        print(f"⏱️ Total search_company_info took {total_time:.2f}s")
        
        return result
    
    def _find_and_scrape_website(self, company_name: str) -> Optional[Dict]:
        """Find and scrape company website - combined operation"""
        website = self._find_company_website(company_name)
        if website:
            return self._scrape_company_website(website)
        return None
    
    def _find_company_website(self, company_name: str) -> Optional[str]:
        """Try to find the company's official website"""
        # First, try common domain patterns - prioritize .com
        clean_name = company_name.lower().replace(' ', '').replace('.', '').replace(',', '')
        common_domains = [
            f"https://www.{clean_name}.com",
            f"https://{clean_name}.com",
            f"https://www.{clean_name}.io",
            f"https://{clean_name}.io",
            f"https://www.{clean_name}.ai",
            f"https://{clean_name}.ai",
            f"https://www.{clean_name}.co",
            f"https://{clean_name}.co"
        ]
        
        # Check if any of these common patterns work
        for domain in common_domains:
            try:
                response = self.session.head(domain, timeout=2, allow_redirects=True)
                if response.status_code < 400:
                    print(f"Found website via common pattern: {domain}")
                    return domain
            except:
                continue
        
        # If common patterns don't work, try Google search
        search_query = f"{company_name} official website"
        try:
            search_url = f"https://www.google.com/search?q={urllib.parse.quote(search_query)}"
            response = self.session.get(search_url, timeout=5)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for URLs in the page text
            text = soup.get_text()
            
            # Try to find URLs that might be the company website - prioritize .com
            for extension in ['.com', '.io', '.ai', '.co', '.org', '.net']:
                url_pattern = rf'(https?://(?:www\.)?{re.escape(clean_name)}{re.escape(extension)})'
                matches = re.findall(url_pattern, text, re.IGNORECASE)
                if matches:
                    return matches[0]
            
            # Look for any links in the search results
            all_links = soup.find_all('a', href=True)
            for link in all_links:
                href = link.get('href', '')
                if href.startswith('http') and clean_name in href.lower():
                    if not any(blocked in href for blocked in ['google.com', 'youtube.com', 'facebook.com', 'linkedin.com', 'twitter.com', 'wikipedia.org']):
                        print(f"Found website via search: {href}")
                        return href
                        
        except Exception as e:
            print(f"Error finding website: {e}")
        
        # Last resort: use .com as it's most common
        fallback = f"https://www.{clean_name}.com"
        print(f"Using fallback domain: {fallback}")
        return fallback
    
    def _scrape_company_website(self, website_url: str) -> Dict[str, Optional[str]]:
        """Scrape company website for information"""
        result = {'description': None, 'founder_name': None, 'ceo_name': None}
        
        try:
            response = self.session.get(website_url, timeout=5)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Get description from meta tags or about section
            description = self._extract_description(soup)
            if description:
                result['description'] = description
            
            # Look for founder/CEO information
            founder_info = self._extract_founder_info(soup)
            result.update(founder_info)
            
        except Exception as e:
            print(f"Error scraping website {website_url}: {e}")
        
        return result
    
    def _extract_description(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract company description from website"""
        # Try meta description first
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            return meta_desc['content'].strip()
        
        # Try Open Graph description
        og_desc = soup.find('meta', attrs={'property': 'og:description'})
        if og_desc and og_desc.get('content'):
            return og_desc['content'].strip()
        
        # Look for about section or first paragraph
        about_selectors = [
            'p:contains("about")',
            '[class*="about"] p',
            '[id*="about"] p',
            'section p:first-of-type',
            'main p:first-of-type',
            '.hero p',
            '.intro p'
        ]
        
        for selector in about_selectors:
            try:
                elements = soup.select(selector)
                for elem in elements:
                    text = elem.get_text().strip()
                    if len(text) > 50 and len(text) < 500:  # Reasonable description length
                        return text
            except:
                continue
        
        return None
    
    def _extract_founder_info(self, soup: BeautifulSoup) -> Dict[str, Optional[str]]:
        """Extract founder/CEO information from website"""
        result = {'founder_name': None, 'ceo_name': None}
        
        # Look for team, about, or leadership sections
        team_sections = soup.find_all(['div', 'section'], class_=re.compile(r'(team|about|leadership|founder|ceo)', re.I))
        
        # Also check for common patterns in text
        text_content = soup.get_text()
        
        # Look for founder patterns
        founder_patterns = [
            r'(?:founded by|founder[:\s]+|co-founder[:\s]+)([A-Z][a-z]+ [A-Z][a-z]+)',
            r'([A-Z][a-z]+ [A-Z][a-z]+)(?:,?\s*(?:founder|co-founder))',
        ]
        
        for pattern in founder_patterns:
            matches = re.findall(pattern, text_content, re.IGNORECASE)
            if matches:
                result['founder_name'] = matches[0].strip()
                break
        
        # Look for CEO patterns
        ceo_patterns = [
            r'(?:CEO[:\s]+|Chief Executive Officer[:\s]+)([A-Z][a-z]+ [A-Z][a-z]+)',
            r'([A-Z][a-z]+ [A-Z][a-z]+)(?:,?\s*(?:CEO|Chief Executive Officer))',
        ]
        
        for pattern in ceo_patterns:
            matches = re.findall(pattern, text_content, re.IGNORECASE)
            if matches:
                result['ceo_name'] = matches[0].strip()
                break
        
        return result
    
    def _search_with_serper(self, company_name: str) -> Dict[str, Any]:
        """Use Serper API for SINGLE comprehensive web search about the company"""
        result = {
            'description': None, 
            'founder_name': None, 
            'ceo_name': None,
            'recent_news': None,
            'funding_info': None,
            'company_metrics': None,
            'recent_articles': []
        }
        
        if not SERPER_API_KEY or SERPER_API_KEY == 'your_serper_api_key_here':
            print("⚠️ SERPER API NOT CONFIGURED - Using fallback Google search")
            print(f"SERPER_API_KEY exists: {bool(SERPER_API_KEY)}")
            print(f"SERPER_API_KEY value: {SERPER_API_KEY[:10]}..." if SERPER_API_KEY else "None")
            return self._search_google_fallback(company_name)
        
        print(f"✅ SERPER API CONFIGURED - Making SINGLE optimized search for {company_name}")
        
        try:
            # Serper API endpoint
            serper_url = "https://google.serper.dev/search"
            headers = {
                "X-API-KEY": SERPER_API_KEY,
                "Content-Type": "application/json"
            }
            
            # SINGLE OPTIMIZED QUERY combining all needs
            current_year = time.strftime('%Y')
            combined_query = f"{company_name} CEO founder funding round {current_year} valuation Series overview"
            search_data = {
                "q": combined_query,
                "num": 15,  # Get more results in one go
                "tbs": "qdr:y"  # Past year for recent info
            }
            
            print(f"Serper SINGLE search: {combined_query}")
            response = self.session.post(serper_url, json=search_data, headers=headers, timeout=8)
            
            if response.status_code == 200:
                serper_results = response.json()
                
                # Extract from knowledge graph if available
                if 'knowledgeGraph' in serper_results:
                    kg = serper_results['knowledgeGraph']
                    if 'description' in kg:
                        result['description'] = kg['description']
                    if 'attributes' in kg:
                        for attr in kg['attributes']:
                            if 'CEO' in attr:
                                result['ceo_name'] = attr['CEO']
                            elif 'Founder' in attr:
                                result['founder_name'] = attr['Founder']
                
                # Process ALL organic results in ONE PASS
                if 'organic' in serper_results:
                    for item in serper_results['organic']:
                        title = item.get('title', '')
                        snippet = item.get('snippet', '')
                        link = item.get('link', '')
                        combined_text = f"{title} {snippet}"
                        
                        # Store article for reference
                        result['recent_articles'].append({
                            'title': title,
                            'snippet': snippet,
                            'link': link
                        })
                        
                        # Extract description if not found
                        if not result['description'] and len(snippet) > 50 and company_name.lower() in snippet.lower():
                            result['description'] = snippet
                        
                        # Extract funding information
                        funding_pattern = r'\$?([\d.]+)\s*(billion|million|B|M)\s*(?:Series\s*[A-Z]|funding|round|valuation)'
                        matches = re.findall(funding_pattern, combined_text, re.IGNORECASE)
                        
                        if matches and not result['funding_info']:
                            amount = matches[0][0]
                            unit = matches[0][1].lower()
                            amount_str = f"${amount}B" if unit.startswith('b') else f"${amount}M"
                            
                            # Extract series info
                            series_match = re.search(r'Series\s*([A-Z])', combined_text)
                            if series_match:
                                result['funding_info'] = f"{amount_str} Series {series_match.group(1)}"
                            else:
                                result['funding_info'] = f"{amount_str} funding"
                            
                            # Extract valuation if present
                            val_pattern = r'(?:valued?|valuation)\s*(?:at|of)?\s*\$?([\d.]+)\s*(billion|million|B|M)'
                            val_matches = re.findall(val_pattern, combined_text, re.IGNORECASE)
                            if val_matches:
                                val_amount = val_matches[0][0]
                                val_unit = val_matches[0][1].lower()
                                result['company_metrics'] = f"${val_amount}B valuation" if val_unit.startswith('b') else f"${val_amount}M valuation"
                        
                        # Extract CEO/Founder names
                        ceo_patterns = [
                            r'(?:CEO|Chief Executive Officer)[\s,:]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
                            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)[\s,]+(?:CEO|Chief Executive Officer)',
                            r'(?:founder|co-founder)[\s,:]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
                        ]
                        
                        for pattern in ceo_patterns:
                            matches = re.findall(pattern, combined_text)
                            if matches:
                                name = matches[0].strip()
                                if 'CEO' in pattern and not result['ceo_name']:
                                    result['ceo_name'] = name
                                elif 'founder' in pattern.lower() and not result['founder_name']:
                                    result['founder_name'] = name
                                break
            
            print(f"Serper results - Description: {result['description'][:50] if result['description'] else 'None'}...")
            print(f"Serper results - CEO: {result['ceo_name']}, Founder: {result['founder_name']}")
            print(f"Serper results - Funding: {result['funding_info']}, Metrics: {result['company_metrics']}")
            
        except Exception as e:
            print(f"Error with Serper API: {e}")
            return self._search_google_fallback(company_name)
        
        return result
    
    def _search_google_fallback(self, company_name: str) -> Dict[str, Optional[str]]:
        """Fallback to basic Google search if Serper fails"""
        result = {'description': None, 'founder_name': None, 'ceo_name': None}
        
        try:
            # Search for company description
            desc_query = f"{company_name} company what do they do"
            desc_url = f"https://www.google.com/search?q={urllib.parse.quote(desc_query)}"
            response = self.session.get(desc_url, timeout=5)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Get any text that might contain company info
            all_text = soup.get_text()
            if company_name.lower() in all_text.lower():
                # Find sentences containing company name
                sentences = all_text.split('.')
                for sentence in sentences:
                    if company_name.lower() in sentence.lower() and len(sentence) > 50:
                        result['description'] = sentence.strip()[:300] + "..."
                        break
            
            time.sleep(1)  # Be respectful to Google
            
            # Search for founder/CEO
            founder_query = f"{company_name} founder CEO"
            founder_url = f"https://www.google.com/search?q={urllib.parse.quote(founder_query)}"
            response = self.session.get(founder_url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            text_content = soup.get_text()
            
            # Extract names using patterns
            name_patterns = [
                rf'{re.escape(company_name)}.*?(?:founder|CEO|founded by).*?([A-Z][a-z]+ [A-Z][a-z]+)',
                rf'([A-Z][a-z]+ [A-Z][a-z]+).*?(?:founder|CEO).*?{re.escape(company_name)}',
            ]
            
            for pattern in name_patterns:
                matches = re.findall(pattern, text_content, re.IGNORECASE)
                if matches:
                    name = matches[0].strip()
                    if not result['founder_name']:
                        result['founder_name'] = name
                    break
            
        except Exception as e:
            print(f"Error searching Google: {e}")
        
        return result
    
    def _search_recent_funding_news(self, company_name: str) -> Dict[str, Optional[str]]:
        """Search for recent funding news and company updates"""
        result = {'recent_news': None, 'impressive_metric': None}
        
        try:
            # Search for recent funding news with current year
            current_year = time.strftime('%Y')
            funding_query = f"{company_name} funding round {current_year} series million billion"
            funding_url = f"https://www.google.com/search?q={urllib.parse.quote(funding_query)}&tbs=qdr:y"  # tbs=qdr:y limits to past year
            
            response = self.session.get(funding_url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for funding amounts in the search results
            text_content = soup.get_text()
            
            # Pattern to find funding amounts
            funding_patterns = [
                rf'{company_name}.*?(?:raised|raises|secured|closed|announced).*?\$?([\d.]+)\s*(billion|million|B|M)\s*(?:Series\s*[A-Z]|funding|round)',
                rf'\$?([\d.]+)\s*(billion|million|B|M).*?(?:Series\s*[A-Z]|funding|round).*?{company_name}',
                rf'{company_name}.*?(?:Series\s*[A-Z]).*?\$?([\d.]+)\s*(billion|million|B|M)',
            ]
            
            for pattern in funding_patterns:
                matches = re.findall(pattern, text_content, re.IGNORECASE)
                if matches:
                    amount = matches[0][0]
                    unit = matches[0][1].lower()
                    if unit.startswith('b'):
                        amount_str = f"${amount}B"
                    else:
                        amount_str = f"${amount}M"
                    
                    # Try to find the series information
                    series_match = re.search(rf'Series\s*([A-Z])', text_content, re.IGNORECASE)
                    if series_match:
                        series = series_match.group(1)
                        result['recent_news'] = f"closing a {amount_str} Series {series} funding round"
                    else:
                        result['recent_news'] = f"securing {amount_str} in funding"
                    break
            
            # If no funding news, look for other recent achievements
            if not result['recent_news']:
                achievement_query = f"{company_name} announcement partnership product launch {current_year}"
                achievement_url = f"https://www.google.com/search?q={urllib.parse.quote(achievement_query)}&tbs=qdr:m"  # past month
                
                response = self.session.get(achievement_url, timeout=10)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for achievement patterns
                achievement_patterns = [
                    rf'{company_name}.*?(?:announced|launches|partners|introduces|unveils)(.*?)(?:\.|$)',
                    rf'{company_name}.*?(?:growth|expansion|milestone)(.*?)(?:\.|$)',
                ]
                
                text_content = soup.get_text()
                for pattern in achievement_patterns:
                    matches = re.findall(pattern, text_content[:2000], re.IGNORECASE)  # Check first 2000 chars
                    if matches:
                        achievement = matches[0].strip()[:100]
                        if len(achievement) > 20:
                            result['recent_news'] = achievement
                            break
            
        except Exception as e:
            print(f"Error searching for recent news: {e}")
        
        return result
    
    def find_email_with_specter(self, company_name: str, person_name: str = None, domain: str = None) -> Optional[str]:
        """Find email address using Specter API"""
        if not SPECTER_API_KEY:
            print("Specter API key not configured")
            return None
        
        try:
            # If we don't have a domain, try to extract it from the company website
            if not domain and company_name:
                website = self._find_company_website(company_name)
                if website:
                    # Extract domain from URL
                    from urllib.parse import urlparse
                    parsed_url = urlparse(website)
                    domain = parsed_url.netloc.replace('www.', '')
                    print(f"Found domain: {domain}")
            
            if not domain:
                print("No domain found, cannot proceed with Specter API")
                return None
            
            # Specter API base URL
            specter_base_url = "https://app.tryspecter.com/api/v1"
            
            # Headers for Specter API
            headers = {
                "X-API-Key": SPECTER_API_KEY,
                "Content-Type": "application/json"
            }
            
            # Step 1: Enrich company to get company ID
            print(f"Enriching company with domain: {domain}")
            
            company_url = f"{specter_base_url}/companies"
            company_data = {
                "domain": domain
            }
            
            print(f"Calling Specter company enrichment: POST {company_url}")
            print(f"Request data: {company_data}")
            
            response = self.session.post(company_url, json=company_data, headers=headers, timeout=10)
            
            print(f"Specter company enrichment response status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"Company enrichment failed: {response.status_code} - {response.text[:500]}")
                return None
            
            company_result = response.json()
            print(f"Company enrichment response type: {type(company_result)}")
            print(f"Company enrichment response: {str(company_result)[:500]}...")  # First 500 chars
            
            # Handle if result is a list (multiple companies found)
            if isinstance(company_result, list):
                if not company_result:
                    print("No companies found in Specter")
                    return None
                # Take the first company
                company_data = company_result[0]
                print(f"Found {len(company_result)} companies, using first one")
            else:
                company_data = company_result
            
            company_id = company_data.get('id')
            
            if not company_id:
                print("No company ID returned from enrichment")
                return None
            
            print(f"Got company ID: {company_id}")
            
            # Step 2: Get company people
            people_url = f"{specter_base_url}/companies/{company_id}/people"
            print(f"Getting company people: GET {people_url}")
            
            people_response = self.session.get(people_url, headers=headers, timeout=10)
            
            print(f"Company people response status: {people_response.status_code}")
            
            if people_response.status_code != 200:
                print(f"Failed to get company people: {people_response.status_code}")
                return None
            
            people = people_response.json()
            print(f"Found {len(people) if isinstance(people, list) else 0} people at company")
            
            if not people or not isinstance(people, list):
                print("No people found at company")
                return None
            
            # Debug: print first person to see structure
            if people:
                print(f"First person object: {people[0]}")
            
            # Step 3: Look for CEO/Founder or specific person
            target_person_id = None
            
            if person_name:
                # Look for specific person by name
                for person in people:
                    if person.get('full_name', '').lower() == person_name.lower():
                        target_person_id = person.get('person_id')
                        print(f"Found target person {person_name} with ID: {target_person_id}")
                        break
            
            # If no specific person found, look for executives
            if not target_person_id:
                for person in people[:10]:  # Check first 10 people
                    name = person.get('full_name', '')
                    title = person.get('title', '').lower()
                    is_founder = person.get('is_founder', False)
                    seniority = person.get('seniority', '').lower()
                    
                    print(f"Checking person: {name} - {person.get('title')}")
                    
                    # Check if this person is a founder, CEO, or executive
                    if (is_founder or 
                        any(role in title for role in ['ceo', 'chief executive', 'founder', 'co-founder']) or
                        'executive' in seniority):
                        target_person_id = person.get('person_id')
                        print(f"Found executive: {name} ({person.get('title')})")
                        break
            
            if not target_person_id:
                print("No target person found")
                return None
            
            # Step 4: Get person's email
            email_url = f"{specter_base_url}/people/{target_person_id}/email"
            print(f"Getting person's email: GET {email_url}")
            
            email_response = self.session.get(email_url, headers=headers, timeout=10)
            
            print(f"Email response status: {email_response.status_code}")
            
            if email_response.status_code == 200:
                email_data = email_response.json()
                email = email_data.get('email')
                if email:
                    print(f"Found email: {email} (type: {email_data.get('type')})")
                    return email
            elif email_response.status_code == 204:
                print("No email found for this person")
            else:
                print(f"Failed to get email: {email_response.status_code}")
            
        except Exception as e:
            print(f"Error finding email with Specter: {e}")
            import traceback
            traceback.print_exc()
        
        return None
    
    def get_specter_company_data(self, company_name: str, domain: str = None) -> Dict[str, Any]:
        """Get comprehensive company data from Specter API"""
        start_time = time.time()
        print(f"\n🔍 Starting Specter search for {company_name}")
        
        specter_data = {
            'company_info': None,
            'people': [],
            'executives': [],
            'domain': domain
        }
        
        if not SPECTER_API_KEY:
            return specter_data
        
        try:
            # Get domain if not provided
            if not domain:
                website = self._find_company_website(company_name)
                if website:
                    from urllib.parse import urlparse
                    parsed_url = urlparse(website)
                    domain = parsed_url.netloc.replace('www.', '')
                    specter_data['domain'] = domain
            
            if not domain:
                return specter_data
            
            # Specter API setup
            specter_base_url = "https://app.tryspecter.com/api/v1"
            headers = {
                "X-API-Key": SPECTER_API_KEY,
                "Content-Type": "application/json"
            }
            
            # Get company data
            response = self.session.post(
                f"{specter_base_url}/companies",
                json={"domain": domain},
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                company_result = response.json()
                if isinstance(company_result, list) and company_result:
                    specter_data['company_info'] = company_result[0]
                else:
                    specter_data['company_info'] = company_result
                
                # Get company people if we have company ID
                company_id = specter_data['company_info'].get('id') if specter_data['company_info'] else None
                if company_id:
                    people_response = self.session.get(
                        f"{specter_base_url}/companies/{company_id}/people",
                        headers=headers,
                        timeout=10
                    )
                    
                    if people_response.status_code == 200:
                        people = people_response.json()
                        if isinstance(people, list):
                            specter_data['people'] = people
                            
                            # Extract executives
                            for person in people:
                                title = person.get('title', '').lower()
                                is_founder = person.get('is_founder', False)
                                seniority = person.get('seniority', '').lower()
                                
                                if (is_founder or 
                                    any(role in title for role in ['ceo', 'chief executive', 'founder', 'co-founder', 'cto', 'coo', 'cfo']) or
                                    'executive' in seniority):
                                    specter_data['executives'].append(person)
        
        except Exception as e:
            print(f"Error getting Specter data: {e}")
        
        print(f"⏱️ Specter search took {time.time() - start_time:.2f}s")
        return specter_data
    
    def enhance_with_openai(self, company_data: Dict[str, Optional[str]], specter_data: Dict[str, Any] = None) -> Dict[str, Optional[str]]:
        """Use OpenAI to synthesize and enhance data from all sources (Specter, Serper, web scraping)"""
        if not OPENAI_API_KEY:
            print("OpenAI API key not configured")
            return company_data
        
        print(f"Enhancing data for company: {company_data['company_name']}")
        try:
            # Extract Specter information if available
            specter_info = ""
            if specter_data and specter_data.get('company_info'):
                company_info = specter_data['company_info']
                specter_info = f"""
                
                === SPECTER DATA (Company Database) ===
                - Official Company Name: {company_info.get('organization_name', 'N/A')}
                - Company Description: {company_info.get('description', 'N/A')}
                - Company Rank: {company_info.get('organization_rank', 'N/A')}
                - Primary Role: {company_info.get('primary_role', 'N/A')}
                - Domain: {specter_data.get('domain', 'N/A')}
                """
                
                if specter_data.get('executives'):
                    specter_info += "\n\nEXECUTIVE TEAM FROM SPECTER:"
                    for exec in specter_data['executives'][:5]:  # Top 5 executives
                        specter_info += f"\n- {exec.get('full_name', 'Unknown')} - {exec.get('title', 'Unknown Title')}"
                        if exec.get('is_founder'):
                            specter_info += " (Founder)"
                
                if specter_data.get('people'):
                    specter_info += f"\n\nTotal Employees in Database: {len(specter_data['people'])}"
            
            # Add Serper search results context
            serper_context = ""
            if company_data.get('recent_news') and '$' in str(company_data.get('recent_news', '')):
                serper_context += f"\n\n=== RECENT FUNDING (from Serper search) ===\n{company_data['recent_news']}"
            if company_data.get('impressive_metric'):
                serper_context += f"\nKey Metric: {company_data['impressive_metric']}"
            
            # Create a comprehensive prompt that synthesizes all data
            prompt = f"""
            You are a world-class venture capital analyst at HOF Capital researching {company_data['company_name']} for a personalized outreach email.
            
            Your task is to synthesize ALL available data sources and provide the most accurate, up-to-date information.
            
            === DATA SOURCES ===
            
            1. WEB SCRAPING DATA:
            - Company: {company_data['company_name']}
            - Description: {company_data.get('description', 'No description found')}
            - CEO/Founder: {company_data.get('ceo_name') or company_data.get('founder_name') or 'Unknown'}
            - Website Data: {company_data.get('recent_news', 'None')}
            
            2. SERPER API SEARCH RESULTS:
            {serper_context if serper_context else '- No recent funding or metrics found via search'}
            
            3. SPECTER DATABASE:
            {specter_info if specter_info else '- No Specter data available'}
            
            === SYNTHESIS INSTRUCTIONS ===
            
            Based on ALL the information above, provide the MOST ACCURATE information by:
            1. Prioritizing Specter data for executive names (it's most reliable)
            2. Using Serper search results for recent funding/news (most current)
            3. Combining all sources for the best company description
            
            Provide:
            1. A compelling 1-2 sentence description that captures what makes this company investment-worthy
            2. The CORRECT CEO/founder name (check Specter executives first, then other sources)
            3. Their unique technology/market edge
            4. The MOST RECENT achievement (prioritize 2024, then late 2023) - BE SPECIFIC with amounts/dates
            5. The MOST IMPRESSIVE metric with actual numbers
            
            CRITICAL ACCURACY RULES:
            - If Serper found funding info (e.g., "$2B from Google"), use that EXACT amount
            - If Specter lists executives, use those EXACT names
            - For achievements, be HYPER-SPECIFIC: dates, amounts, partner names
            - NEVER make up information - only use what's provided
            
            Format your response EXACTLY as:
            DESCRIPTION: [1-2 sentences, investment-focused]
            CEO_NAME: [exact name - check Specter executives first]
            TECHNOLOGY: [their specific edge/approach]
            RECENT_NEWS: [most recent achievement with EXACT details]
            IMPRESSIVE_METRIC: [specific number with context - MUST HAVE NUMBERS]
            """
            
            import openai
            openai.api_key = OPENAI_API_KEY
            
            response = openai.ChatCompletion.create(
                model=MODEL_CONFIG[ACTIVE_MODEL]["model"],
                messages=[
                    {"role": "system", "content": """You are a world-class venture capital analyst at HOF Capital conducting deep due diligence. Your analysis should be:
1. HYPER-SPECIFIC: Use exact numbers, dates, names, and details from the provided data
2. INVESTMENT-FOCUSED: Frame everything through the lens of what makes this company attractive to VCs
3. ACCURATE: If data conflicts, prioritize Specter (real-time) > web scraping > general knowledge
4. COMPREHENSIVE: Connect multiple data points to form insights
5. CURRENT: Focus on 2023-2024 developments, not outdated information"""},
                    {"role": "user", "content": prompt}
                ],
                temperature=MODEL_CONFIG[ACTIVE_MODEL]["temperature"],
                max_tokens=500
            )
            
            # Parse the response
            content = response['choices'][0]['message']['content']
            
            # Extract enhanced information
            description_match = re.search(r'DESCRIPTION:\s*(.+?)(?=CEO_NAME:|TECHNOLOGY:|RECENT_NEWS:|IMPRESSIVE_METRIC:|$)', content, re.DOTALL)
            ceo_match = re.search(r'CEO_NAME:\s*(.+?)(?=DESCRIPTION:|TECHNOLOGY:|RECENT_NEWS:|IMPRESSIVE_METRIC:|$)', content, re.DOTALL)
            tech_match = re.search(r'TECHNOLOGY:\s*(.+?)(?=DESCRIPTION:|CEO_NAME:|RECENT_NEWS:|IMPRESSIVE_METRIC:|$)', content, re.DOTALL)
            news_match = re.search(r'RECENT_NEWS:\s*(.+?)(?=DESCRIPTION:|CEO_NAME:|TECHNOLOGY:|IMPRESSIVE_METRIC:|$)', content, re.DOTALL)
            metric_match = re.search(r'IMPRESSIVE_METRIC:\s*(.+?)(?=DESCRIPTION:|CEO_NAME:|TECHNOLOGY:|RECENT_NEWS:|$)', content, re.DOTALL)
            
            if description_match:
                enhanced_desc = description_match.group(1).strip()
                if enhanced_desc and enhanced_desc.lower() != 'unknown':
                    company_data['description'] = enhanced_desc
            
            if ceo_match:
                ceo_name = ceo_match.group(1).strip()
                if ceo_name and ceo_name.lower() != 'unknown':
                    if not company_data.get('ceo_name'):
                        company_data['ceo_name'] = ceo_name
            
            if tech_match:
                tech = tech_match.group(1).strip()
                if tech and tech.lower() != 'unknown':
                    company_data['technology_focus'] = tech
            
            if news_match:
                news = news_match.group(1).strip()
                if news and news.lower() != 'unknown':
                    # Only update if we don't already have recent news from real-time search
                    if not company_data.get('recent_news'):
                        company_data['recent_news'] = news
                    elif 'closing a $' not in company_data.get('recent_news', ''):
                        # If we have news but it's not specific funding info, enhance it
                        company_data['recent_news'] = news
            
            if metric_match:
                metric = metric_match.group(1).strip()
                if metric and metric.lower() != 'unknown':
                    company_data['impressive_metric'] = metric
            
            print(f"Enhanced data - CEO: {company_data.get('ceo_name')}, News: {company_data.get('recent_news', 'None')[:100] if company_data.get('recent_news') else 'None'}")
            
        except Exception as e:
            error_msg = str(e)
            if "quota" in error_msg.lower():
                print("⚠️  OpenAI API quota exceeded - please add credits to your OpenAI account")
                print("   Visit: https://platform.openai.com/account/billing")
            else:
                print(f"Error enhancing with OpenAI: {e}")
            import traceback
            traceback.print_exc()
        
        return company_data

    def __del__(self):
        """Cleanup thread pool on deletion"""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)

def generate_email(company_data: Dict[str, Optional[str]], specter_executives: list = None) -> str:
    """Generate a highly personalized outreach email using all available data"""
    company_name = company_data['company_name']
    ceo_name = company_data['ceo_name'] or company_data['founder_name'] or '[CEO/Founder Name]'
    
    # Extract first name for greeting
    first_name = ceo_name.split()[0] if ceo_name and ceo_name != '[CEO/Founder Name]' else ceo_name
    
    # Get company details
    description = company_data.get('description', '')
    recent_news = company_data.get('recent_news', '')
    technology_focus = company_data.get('technology_focus', '')
    impressive_metric = company_data.get('impressive_metric', '')
    
    # Fixed email template bottom half (NEVER CHANGES)
    fixed_bottom = f"""For quick context, I'm an Investor at HOF Capital, a $3B+ AUM multi-stage VC firm that has backed transformative ventures including OpenAI, xAI, Epic Games, UiPath, and Rimac Automobili. Each year, we selectively partner with visionary founders tackling critical societal challenges through groundbreaking technology. Additionally, our LP base (https://hofcapital.com/partners/) includes influential leaders across consumer and technology industries, providing extensive strategic value.

I'd love to set up a conversation to learn more about {company_name} and explore potential ways we could support your impactful journey. Here's my calendar: https://app.usemotion.com/meet/tahseen-rashid/trapgm

Cheers,
Tahseen Rashid
Investor | HOF Capital"""
    
    # If we have OpenAI API key, generate ONLY the personalized intro
    if OPENAI_API_KEY:
        try:
            import openai
            openai.api_key = OPENAI_API_KEY
            
            # Simplified training examples - hardcoded for reliability
            print(f"=== GENERATING EMAIL FOR {company_name} ===")
            print(f"Using model: {MODEL_CONFIG[ACTIVE_MODEL]['model']}")
            
            # Hardcode key training examples for production reliability
            selected_examples = [
                '"Hi Sam, I\'ve been closely tracking OpenAI\'s extraordinary growth - hitting 200M weekly active users while maintaining your mission of ensuring AGI benefits all of humanity is truly remarkable. The way you\'ve balanced rapid commercialization with responsible AI development, especially with the recent GPT-4o launch, demonstrates the kind of transformative leadership we love to support."',
                '"Hi Patrick, Stripe crossing $1 trillion in total payment volume is a defining moment for global internet commerce. The infrastructure you\'ve built has become so fundamental that it\'s hard to imagine the modern internet economy without it - that\'s the kind of category-defining impact we\'re passionate about supporting."',
                '"Hi Dario, Claude 3\'s breakthrough performance combined with your recent $7.3B raise at an $18.4B valuation is reshaping the entire AI landscape. Your commitment to AI safety while shipping products that genuinely compete with and often surpass GPT-4 shows that responsible development and commercial success aren\'t mutually exclusive."'
            ]
            
            print(f"Loaded {len(selected_examples)} training examples")
            print(f"Recent news: {recent_news[:100] if recent_news else 'None'}")
            print(f"Metric: {impressive_metric[:100] if impressive_metric else 'None'}")
            
            # Create a prompt for ONLY the intro paragraph
            prompt = f"""
            Write ONLY a brief 2-3 sentence personalized intro paragraph for a VC outreach email from Tahseen Rashid to {first_name} at {company_name}.
            
            COMPANY DETAILS:
            - Company: {company_name}
            - CEO/Founder: {ceo_name}
            - What they do: {description}
            - Recent achievement: {recent_news}
            - Key metric: {impressive_metric}
            
            REQUIREMENTS:
            1. Start with "Hi {first_name},"
            2. In 2-3 sentences MAX, show genuine interest by:
               - Mentioning a SPECIFIC recent achievement, news, or impressive metric
               - Briefly showing you understand what they do
               - Being authentic and conversational
            3. DO NOT include any HOF Capital context - that comes later
            4. DO NOT include call-to-action - that comes later
            5. Just write the greeting and 2-3 sentences of personalized interest
            
            CRITICAL ACCURACY RULES:
            - If recent news mentions a funding round, use the EXACT amount (e.g., "$150M Series D")
            - Be specific about dates when available (e.g., "your January 2024 announcement")
            - Name specific products, partnerships, or people when mentioned
            - Avoid generic phrases like "impressive growth" without specifics
            - If a metric is provided, use the exact number
            
            PERFECT EXAMPLES FROM TRAINING DATA:
            {chr(10).join([f'"{ex}"' for ex in selected_examples]) if selected_examples else '''
            "Hi Sam, I've been closely tracking OpenAI's extraordinary growth - hitting 200M weekly active users while maintaining your mission of ensuring AGI benefits all of humanity is truly remarkable. The way you've balanced rapid commercialization with responsible AI development, especially with the recent GPT-4o launch, demonstrates the kind of transformative leadership we love to support."
            
            "Hi Patrick, Stripe crossing $1 trillion in total payment volume is a defining moment for global internet commerce. The infrastructure you've built has become so fundamental that it's hard to imagine the modern internet economy without it - that's the kind of category-defining impact we're passionate about supporting."
            
            "Hi Melanie, Canva's achievement of 170M+ monthly active users and $2.3B in ARR while democratizing design globally is extraordinary. Your vision of empowering everyone to create has fundamentally changed how billions approach visual communication - that's precisely the kind of transformative impact we seek to accelerate."
            '''}
            
            WINNING FORMULAS:
            - Achievement + Impact: "[Specific achievement] is [adjective]. [How this impacts industry] - that's [connection to HOF thesis]."
            - Metric + Vision: "[Impressive metric] while [broader mission] is [adjective]. [Strategic insight] [what HOF values]."
            - Category Creation: "[What they're doing differently] shows you're [creating/redefining category]. [Why this matters] - that's the kind of [transformation] [HOF connection]."
            
            BAD EXAMPLES (NEVER WRITE LIKE THIS):
            "Hi [Name], I've been impressed by your company's growth." (Too generic)
            "Hi [Name], Congrats on your recent funding!" (Not specific enough)
            "Hi [Name], Your company is doing great things in the industry." (No substance)
            "Hi [Name], I wanted to reach out about investment opportunities." (Too salesy)
            
            SPECIFIC PATTERNS TO FOLLOW:
            - Funding: "your $150M Series D at a $2B valuation"
            - Metrics: "reaching 10 million active users" or "growing revenue 300% YoY to $50M ARR"
            - Product launches: "the launch of [Product Name] which already has 100K users"
            - Partnerships: "your partnership with Microsoft to integrate [specific feature]"
            - Market position: "becoming the de facto standard for [specific use case]"
            
            Write ONLY the intro paragraph now:
            """
            
            response = openai.ChatCompletion.create(
                model=MODEL_CONFIG[ACTIVE_MODEL]["model"],
                messages=[
                    {"role": "system", "content": """You are Tahseen Rashid, an investor at HOF Capital, writing the opening of a personalized outreach email. Your writing should be:

1. AUTHENTIC: Sound like a real person who has genuinely researched the company, not a template
2. SPECIFIC: Reference exact metrics, dates, product names, funding amounts - no generic statements
3. INSIGHTFUL: Show you understand not just what they do, but why it matters in the market
4. CONCISE: Maximum 2-3 sentences that pack a punch
5. CONVERSATIONAL: Professional but warm, like reaching out to a potential partner, not cold sales

Remember: This is just the intro. The HOF Capital context and call-to-action come later."""},
                    {"role": "user", "content": prompt}
                ],
                temperature=MODEL_CONFIG[ACTIVE_MODEL]["temperature"],
                max_tokens=150
            )
            
            intro = response['choices'][0]['message']['content'].strip()
            
            # Log the generated intro for quality monitoring
            print(f"\n=== GPT-4 Generated Intro ===")
            print(f"Company: {company_name}")
            print(f"Model: {MODEL_CONFIG[ACTIVE_MODEL]['model']}")
            print(f"Generated intro:\n{intro}")
            print("="*30)
            
            # Ensure the intro doesn't already contain the fixed content
            if "HOF Capital" in intro or "calendar" in intro.lower():
                # If it does, extract only the first paragraph
                intro_lines = intro.split('\n')
                intro = '\n'.join([line for line in intro_lines[:2] if "HOF Capital" not in line and "calendar" not in line.lower()])
            
            # Combine intro with fixed bottom
            email = f"{intro}\n\n{fixed_bottom}"
            
            return email
            
        except Exception as e:
            print(f"Error generating personalized intro: {e}")
            # Fall through to default template
    
    # Fallback template if OpenAI fails
    if recent_news and impressive_metric:
        intro = f"Hi {first_name}, I've been following {company_name}'s incredible progress - congratulations on {recent_news}! {impressive_metric} is truly impressive and speaks to the transformative impact you're having."
    elif recent_news:
        intro = f"Hi {first_name}, I've been following {company_name}'s journey and was excited to see you {recent_news}. The work you're doing in {description.lower() if description else 'your space'} is truly compelling."
    elif impressive_metric:
        intro = f"Hi {first_name}, I've been tracking {company_name}'s growth and {impressive_metric} really caught my attention. Your approach to {description.lower() if description else 'the market'} is exactly the kind of innovation we love to support."
    else:
        intro = f"Hi {first_name}, I've been following {company_name} with great interest. Your work in {description.lower() if description else 'building transformative technology'} aligns perfectly with the kind of visionary companies we partner with."
    
    # Combine intro with fixed bottom
    email = f"{intro}\n\n{fixed_bottom}"
    
    return email

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({
        'status': 'healthy', 
        'service': 'HOF Capital VC Outreach',
        'api_keys_configured': {
            'openai': bool(OPENAI_API_KEY),
            'specter': bool(SPECTER_API_KEY)
        }
    }), 200

@app.route('/api/generate-outreach', methods=['POST'])
def generate_outreach():
    try:
        request_start = time.time()
        
        # Check for API key authentication
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            provided_key = auth_header.split(' ')[1]
            if provided_key != HOF_API_KEY:
                return jsonify({'error': 'Invalid API key'}), 401
        
        data = request.get_json()
        company_name = data.get('company_name', '').strip()
        
        if not company_name:
            return jsonify({'error': 'Company name is required'}), 400
        
        print(f"\n🚀 === Processing company: {company_name} at {time.strftime('%H:%M:%S')} ===")
        print(f"OpenAI API Key available: {'Yes' if OPENAI_API_KEY else 'No'}")
        
        # Check cache first
        cache_key = company_name.lower()
        if cache_key in SEARCH_CACHE:
            print(f"💾 CACHE HIT for {company_name}!")
            cached_data = SEARCH_CACHE[cache_key]
            # Move to end (most recently used)
            SEARCH_CACHE.move_to_end(cache_key)
            
            # Generate fresh email even for cached data
            email_content = generate_email(cached_data['company_data'], cached_data.get('specter_executives', []))
            
            total_time = time.time() - request_start
            print(f"\n✅ TOTAL REQUEST TIME (from cache): {total_time:.2f}s")
            
            return jsonify({
                'success': True,
                'data': {
                    'company_name': cached_data['company_data'].get('company_name'),
                    'ceo_name': cached_data['company_data'].get('ceo_name') or cached_data['company_data'].get('founder_name'),
                    'ceo_email': cached_data.get('ceo_email'),
                    'email_content': email_content,
                    'subject_line': f"HOF Capital - Partnership Opportunity with {cached_data['company_data'].get('company_name')}",
                    'company_details': {
                        'description': cached_data['company_data'].get('description'),
                        'technology_focus': cached_data['company_data'].get('technology_focus'),
                        'recent_news': cached_data['company_data'].get('recent_news'),
                        'impressive_metric': cached_data['company_data'].get('impressive_metric')
                    }
                },
                'metadata': {
                    'generated_at': time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime()),
                    'api_version': '1.0',
                    'processing_time_seconds': round(total_time, 2),
                    'cache_hit': True,
                    'debug': {
                        'specter_configured': bool(SPECTER_API_KEY),
                        'attempted_email_search': bool(cached_data.get('ceo_email') is not None)
                    }
                }
            })
        
        # Not in cache, proceed with normal flow
        # Scrape company information
        scraper = CompanyDataScraper()
        scrape_start = time.time()
        
        # Create executor for concurrent operations
        with ThreadPoolExecutor(max_workers=2) as executor:
            # Start web scraping
            scrape_future = executor.submit(scraper.search_company_info, company_name)
            
            # Start Specter search concurrently
            specter_future = executor.submit(scraper.get_specter_company_data, company_name)
            
            # Get web scraping results
            company_data = scrape_future.result(timeout=15)
            print(f"⏱️ Total web scraping took {time.time() - scrape_start:.2f}s")
            print(f"Initial scrape results - CEO: {company_data.get('ceo_name')}, Founder: {company_data.get('founder_name')}, Description: {company_data.get('description')[:50] if company_data.get('description') else 'None'}...")
            
            # Get Specter results
            specter_data = specter_future.result(timeout=10)
            print(f"⏱️ Total Specter API took {time.time() - scrape_start:.2f}s")
        
        # Enhance with OpenAI using both data sources
        enhance_start = time.time()
        company_data = scraper.enhance_with_openai(company_data, specter_data)
        print(f"⏱️ OpenAI enhancement took {time.time() - enhance_start:.2f}s")
        
        # If we found executives in Specter, update CEO name
        if specter_data.get('executives'):
            for exec in specter_data['executives']:
                if exec.get('is_founder') or 'ceo' in exec.get('title', '').lower():
                    company_data['ceo_name'] = exec.get('full_name')
                    break
        
        # Try to find CEO/Founder email address
        ceo_email = None
        if company_data.get('ceo_name') or company_data.get('founder_name'):
            person_name = company_data.get('ceo_name') or company_data.get('founder_name')
            ceo_email = scraper.find_email_with_specter(company_name, person_name)
        
        # Generate email with Specter executive data
        email_content = generate_email(company_data, specter_data.get('executives', []))
        
        # Add to cache before returning
        cache_data = {
            'company_data': company_data,
            'specter_executives': specter_data.get('executives', []),
            'ceo_email': ceo_email
        }
        
        # Add to cache with size limit
        SEARCH_CACHE[cache_key] = cache_data
        if len(SEARCH_CACHE) > CACHE_MAX_SIZE:
            # Remove oldest item
            SEARCH_CACHE.popitem(last=False)
        
        # Structure the response for easy integration
        total_time = time.time() - request_start
        print(f"\n✅ TOTAL REQUEST TIME: {total_time:.2f}s")
        print(f"💾 Cached result for future requests")
        
        if total_time > 25:
            print(f"⚠️  WARNING: Request took {total_time:.2f}s - approaching 30s timeout limit!")
        
        return jsonify({
            'success': True,
            'data': {
                'company_name': company_data.get('company_name'),
                'ceo_name': company_data.get('ceo_name') or company_data.get('founder_name'),
                'ceo_email': ceo_email,  # New field with discovered email
                'email_content': email_content,
                'subject_line': f"HOF Capital - Partnership Opportunity with {company_data.get('company_name')}",
                'company_details': {
                    'description': company_data.get('description'),
                    'technology_focus': company_data.get('technology_focus'),
                    'recent_news': company_data.get('recent_news'),
                    'impressive_metric': company_data.get('impressive_metric')
                }
            },
                            'metadata': {
                    'generated_at': time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime()),
                    'api_version': '1.0',
                    'processing_time_seconds': round(total_time, 2),
                    'cache_hit': False,
                    'debug': {
                        'specter_configured': bool(SPECTER_API_KEY),
                        'attempted_email_search': bool(ceo_email is not None or (company_data.get('ceo_name') or company_data.get('founder_name')))
                    }
                }
            })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to generate outreach email'
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001) 