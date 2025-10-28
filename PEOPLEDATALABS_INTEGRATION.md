# PeopleDataLabs Integration for DataEnrichmentAgent

## 🔄 **Migration from Clearbit to PeopleDataLabs**

The `DataEnrichmentAgent` has been successfully updated to use **PeopleDataLabs API** instead of Clearbit for comprehensive data enrichment.

## 🆕 **What's New**

### **Enhanced Company Enrichment**
- **Company Domain**: Website URL
- **Company Description**: Business summary
- **Company Industry**: Industry classification
- **Company Size**: Employee count
- **Company Revenue**: Annual revenue
- **Company Technologies**: Tech stack used
- **Company Location**: City and country
- **Social Profiles**: LinkedIn, Twitter, Facebook, Crunchbase
- **Company Founded**: Founding year
- **Company Type**: Business type
- **NAICS/SIC Codes**: Industry classification codes
- **Company Tags**: Categorized tags

### **Advanced Contact Enrichment**
- **Contact Title**: Job title
- **Contact Role**: Specific role
- **Contact Seniority**: Seniority level
- **Contact Department**: Department
- **Contact Experience**: Work experience
- **Contact Education**: Educational background
- **Contact Skills**: Professional skills
- **Contact Languages**: Languages spoken
- **Contact Location**: Personal location
- **Social Profiles**: LinkedIn, Twitter, Facebook, GitHub
- **Contact Phone**: Phone numbers
- **Demographics**: Birth year, gender, nationality
- **Industry Info**: Industry and sub-industry
- **Company Context**: Current company details

## 🔧 **Setup Instructions**

### **1. Get PeopleDataLabs API Key**
1. Visit https://www.peopledatalabs.com/
2. Sign up for an account
3. Get your API key from the dashboard
4. Note: Free tier includes limited credits

### **2. Update Environment Variables**
Add to your `.env` file:
```bash
# PeopleDataLabs API Configuration
PEOPLEDATALABS_API_KEY=your_peopledatalabs_api_key_here
```

### **3. Update Workflow Configuration**
The `workflow.json` has been updated to use PeopleDataLabs:
```json
{
  "id": "enrichment",
  "agent": "DataEnrichmentAgent",
  "instructions": "Enrich lead data using PeopleDataLabs API for comprehensive company and contact information.",
  "tools": [
    {"name": "PeopleDataLabs", "config": {"api_key": "{{PEOPLEDATALABS_API_KEY}}"}}
  ]
}
```

## 🧪 **Testing the Integration**

### **Run the Test Script**
```bash
python test_peopledatalabs.py
```

### **Expected Output**
- ✅ API key validation
- ✅ Company enrichment data
- ✅ Contact enrichment data
- ✅ Comprehensive lead profiles

## 📊 **API Endpoints Used**

### **Company Enrichment**
- **Endpoint**: `https://api.peopledatalabs.com/v5/company/enrich`
- **Method**: GET
- **Parameters**: `name` (company name)
- **Response**: Company details, technologies, social profiles

### **Person Enrichment**
- **Endpoint**: `https://api.peopledatalabs.com/v5/person/enrich`
- **Method**: GET
- **Parameters**: `email` (contact email)
- **Response**: Person details, skills, experience, company context

## 🔍 **Data Quality Features**

### **Fallback Strategy**
1. **Primary**: PeopleDataLabs API enrichment
2. **Fallback**: Basic contact data extraction
3. **Error Handling**: Graceful degradation with error flags

### **Data Validation**
- Email format validation
- Company name normalization
- Data type consistency
- Missing data handling

## 📈 **Benefits of PeopleDataLabs**

### **vs. Clearbit**
- ✅ **More Comprehensive**: 50+ data points per contact
- ✅ **Better Coverage**: Global database with 1B+ profiles
- ✅ **Real-time Data**: Fresh, up-to-date information
- ✅ **Advanced Filtering**: Industry, skills, location filters
- ✅ **Social Profiles**: LinkedIn, Twitter, GitHub, Facebook
- ✅ **Company Context**: Current company details for contacts

### **Data Points Comparison**
| Feature | Clearbit | PeopleDataLabs |
|---------|----------|----------------|
| Company Domain | ✅ | ✅ |
| Company Description | ✅ | ✅ |
| Company Industry | ✅ | ✅ |
| Company Size | ✅ | ✅ |
| Company Revenue | ✅ | ✅ |
| Company Technologies | ✅ | ✅ |
| Contact Title | ❌ | ✅ |
| Contact Skills | ❌ | ✅ |
| Contact Experience | ❌ | ✅ |
| Contact Education | ❌ | ✅ |
| Social Profiles | Limited | Comprehensive |
| Demographics | ❌ | ✅ |
| Phone Numbers | ❌ | ✅ |

## 🚀 **Usage in Workflow**

### **Input Data**
```json
{
  "leads": [
    {
      "company": "TechFlow Solutions",
      "contact_name": "Sarah Johnson",
      "email": "sarah.johnson@techflowsolutions.com",
      "linkedin": "https://linkedin.com/in/sarahjohnson1"
    }
  ]
}
```

### **Output Data**
```json
{
  "enriched_leads": [
    {
      "company": "TechFlow Solutions",
      "contact_name": "Sarah Johnson",
      "email": "sarah.johnson@techflowsolutions.com",
      "company_domain": "techflowsolutions.com",
      "company_description": "AI-powered workflow automation platform",
      "company_industry": "Software Development",
      "company_size": 150,
      "company_technologies": ["Python", "React", "AWS", "Docker"],
      "contact_title": "VP of Sales",
      "contact_role": "Sales Director",
      "contact_seniority": "Senior",
      "contact_skills": ["Sales", "CRM", "Lead Generation"],
      "contact_linkedin": "https://linkedin.com/in/sarahjohnson1",
      "contact_phone": "+1-555-0123",
      "enriched": true
    }
  ]
}
```

## 🔧 **Troubleshooting**

### **Common Issues**
1. **API Key Invalid**: Check key format and validity
2. **Rate Limits**: Monitor API usage and credits
3. **Data Not Found**: Some contacts may not be in database
4. **Network Issues**: Check connectivity and firewall settings

### **Error Handling**
- Graceful degradation on API failures
- Detailed error logging
- Fallback to basic enrichment
- Error flags in output data

## 📚 **API Documentation**
- **PeopleDataLabs Docs**: https://docs.peopledatalabs.com/
- **Company API**: https://docs.peopledatalabs.com/docs/company-enrichment-api
- **Person API**: https://docs.peopledatalabs.com/docs/person-enrichment-api
- **Rate Limits**: https://docs.peopledatalabs.com/docs/rate-limits

## 🎯 **Next Steps**

1. **Get API Key**: Sign up at PeopleDataLabs
2. **Update .env**: Add your API key
3. **Test Integration**: Run the test script
4. **Verify Results**: Check enrichment quality
5. **Deploy**: Use in your workflow

The integration is now ready for production use with comprehensive data enrichment capabilities!
