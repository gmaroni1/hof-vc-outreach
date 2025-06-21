# HOF Capital VC Outreach - Model Training Guide

## Overview
This guide helps you optimize GPT-4's performance for generating accurate, personalized VC outreach emails.

## Quick Start

### 1. Run the Test Suite
```bash
python test_emails.py test
```
This tests 8 major companies and provides accuracy scores.

### 2. Interactive Testing
```bash
python test_emails.py interactive
```
Test specific companies and provide feedback in real-time.

### 3. Test Single Company
```bash
python test_emails.py "Company Name"
```

## Understanding the Quality Metrics

### Accuracy Score
- Measures how many expected elements appear in the email
- Target: 80%+ accuracy
- Elements checked: CEO name, funding amounts, metrics, product names

### Processing Time
- GPT-4 typical: 5-10 seconds
- Includes: scraping + Specter API + GPT-4 generation
- Acceptable range: 5-15 seconds

## Common Issues & Solutions

### Issue 1: Generic/Vague Intros
**Symptom**: "I've been impressed by your company's growth"

**Solution**: 
- Check if web scraping found recent news
- Verify Specter API is returning data
- Add the company to test suite with expected elements

### Issue 2: Wrong CEO/Founder Name
**Symptom**: Using outdated or incorrect executive names

**Solution**:
- Specter data should override web scraping
- Check if company domain is being found correctly
- May need to add domain mapping for edge cases

### Issue 3: Outdated Information
**Symptom**: Referencing old funding rounds or metrics

**Solution**:
- The `_search_recent_funding_news` function focuses on past year
- GPT-4 is instructed to prioritize 2023-2024 data
- Consider adjusting time filters in search

### Issue 4: Missing Recent Achievements
**Symptom**: Not mentioning recent funding/product launches

**Solution**:
- Check Google search results manually
- May need to adjust search query patterns
- Consider adding more news sources

## Improving Accuracy

### 1. Collect Feedback
Run interactive mode and rate emails 1-5:
```bash
python test_emails.py interactive
```
Feedback is saved to `training_feedback.txt`

### 2. Analyze Patterns
Look for common issues across multiple emails:
- Are certain types of companies problematic?
- Do specific industries need different approaches?
- Are there repeated phrases to avoid?

### 3. Update Prompts
Based on feedback, update prompts in `app.py`:

```python
# Add more good examples
"Hi [Name], Your recent $50M Series B led by Sequoia..."

# Add bad patterns to avoid
"Hi [Name], I noticed your company..." (too generic)

# Add industry-specific patterns
- Biotech: "FDA approval", "clinical trials", "Phase 2"
- Fintech: "transaction volume", "AUM", "regulatory approval"
```

### 4. Test Edge Cases
Companies that often need special handling:
- Recent pivots or rebrands
- Stealth mode companies
- International companies
- B2B enterprise companies

## Best Practices

### 1. Weekly Testing
Run the full test suite weekly:
```bash
python test_emails.py test
```
Track accuracy trends over time.

### 2. Save Good Examples
When you get a perfect email, save it as a reference:
- Add to the "GOOD EXAMPLES" in the prompt
- Use specific patterns in future prompts

### 3. Monitor API Responses
Check logs for what GPT-4 generates:
```
=== GPT-4 Generated Intro ===
Company: [Name]
Model: gpt-4
Generated intro: [Content]
```

### 4. Domain Verification
For companies where email discovery fails:
1. Manually check their domain
2. Add to a domain mapping if needed
3. Verify Specter has data for that domain

## Advanced Optimization

### 1. Temperature Tuning
Current: 0.2 (low = consistent)
- Lower (0.1): More predictable, less creative
- Higher (0.3-0.4): More variety, risk of inconsistency

### 2. Prompt Engineering Tips
- Be explicit about what NOT to do
- Provide 3-5 excellent examples
- Use consistent formatting in examples
- Include edge cases in instructions

### 3. Company Categories
Consider different approaches for:
- Pre-seed/Seed companies (focus on vision)
- Growth stage (focus on metrics)
- Industry leaders (focus on market position)
- Technical deep tech (focus on innovation)

## Maintenance Schedule

### Daily
- Monitor error logs for API failures
- Check email generation quality

### Weekly
- Run test suite
- Review feedback file
- Update problem company list

### Monthly
- Analyze accuracy trends
- Update prompt examples
- Review and update expected elements
- Clean up test results files

## Troubleshooting

### API Errors
- Check OpenAI API credits
- Verify Specter API key is valid
- Monitor rate limits

### Poor Quality Emails
1. Test the company manually
2. Check what data was found
3. Review GPT-4 prompt
4. Add specific instructions if needed

### Slow Performance
- Normal: 5-10 seconds
- If slower: Check network, API status
- Consider caching for repeated companies

## Contact
For prompt engineering assistance or model issues:
- Review test results in `test_results_*.json`
- Check feedback in `training_feedback.txt`
- Logs show exact prompts and responses 