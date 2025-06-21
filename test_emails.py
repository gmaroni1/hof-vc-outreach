#!/usr/bin/env python3
"""
Training and Testing Script for HOF Capital VC Outreach System
This script helps you test and refine the email generation quality
"""

import os
import json
import time
from datetime import datetime
from app import CompanyDataScraper, generate_email

# Test companies with known good data
TEST_COMPANIES = [
    {
        "name": "OpenAI",
        "expected_elements": ["ChatGPT", "Sam Altman", "GPT-4", "100M users", "$10B valuation"],
        "category": "AI/ML"
    },
    {
        "name": "Stripe",
        "expected_elements": ["Patrick Collison", "payment", "fintech", "$95B valuation"],
        "category": "Fintech"
    },
    {
        "name": "Anthropic",
        "expected_elements": ["Claude", "AI safety", "Dario Amodei", "$4B Series C"],
        "category": "AI/ML"
    },
    {
        "name": "Figma",
        "expected_elements": ["Dylan Field", "design", "Adobe", "$20B acquisition"],
        "category": "Design/SaaS"
    },
    {
        "name": "Canva",
        "expected_elements": ["Melanie Perkins", "design platform", "visual", "$40B valuation"],
        "category": "Design/SaaS"
    },
    {
        "name": "Databricks",
        "expected_elements": ["Ali Ghodsi", "data", "lakehouse", "$43B valuation"],
        "category": "Data/Analytics"
    },
    {
        "name": "Scale AI",
        "expected_elements": ["Alexandr Wang", "data labeling", "AI training", "$7.3B valuation"],
        "category": "AI/ML"
    },
    {
        "name": "Ramp",
        "expected_elements": ["Eric Glyman", "corporate cards", "expense", "$8.1B valuation"],
        "category": "Fintech"
    }
]

def test_single_company(company_name, expected_elements=None):
    """Test email generation for a single company"""
    print(f"\n{'='*60}")
    print(f"Testing: {company_name}")
    print(f"{'='*60}")
    
    start_time = time.time()
    
    # Initialize scraper
    scraper = CompanyDataScraper()
    
    # Get company data
    print("1. Scraping company information...")
    company_data = scraper.search_company_info(company_name)
    
    # Get Specter data
    print("2. Fetching Specter data...")
    specter_data = scraper.get_specter_company_data(company_name)
    
    # Enhance with OpenAI
    print("3. Enhancing with GPT-4...")
    company_data = scraper.enhance_with_openai(company_data, specter_data)
    
    # Find email if possible
    print("4. Searching for executive email...")
    ceo_email = None
    if company_data.get('ceo_name') or company_data.get('founder_name'):
        person_name = company_data.get('ceo_name') or company_data.get('founder_name')
        if person_name:  # Additional check to ensure person_name is not None
            ceo_email = scraper.find_email_with_specter(company_name, person_name)
    
    # Generate email
    print("5. Generating personalized email...")
    email_content = generate_email(company_data, specter_data.get('executives', []))
    
    end_time = time.time()
    
    # Extract just the intro (before "For quick context")
    intro_end = email_content.find("For quick context")
    intro = email_content[:intro_end].strip() if intro_end > 0 else email_content
    
    # Results
    print(f"\n{'='*60}")
    print("RESULTS:")
    print(f"{'='*60}")
    print(f"Company: {company_data.get('company_name')}")
    print(f"CEO/Founder: {company_data.get('ceo_name') or company_data.get('founder_name') or 'Not found'}")
    print(f"Email Found: {ceo_email or 'No'}")
    print(f"Recent News: {company_data.get('recent_news', 'None')}")
    print(f"Key Metric: {company_data.get('impressive_metric', 'None')}")
    print(f"Processing Time: {end_time - start_time:.2f} seconds")
    
    print(f"\n{'='*60}")
    print("GENERATED INTRO:")
    print(f"{'='*60}")
    print(intro)
    
    # Quality check
    if expected_elements:
        print(f"\n{'='*60}")
        print("QUALITY CHECK:")
        print(f"{'='*60}")
        found_elements = []
        missing_elements = []
        
        for element in expected_elements:
            if element.lower() in email_content.lower():
                found_elements.append(element)
            else:
                missing_elements.append(element)
        
        print(f"✅ Found ({len(found_elements)}/{len(expected_elements)}): {', '.join(found_elements)}")
        if missing_elements:
            print(f"❌ Missing: {', '.join(missing_elements)}")
        
        accuracy_score = (len(found_elements) / len(expected_elements)) * 100
        print(f"\nAccuracy Score: {accuracy_score:.1f}%")
    
    return {
        "company": company_name,
        "intro": intro,
        "full_email": email_content,
        "ceo_name": company_data.get('ceo_name') or company_data.get('founder_name'),
        "ceo_email": ceo_email,
        "recent_news": company_data.get('recent_news'),
        "key_metric": company_data.get('impressive_metric'),
        "processing_time": end_time - start_time,
        "accuracy_score": accuracy_score if expected_elements else None
    }

def run_full_test_suite():
    """Run tests on all test companies"""
    results = []
    total_accuracy = 0
    companies_with_scores = 0
    
    print("\n" + "="*60)
    print("HOF CAPITAL VC OUTREACH - MODEL TESTING SUITE")
    print("="*60)
    print(f"Testing {len(TEST_COMPANIES)} companies...")
    print(f"Model: GPT-4")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    for test_company in TEST_COMPANIES:
        try:
            result = test_single_company(
                test_company["name"], 
                test_company.get("expected_elements")
            )
            results.append(result)
            
            if result["accuracy_score"] is not None:
                total_accuracy += result["accuracy_score"]
                companies_with_scores += 1
                
        except Exception as e:
            print(f"\n❌ Error testing {test_company['name']}: {e}")
            continue
        
        # Small delay between tests
        time.sleep(2)
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Total companies tested: {len(results)}")
    print(f"Average processing time: {sum(r['processing_time'] for r in results) / len(results):.2f} seconds")
    
    if companies_with_scores > 0:
        print(f"Average accuracy score: {total_accuracy / companies_with_scores:.1f}%")
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"test_results_{timestamp}.json"
    
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"\nResults saved to: {filename}")
    
    return results

def interactive_test():
    """Interactive testing mode for specific companies"""
    print("\n" + "="*60)
    print("INTERACTIVE TESTING MODE")
    print("="*60)
    print("Enter company names to test (or 'quit' to exit)")
    
    while True:
        company_name = input("\nCompany name: ").strip()
        
        if company_name.lower() == 'quit':
            break
        
        if not company_name:
            continue
        
        try:
            result = test_single_company(company_name)
            
            # Ask for feedback
            print("\n" + "="*60)
            print("FEEDBACK")
            print("="*60)
            rating = input("Rate this email (1-5, or press Enter to skip): ").strip()
            
            if rating:
                feedback = input("What could be improved? ")
                
                # Save feedback
                with open("training_feedback.txt", "a") as f:
                    f.write(f"\n{'='*60}\n")
                    f.write(f"Company: {company_name}\n")
                    f.write(f"Rating: {rating}/5\n")
                    f.write(f"Feedback: {feedback}\n")
                    f.write(f"Intro: {result['intro']}\n")
                    f.write(f"Timestamp: {datetime.now()}\n")
                
                print("✅ Feedback saved!")
                
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            # Run full test suite
            run_full_test_suite()
        elif sys.argv[1] == "interactive":
            # Interactive mode
            interactive_test()
        else:
            # Test specific company
            test_single_company(sys.argv[1])
    else:
        print("Usage:")
        print("  python test_emails.py test          # Run full test suite")
        print("  python test_emails.py interactive   # Interactive testing mode")
        print("  python test_emails.py <company>     # Test specific company") 