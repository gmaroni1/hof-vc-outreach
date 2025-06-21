#!/usr/bin/env python3
"""
Quick script to add training examples to improve email generation
"""

import json
import os
from datetime import datetime

def add_example():
    print("\n=== ADD TRAINING EXAMPLE ===")
    print("This will help improve the model by adding good examples\n")
    
    # Get details
    company = input("Company name: ").strip()
    ceo_name = input("CEO/Founder name: ").strip()
    recent_achievement = input("Recent achievement (be specific): ").strip()
    key_metric = input("Key metric (with numbers): ").strip()
    
    print("\nNow write the PERFECT intro (2-3 sentences):")
    print("Example: Hi Sam, I've been following OpenAI's incredible trajectory...")
    perfect_intro = input("\nPerfect intro: ").strip()
    
    # Rating
    category = input("\nCategory (AI/ML, Fintech, SaaS, etc.): ").strip()
    notes = input("Any special notes about this example: ").strip()
    
    # Create example entry
    example = {
        "company": company,
        "ceo_name": ceo_name,
        "recent_achievement": recent_achievement,
        "key_metric": key_metric,
        "perfect_intro": perfect_intro,
        "category": category,
        "notes": notes,
        "timestamp": datetime.now().isoformat()
    }
    
    # Load existing examples
    examples_file = "training_examples.json"
    if os.path.exists(examples_file):
        with open(examples_file, 'r') as f:
            examples = json.load(f)
    else:
        examples = []
    
    # Add new example
    examples.append(example)
    
    # Save
    with open(examples_file, 'w') as f:
        json.dump(examples, f, indent=2)
    
    print(f"\n✅ Example saved! Total examples: {len(examples)}")
    
    # Also append to a markdown file for easy reading
    with open("TRAINING_EXAMPLES.md", 'a') as f:
        if os.path.getsize("TRAINING_EXAMPLES.md") == 0:
            f.write("# Training Examples for HOF Capital VC Outreach\n\n")
        
        f.write(f"\n## {company} - {category}\n")
        f.write(f"**CEO**: {ceo_name}\n")
        f.write(f"**Achievement**: {recent_achievement}\n")
        f.write(f"**Metric**: {key_metric}\n")
        f.write(f"**Perfect Intro**:\n> {perfect_intro}\n")
        if notes:
            f.write(f"**Notes**: {notes}\n")
        f.write(f"*Added: {datetime.now().strftime('%Y-%m-%d')}*\n")
    
    print("Also saved to TRAINING_EXAMPLES.md for easy reference")
    
    # Ask if they want to add another
    another = input("\nAdd another example? (y/n): ").strip().lower()
    if another == 'y':
        add_example()

def view_examples():
    """View all training examples"""
    examples_file = "training_examples.json"
    if not os.path.exists(examples_file):
        print("No training examples found yet!")
        return
    
    with open(examples_file, 'r') as f:
        examples = json.load(f)
    
    print(f"\n=== TRAINING EXAMPLES ({len(examples)} total) ===\n")
    
    # Group by category
    by_category = {}
    for ex in examples:
        cat = ex.get('category', 'Other')
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(ex)
    
    for category, items in sorted(by_category.items()):
        print(f"\n{category.upper()} ({len(items)} examples)")
        print("-" * 40)
        
        for ex in items:
            print(f"\n{ex['company']} - {ex['ceo_name']}")
            print(f"Achievement: {ex['recent_achievement']}")
            print(f"Intro: {ex['perfect_intro'][:100]}...")

def export_for_prompt():
    """Export examples in a format ready to paste into the prompt"""
    examples_file = "training_examples.json"
    if not os.path.exists(examples_file):
        print("No training examples found yet!")
        return
    
    with open(examples_file, 'r') as f:
        examples = json.load(f)
    
    print("\n=== EXAMPLES FOR GPT-4 PROMPT ===")
    print("Copy and paste these into your prompt:\n")
    
    # Get the 5 most recent examples
    recent = sorted(examples, key=lambda x: x['timestamp'], reverse=True)[:5]
    
    for ex in recent:
        print(f'"{ex["perfect_intro"]}"')
        print()
    
    print("\n=== PATTERN EXAMPLES ===")
    print("Funding:", [ex['recent_achievement'] for ex in examples if 'funding' in ex['recent_achievement'].lower()][:3])
    print("Metrics:", [ex['key_metric'] for ex in examples][:3])

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "view":
        view_examples()
    elif len(sys.argv) > 1 and sys.argv[1] == "export":
        export_for_prompt()
    else:
        print("\nOptions:")
        print("1. Add new training example")
        print("2. View all examples")
        print("3. Export for prompt")
        
        choice = input("\nChoice (1-3): ").strip()
        
        if choice == "1":
            add_example()
        elif choice == "2":
            view_examples()
        elif choice == "3":
            export_for_prompt() 