#!/usr/bin/env python3
"""Test multiple companies to ensure stability and measure performance"""

import requests
import json
import time
import concurrent.futures
from typing import List, Dict, Tuple

# Configuration
LOCAL_URL = "http://localhost:5001/api/generate-outreach"
DEPLOYED_URL = "https://hof-vc-outreach.onrender.com/api/generate-outreach"
API_KEY = "sA7Zno0jpyrTGrAKDBMRwSUfSdxMaiDGF2Ypi-2F8u8"

# Test companies - mix of known and challenging ones
TEST_COMPANIES = [
    # Known companies (should be fast)
    "OpenAI",
    "Stripe", 
    "Anthropic",
    "Notion",
    
    # Challenging companies
    "Databricks",
    "Canva",
    "SpaceX",
    "Figma",
    "Discord",
    "Plaid",
    
    # Lesser known companies
    "Whering",
    "Airtable",
    "Vercel",
    "Linear",
    "Replit"
]

def test_company(company: str, use_deployed: bool = False) -> Tuple[str, Dict, float]:
    """Test a single company and return results"""
    url = DEPLOYED_URL if use_deployed else LOCAL_URL
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY
    }
    
    start_time = time.time()
    
    try:
        response = requests.post(
            url,
            headers=headers,
            json={"company_name": company},
            timeout=35  # 35s timeout to catch 30s timeouts
        )
        
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            return (company, {
                "success": True,
                "ceo": data.get("data", {}).get("ceo_name"),
                "email": data.get("data", {}).get("ceo_email"),
                "has_news": bool(data.get("data", {}).get("company_details", {}).get("recent_news")),
                "processing_time": data.get("metadata", {}).get("processing_time_seconds", elapsed),
                "status_code": response.status_code
            }, elapsed)
        else:
            return (company, {
                "success": False,
                "error": f"Status {response.status_code}",
                "text": response.text[:200],
                "status_code": response.status_code
            }, elapsed)
            
    except requests.exceptions.Timeout:
        elapsed = time.time() - start_time
        return (company, {
            "success": False,
            "error": "Timeout",
            "elapsed": elapsed
        }, elapsed)
        
    except Exception as e:
        elapsed = time.time() - start_time
        return (company, {
            "success": False,
            "error": str(e),
            "elapsed": elapsed
        }, elapsed)

def test_all_companies(companies: List[str], use_deployed: bool = False, parallel: bool = False):
    """Test all companies and print results"""
    print(f"\n{'='*60}")
    print(f"Testing {len(companies)} companies on {'DEPLOYED' if use_deployed else 'LOCAL'} server")
    print(f"Parallel: {parallel}")
    print(f"{'='*60}\n")
    
    results = []
    total_start = time.time()
    
    if parallel:
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_company = {
                executor.submit(test_company, company, use_deployed): company 
                for company in companies
            }
            
            for future in concurrent.futures.as_completed(future_to_company):
                results.append(future.result())
    else:
        for company in companies:
            print(f"Testing {company}...", end="", flush=True)
            result = test_company(company, use_deployed)
            results.append(result)
            print(f" {result[2]:.2f}s {'✓' if result[1]['success'] else '✗'}")
    
    total_elapsed = time.time() - total_start
    
    # Print summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    
    successes = [r for r in results if r[1]["success"]]
    failures = [r for r in results if not r[1]["success"]]
    
    print(f"\nSuccessful: {len(successes)}/{len(results)}")
    print(f"Failed: {len(failures)}/{len(results)}")
    print(f"Total time: {total_elapsed:.2f}s")
    print(f"Average time per company: {total_elapsed/len(results):.2f}s")
    
    if successes:
        print(f"\n✅ Successful companies:")
        for company, data, elapsed in sorted(successes, key=lambda x: x[2]):
            print(f"  - {company}: {elapsed:.2f}s, CEO: {data.get('ceo', 'Unknown')}, Email: {'✓' if data.get('email') else '✗'}")
    
    if failures:
        print(f"\n❌ Failed companies:")
        for company, data, elapsed in failures:
            print(f"  - {company}: {elapsed:.2f}s, Error: {data.get('error', 'Unknown')}")
            if data.get('text'):
                print(f"    Response: {data['text']}")
    
    # Timing analysis
    times = [r[2] for r in results]
    print(f"\n⏱️  Timing Analysis:")
    print(f"  - Fastest: {min(times):.2f}s")
    print(f"  - Slowest: {max(times):.2f}s")
    print(f"  - Average: {sum(times)/len(times):.2f}s")
    
    # Warning about slow requests
    slow_requests = [r for r in results if r[2] > 20]
    if slow_requests:
        print(f"\n⚠️  Slow requests (>20s):")
        for company, _, elapsed in sorted(slow_requests, key=lambda x: -x[2]):
            print(f"  - {company}: {elapsed:.2f}s")

if __name__ == "__main__":
    # Test locally first
    print("\n🏠 LOCAL TESTING")
    test_all_companies(TEST_COMPANIES[:5], use_deployed=False, parallel=False)
    
    # Then test deployed version
    print("\n\n☁️  DEPLOYED TESTING")
    test_all_companies(TEST_COMPANIES, use_deployed=True, parallel=False)
    
    # Stress test with parallel requests
    print("\n\n🔥 PARALLEL STRESS TEST (Deployed)")
    test_all_companies(TEST_COMPANIES[:10], use_deployed=True, parallel=True) 