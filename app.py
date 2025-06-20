from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import re
import time
import urllib.parse
from typing import Dict, Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"])  # Enable CORS for all origins for API access

# Check if OpenAI API key is available
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
HOF_API_KEY = os.getenv('HOF_API_KEY', 'your-secure-api-key-here')  # Add your own API key for authentication
print(f"OpenAI API Key configured: {'Yes' if OPENAI_API_KEY else 'No'}")

class CompanyDataScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def search_company_info(self, company_name: str) -> Dict[str, Optional[str]]:
        """Search for company information using multiple sources"""
        result = {
            'company_name': company_name,
            'description': None,
            'founder_name': None,
            'ceo_name': None
        }
        
        # Common company data (fallback for demo purposes)
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
            return result
        
        # Try to get company website first
        website = self._find_company_website(company_name)
        if website:
            company_info = self._scrape_company_website(website)
            result.update(company_info)
        
        # If we don't have enough info, try Google search
        if not result['description'] or not (result['founder_name'] or result['ceo_name']):
            google_info = self._search_google(company_name)
            if google_info['description'] and not result['description']:
                result['description'] = google_info['description']
            if google_info['founder_name'] and not result['founder_name']:
                result['founder_name'] = google_info['founder_name']
            if google_info['ceo_name'] and not result['ceo_name']:
                result['ceo_name'] = google_info['ceo_name']
        
        # Search for recent funding news and updates
        recent_news_info = self._search_recent_funding_news(company_name)
        if recent_news_info['recent_news']:
            result['recent_news'] = recent_news_info['recent_news']
        if recent_news_info['impressive_metric']:
            result['impressive_metric'] = recent_news_info['impressive_metric']
        
        return result
    
    def _find_company_website(self, company_name: str) -> Optional[str]:
        """Try to find the company's official website"""
        search_query = f"{company_name} official website"
        try:
            search_url = f"https://www.google.com/search?q={urllib.parse.quote(search_query)}"
            response = self.session.get(search_url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for the first organic result
            search_results = soup.find_all('div', class_='g')
            for result in search_results[:3]:  # Check first 3 results
                link_elem = result.find('a')
                if link_elem and 'href' in link_elem.attrs:
                    url = link_elem['href']
                    if url.startswith('http') and not any(blocked in url for blocked in ['google.com', 'youtube.com', 'facebook.com', 'linkedin.com', 'twitter.com']):
                        return url
        except Exception as e:
            print(f"Error finding website: {e}")
        
        return None
    
    def _scrape_company_website(self, website_url: str) -> Dict[str, Optional[str]]:
        """Scrape company website for information"""
        result = {'description': None, 'founder_name': None, 'ceo_name': None}
        
        try:
            response = self.session.get(website_url, timeout=10)
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
    
    def _search_google(self, company_name: str) -> Dict[str, Optional[str]]:
        """Search Google for company information"""
        result = {'description': None, 'founder_name': None, 'ceo_name': None}
        
        try:
            # Search for company description
            desc_query = f"{company_name} company what do they do"
            desc_url = f"https://www.google.com/search?q={urllib.parse.quote(desc_query)}"
            response = self.session.get(desc_url, timeout=10)
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
    
    def enhance_with_openai(self, company_data: Dict[str, Optional[str]]) -> Dict[str, Optional[str]]:
        """Use OpenAI to enhance company data and generate better descriptions"""
        if not OPENAI_API_KEY:
            print("OpenAI API key not configured")
            return company_data
        
        print(f"Enhancing data for company: {company_data['company_name']}")
        try:
            # Create a prompt to enhance the company information
            prompt = f"""
            Company: {company_data['company_name']}
            Current Description: {company_data.get('description', 'No description found')}
            CEO/Founder: {company_data.get('ceo_name') or company_data.get('founder_name') or 'Unknown'}
            Recent News Found: {company_data.get('recent_news', 'None')}
            
            Based on your knowledge and the information provided above, provide:
            1. A compelling 1-2 sentence description of what this company does and their key innovation
            2. The name of the CEO or founder (if known)
            3. What cutting-edge technology or approach they're using
            4. If no recent news was found above, provide any recent achievement or development you know of
            5. A specific impressive metric or fact (like number of users, revenue growth, market share, etc.)
            
            Important: If recent news was already found (shown above), use that information and enhance it with context.
            
            Format your response as:
            DESCRIPTION: [description]
            CEO_NAME: [name or "Unknown"]
            TECHNOLOGY: [their key technology/approach]
            RECENT_NEWS: [if no news found above, provide recent development; otherwise enhance the existing news]
            IMPRESSIVE_METRIC: [specific number or achievement]
            """
            
            import openai
            openai.api_key = OPENAI_API_KEY
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a venture capital analyst helping to research companies for outreach. Provide accurate, specific information with real metrics and achievements when known."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=400
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

def generate_email(company_data: Dict[str, Optional[str]]) -> str:
    """Generate the outreach email using the enhanced template"""
    company_name = company_data['company_name']
    ceo_name = company_data['ceo_name'] or company_data['founder_name'] or '[CEO/Founder Name]'
    
    # Extract first name for greeting
    first_name = ceo_name.split()[0] if ceo_name and ceo_name != '[CEO/Founder Name]' else ceo_name
    
    # Get company details
    description = company_data.get('description', '')
    recent_news = company_data.get('recent_news', '')
    technology_focus = company_data.get('technology_focus', '')
    impressive_metric = company_data.get('impressive_metric', '')
    
    # If we have OpenAI API key, generate a more customized opening
    if OPENAI_API_KEY and (description or recent_news):
        try:
            import openai
            openai.api_key = OPENAI_API_KEY
            
            # Create a prompt for a personalized opening
            prompt = f"""
            Generate a personalized opening paragraph for a VC outreach email to {company_name}.
            
            Company: {company_name}
            CEO/Founder: {ceo_name}
            Description: {description}
            Technology Focus: {technology_focus}
            Recent News: {recent_news}
            Impressive Metric: {impressive_metric}
            
            Create an opening that:
            1. Starts with "Hope you're doing well!"
            2. Congratulates them on a specific achievement or milestone (use the recent news if available, or reference their growth/technology)
            3. Mentions a specific impressive metric or accomplishment if known (use the impressive metric field)
            4. Shows genuine excitement about what they're building
            5. Keep it to 2-3 sentences max
            
            Example format:
            "Hope you're doing well! Congrats on [specific achievement]! My name is Tahseen Rashid and I'm truly excited by how [company] is [what they're doing]. [Specific impressive fact about the company]!"
            
            Return ONLY the opening paragraph, nothing else.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are helping write personalized VC outreach emails. Be specific, enthusiastic, and reference real achievements."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=150
            )
            
            custom_opening = response['choices'][0]['message']['content'].strip()
            
            # Ensure it starts with the greeting and includes the name
            if "Hope you're doing well!" not in custom_opening:
                custom_opening = f"Hope you're doing well! {custom_opening}"
            if "Tahseen Rashid" not in custom_opening:
                custom_opening = custom_opening.replace("My name is", "My name is Tahseen Rashid and I'm")
            
        except Exception as e:
            print(f"Error generating custom opening: {e}")
            # Fallback to default opening
            custom_opening = None
    else:
        custom_opening = None
    
    # Use custom opening if generated, otherwise use a default
    if custom_opening:
        opening_paragraph = custom_opening
    else:
        # Default opening when we don't have enough information
        if recent_news:
            opening_paragraph = f"Hope you're doing well! Congrats on {recent_news.lower()}! My name is Tahseen Rashid and I'm truly excited by how {company_name} is transforming the industry."
        else:
            opening_paragraph = f"Hope you're doing well! Congrats on the growth and momentum with {company_name}! My name is Tahseen Rashid and I'm truly excited by what you're building."
    
    # Generate the full email
    email = f"""Hi {first_name},

{opening_paragraph}

For quick context, I'm an Investor at HOF Capital, a $3B+ AUM multi-stage VC firm that has backed transformative ventures including OpenAI, xAI, Epic Games, UiPath, and Rimac Automobili. Each year, we selectively partner with visionary founders tackling critical societal challenges through groundbreaking technology. Additionally, our LP base includes influential leaders across consumer and technology industries, providing extensive strategic value.

I'd love to set up a conversation to learn more about {company_name} and explore potential ways we could support your impactful journey. Here's my calendar.

Cheers,
Tahseen Rashid
Investor | HOF Capital"""
    
    return email

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({'status': 'healthy', 'service': 'HOF Capital VC Outreach'}), 200

@app.route('/api/generate-outreach', methods=['POST'])
def generate_outreach():
    try:
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
        
        print(f"\n=== Processing company: {company_name} ===")
        print(f"OpenAI API Key available: {'Yes' if OPENAI_API_KEY else 'No'}")
        
        # Scrape company information
        scraper = CompanyDataScraper()
        company_data = scraper.search_company_info(company_name)
        print(f"Initial scrape results - CEO: {company_data.get('ceo_name')}, Founder: {company_data.get('founder_name')}, Description: {company_data.get('description')[:50] if company_data.get('description') else 'None'}...")
        
        # Enhance with OpenAI if available
        company_data = scraper.enhance_with_openai(company_data)
        
        # Generate email
        email_content = generate_email(company_data)
        
        # Structure the response for easy integration
        return jsonify({
            'success': True,
            'data': {
                'company_name': company_data.get('company_name'),
                'ceo_name': company_data.get('ceo_name') or company_data.get('founder_name'),
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
                'api_version': '1.0'
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