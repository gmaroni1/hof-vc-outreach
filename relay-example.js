// Example: How to call HOF VC Outreach API from Relay.app or any automation platform

// For Relay.app Custom Code Action:
async function generateOutreachEmail(companyName) {
  const API_URL = 'https://your-deployed-api.com/api/generate-outreach';
  const API_KEY = 'your-hof-api-key';
  
  try {
    const response = await fetch(API_URL, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${API_KEY}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        company_name: companyName
      })
    });
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    
    const result = await response.json();
    
    if (result.success) {
      return {
        email_content: result.data.email_content,
        subject_line: result.data.subject_line,
        ceo_name: result.data.ceo_name,
        company_details: result.data.company_details
      };
    } else {
      throw new Error(result.error || 'Failed to generate email');
    }
  } catch (error) {
    console.error('Error calling HOF API:', error);
    throw error;
  }
}

// Example usage in Relay.app:
// 1. Add this as a Custom Code action
// 2. Pass {{company_name}} from your trigger or previous step
// 3. Use the returned data in subsequent actions (send email, update CRM, etc.)

// Test locally:
if (require.main === module) {
  generateOutreachEmail('OpenAI')
    .then(result => console.log('Success:', result))
    .catch(error => console.error('Error:', error));
} 