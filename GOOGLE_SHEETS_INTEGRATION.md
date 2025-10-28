# Google Sheets Integration in FeedbackTrainerAgent

## 🔧 **How Google Sheets Integration Works**

The `FeedbackTrainerAgent` utilizes Google Sheets to store and track performance recommendations and metrics. Here's how it works:

### **1. Environment Variables**

The system uses two key environment variables:

```bash
# In your .env file
GOOGLE_CREDENTIALS_FILE=path/to/your/credentials.json
SHEET_ID=your_google_sheet_id_here
```

### **2. Configuration in workflow.json**

```json
{
  "id": "feedback_trainer",
  "agent": "FeedbackTrainerAgent",
  "tools": [
    {
      "name": "GoogleSheets", 
      "config": {
        "sheet_id": "{{SHEET_ID}}", 
        "credentials": "{{GOOGLE_CREDENTIALS_FILE}}"
      }
    }
  ]
}
```

### **3. Authentication Methods**

The system supports two authentication methods:

#### **A. Service Account Authentication (Recommended)**
- Download service account JSON key from Google Cloud Console
- Set `GOOGLE_CREDENTIALS_FILE` to the path of the JSON file
- No user interaction required

#### **B. OAuth2 Authentication**
- Download OAuth2 client credentials from Google Cloud Console
- Set `GOOGLE_CREDENTIALS_FILE` to the path of the JSON file
- First run will open browser for authentication
- Subsequent runs use stored tokens

### **4. Data Written to Sheets**

The agent creates and writes to three sheets:

#### **A. Recommendations Sheet**
| Column | Description |
|--------|-------------|
| Timestamp | When the recommendation was generated |
| Type | Type of recommendation (icp_adjustment, subject_line_optimization, etc.) |
| Priority | Priority level (high, medium, low) |
| Title | Recommendation title |
| Description | Detailed description |
| Suggestions | Specific action items |
| Expected Impact | Expected improvement |
| Status | Current status (pending, approved, implemented) |

#### **B. Performance Sheet**
| Column | Description |
|--------|-------------|
| Timestamp | When the metric was recorded |
| Metric | Metric name |
| Value | Metric value |
| Category | Category (engagement_insights, response_patterns, etc.) |

#### **C. Campaign_Data Sheet**
- Stores detailed campaign performance data
- Used for historical analysis and trend tracking

## 🚀 **Setup Instructions**

### **Step 1: Create Google Cloud Project**

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google Sheets API
4. Create credentials (Service Account or OAuth2)

### **Step 2: Create Google Sheet**

1. Go to [Google Sheets](https://sheets.google.com/)
2. Create a new spreadsheet
3. Copy the Sheet ID from the URL:
   ```
   https://docs.google.com/spreadsheets/d/SHEET_ID_HERE/edit
   ```
4. Set `SHEET_ID` environment variable

### **Step 3: Configure Credentials**

#### **For Service Account:**
1. Go to Google Cloud Console → IAM & Admin → Service Accounts
2. Create new service account
3. Download JSON key file
4. Set `GOOGLE_CREDENTIALS_FILE` to the JSON file path
5. Share the Google Sheet with the service account email

#### **For OAuth2:**
1. Go to Google Cloud Console → APIs & Services → Credentials
2. Create OAuth2 client ID
3. Download JSON file
4. Set `GOOGLE_CREDENTIALS_FILE` to the JSON file path

### **Step 4: Install Dependencies**

```bash
pip install google-auth google-auth-oauthlib google-api-python-client
```

### **Step 5: Test Integration**

```python
from agents.google_sheets_client import GoogleSheetsClient

# Test the client
client = GoogleSheetsClient(
    sheet_id="your_sheet_id",
    credentials_file="path/to/credentials.json"
)

# Test writing data
test_recommendations = [
    {
        "type": "test",
        "priority": "high",
        "title": "Test Recommendation",
        "description": "This is a test",
        "suggestions": ["Test suggestion"],
        "expected_impact": "Test impact"
    }
]

success = client.write_recommendations(test_recommendations)
print(f"Success: {success}")
```

## 🔄 **How It Works in the Workflow**

### **1. Agent Initialization**
```python
# When FeedbackTrainerAgent is created
agent = FeedbackTrainerAgent(
    agent_id="feedback_trainer",
    instructions="Analyze performance and generate recommendations",
    tools=[{
        "name": "GoogleSheets",
        "config": {
            "sheet_id": "{{SHEET_ID}}",
            "credentials": "{{GOOGLE_CREDENTIALS_FILE}}"
        }
    }]
)
```

### **2. Tool Creation**
```python
# The _create_tool method creates a GoogleSheetsClient
sheets_client = GoogleSheetsClient(
    sheet_id=config.get("sheet_id"),
    credentials_file=config.get("credentials")
)
```

### **3. Data Writing**
```python
# When recommendations are generated
def _write_recommendations_to_sheets(self, recommendations):
    sheets_client = self.google_sheets_client["client"]
    
    # Create sheets if they don't exist
    sheets_client.create_sheets_if_not_exist()
    
    # Write recommendations
    success = sheets_client.write_recommendations(recommendations)
```

## 📊 **Example Data Written**

### **Recommendations Example:**
```
Timestamp: 2025-10-18T18:30:00
Type: subject_line_optimization
Priority: high
Title: Improve Subject Lines
Description: Low open rate (15%) indicates subject lines need improvement
Suggestions: Use more personalized subject lines; Add urgency elements; Test different formats
Expected Impact: Increase open rates by 20-30%
Status: pending
```

### **Performance Metrics Example:**
```
Timestamp: 2025-10-18T18:30:00
Metric: open_rate
Value: 15.5
Category: engagement_insights
```

## 🛠️ **Error Handling**

The system includes comprehensive error handling:

- **Authentication Errors**: Graceful fallback if credentials are invalid
- **API Errors**: Retry logic and detailed error logging
- **Sheet Creation**: Automatic sheet creation if they don't exist
- **Data Validation**: Input validation before writing to sheets

## 🔍 **Monitoring and Logging**

All Google Sheets operations are logged:

```python
self.log_reasoning(
    "sheets_write_success",
    f"Successfully wrote {len(recommendations)} recommendations to Google Sheets"
)
```

## 🚨 **Security Considerations**

- **Credentials**: Store credentials file securely, never commit to version control
- **Permissions**: Use least-privilege access for service accounts
- **Data**: Sensitive data is not logged, only operation status
- **Environment**: Use environment variables for all sensitive configuration

## 📈 **Benefits of Google Sheets Integration**

1. **Human Review**: Recommendations can be reviewed and approved by humans
2. **Historical Tracking**: Performance metrics are stored for trend analysis
3. **Collaboration**: Multiple team members can access and update recommendations
4. **Reporting**: Easy to create reports and dashboards from the data
5. **Integration**: Works with other Google Workspace tools

This integration makes the feedback loop truly autonomous while maintaining human oversight and control over critical decisions.
