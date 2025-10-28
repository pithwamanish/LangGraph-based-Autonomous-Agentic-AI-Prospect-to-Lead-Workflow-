# Prospect-to-Lead Workflow System

A comprehensive LangGraph-based autonomous prospect-to-lead workflow system that dynamically discovers, enriches, scores, and contacts B2B prospects using AI agents.

## 🎯 Overview

This system implements an end-to-end B2B lead generation workflow using LangGraph and LangChain. It dynamically constructs agent workflows from JSON configuration files, enabling flexible and maintainable prospect-to-lead automation.

### Key Features

- **Dynamic Workflow Construction**: Build workflows from JSON configuration files
- **Modular Agent Architecture**: Each step is handled by a specialized agent
- **AI-Powered Content Generation**: Personalized outreach using OpenAI GPT models
- **Multi-API Integration**: Clay, Apollo, Clearbit, SendGrid, and Google Sheets
- **Performance Tracking**: Comprehensive response tracking and analytics
- **Feedback Loop**: Automated performance analysis and recommendations
- **Structured Logging**: Full observability with structured logging

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Workflow      │    │   LangGraph      │    │   Agents        │
│   JSON Config   │───▶│   Builder        │───▶│   Execution     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │   State          │
                       │   Management     │
                       └──────────────────┘
```

### Workflow Steps

1. **Prospect Search** - Find B2B prospects using Clay and Apollo APIs
2. **Data Enrichment** - Enrich lead data with company and contact information
3. **Scoring** - Score and rank leads based on ICP criteria
4. **Content Generation** - Create personalized outreach messages
5. **Outreach Execution** - Send emails via SendGrid or Apollo
6. **Response Tracking** - Monitor engagement and responses
7. **Feedback Training** - Analyze performance and generate recommendations

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- API keys for external services (see Configuration section)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd prospect-to-lead
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your API keys
   ```

5. **Run the workflow**
   ```bash
   python langgraph_builder.py
   ```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Clay API Configuration
CLAY_API_KEY=your_clay_api_key_here

# Apollo API Configuration
APOLLO_API_KEY=your_apollo_api_key_here

# Clearbit API Configuration
CLEARBIT_API_KEY=your_clearbit_api_key_here

# SendGrid Configuration
SENDGRID_API_KEY=your_sendgrid_api_key_here

# Google Sheets Configuration
GOOGLE_CREDENTIALS_FILE=path/to/credentials.json
SHEET_ID=your_google_sheet_id_here

# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### Workflow Configuration

The system uses `workflow.json` to define the workflow structure. Here's the schema:

```json
{
  "workflow_name": "OutboundLeadGeneration",
  "description": "End-to-end AI agent workflow",
  "version": "1.0.0",
  "config": {
    "scoring": {
      "criteria": [
        {"field": "company_size", "weight": 0.3, "min": 100, "max": 1000},
        {"field": "revenue", "weight": 0.25, "min": 20000000, "max": 200000000}
      ]
    },
    "outreach": {
      "persona": "SDR",
      "tone": "friendly"
    }
  },
  "steps": [
    {
      "id": "prospect_search",
      "agent": "ProspectSearchAgent",
      "inputs": {
        "icp": {
          "industry": "SaaS",
          "location": "USA",
          "employee_count": {"min": 100, "max": 1000}
        }
      },
      "tools": [
        {
          "name": "ClayAPI",
          "config": {"api_key": "{{CLAY_API_KEY}}"}
        }
      ],
      "next_steps": ["enrichment"]
    }
  ]
}
```

## 🤖 Agent Reference

### ProspectSearchAgent
- **Purpose**: Find B2B prospects using external APIs
- **APIs**: Clay API, Apollo API
- **Input**: ICP criteria, search signals
- **Output**: List of prospect leads

### DataEnrichmentAgent
- **Purpose**: Enrich lead data with additional information
- **APIs**: Clearbit API
- **Input**: Raw prospect data
- **Output**: Enriched lead data

### ScoringAgent
- **Purpose**: Score and rank leads based on ICP criteria
- **APIs**: None (internal logic)
- **Input**: Enriched leads, scoring criteria
- **Output**: Ranked leads with scores

### OutreachContentAgent
- **Purpose**: Generate personalized outreach messages
- **APIs**: OpenAI API
- **Input**: Ranked leads, persona configuration
- **Output**: Personalized email content

### OutreachExecutorAgent
- **Purpose**: Send outreach messages via email
- **APIs**: SendGrid API, Apollo API
- **Input**: Generated messages
- **Output**: Sending status and campaign ID

### ResponseTrackerAgent
- **Purpose**: Track email responses and engagement
- **APIs**: Apollo API
- **Input**: Campaign ID
- **Output**: Response data and metrics

### FeedbackTrainerAgent
- **Purpose**: Analyze performance and generate recommendations
- **APIs**: Google Sheets API
- **Input**: Response data
- **Output**: Performance recommendations

## 📊 Usage Examples

### Basic Workflow Execution

```python
from langgraph_builder import LangGraphBuilder

# Initialize builder
builder = LangGraphBuilder()

# Get workflow summary
summary = builder.get_workflow_summary()
print(summary)

# Execute workflow
final_state = builder.execute_workflow()
print(f"Workflow completed in {final_state['duration']:.2f} seconds")
```

### Custom Workflow Configuration

```python
# Load custom workflow
builder = LangGraphBuilder("custom_workflow.json")

# Execute with custom inputs
initial_inputs = {
    "custom_icp": {
        "industry": "Healthcare",
        "location": "Canada"
    }
}
final_state = builder.execute_workflow(initial_inputs)
```

### Agent-Specific Execution

```python
from agents import ProspectSearchAgent

# Create agent directly
agent = ProspectSearchAgent(
    agent_id="custom_search",
    instructions="Find healthcare prospects in Canada",
    tools=[{"name": "ApolloAPI", "config": {"api_key": "your_key"}}]
)

# Execute agent
result = agent.execute({
    "icp": {"industry": "Healthcare", "location": "Canada"},
    "signals": ["recent_funding"]
})
```

## 🔧 Development

### Project Structure

```
prospect-to-lead/
├── agents/                     # Agent implementations
│   ├── __init__.py
│   ├── base_agent.py          # Base agent class
│   ├── prospect_search_agent.py
│   ├── data_enrichment_agent.py
│   ├── scoring_agent.py
│   ├── outreach_content_agent.py
│   ├── outreach_executor_agent.py
│   ├── response_tracker_agent.py
│   └── feedback_trainer_agent.py
├── langgraph_builder.py       # Main LangGraph builder
├── workflow.json              # Workflow configuration
├── requirements.txt           # Python dependencies
├── env.example               # Environment variables template
└── README.md                 # This file
```

### Adding New Agents

1. **Create agent class** in `agents/` directory
2. **Inherit from BaseAgent**
3. **Implement `_execute_agent` method**
4. **Add to agent registry** in `langgraph_builder.py`
5. **Update workflow JSON** to use new agent

Example:

```python
# agents/custom_agent.py
from .base_agent import BaseAgent, AgentInput

class CustomAgent(BaseAgent):
    def _execute_agent(self, input_data: AgentInput) -> Dict[str, Any]:
        # Implement agent logic
        return {"result": "success"}
```

### Modifying Workflow

Edit `workflow.json` to:
- Add/remove steps
- Modify agent configurations
- Change input/output mappings
- Update tool configurations

## 📈 Monitoring and Logging

The system provides comprehensive logging and monitoring:

### Structured Logging
- All operations are logged with structured data
- Easy integration with log aggregation systems
- Performance metrics and error tracking

### Execution Tracking
- Step-by-step execution logs
- Performance timing for each agent
- Error tracking and recovery

### Metrics Collection
- Response rates and engagement metrics
- Agent performance statistics
- Workflow execution analytics

## 🚨 Error Handling

The system includes robust error handling:

- **Agent-level errors**: Individual agent failures don't stop the workflow
- **API failures**: Graceful degradation when external APIs are unavailable
- **Validation errors**: Input/output validation with clear error messages
- **Retry logic**: Configurable retry mechanisms for transient failures

## 🔒 Security Considerations

- **API Key Management**: Store sensitive keys in environment variables
- **Data Privacy**: No sensitive data is logged or stored permanently
- **Rate Limiting**: Built-in rate limiting for API calls
- **Input Validation**: All inputs are validated before processing

## 🧪 Testing

Run tests to verify the system:

```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-mock

# Run tests
pytest tests/
```

## 📝 API Reference

### LangGraphBuilder

#### `__init__(workflow_file: str, env_file: str)`
Initialize the builder with workflow and environment files.

#### `build_graph() -> StateGraph`
Build the LangGraph from workflow configuration.

#### `execute_workflow(initial_inputs: Dict) -> Dict`
Execute the complete workflow with optional initial inputs.

#### `get_workflow_summary() -> Dict`
Get a summary of the workflow configuration.

### BaseAgent

#### `execute(input_data: AgentInput) -> AgentOutput`
Execute the agent with input data and return results.

#### `log_reasoning(step: str, reasoning: str, data: Any)`
Log reasoning steps for transparency and debugging.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For questions and support:

1. Check the documentation
2. Review the example configurations
3. Open an issue on GitHub
4. Contact the development team

## 🔄 Changelog

### Version 1.0.0
- Initial release
- Core LangGraph builder functionality
- All 7 agent types implemented
- JSON-based workflow configuration
- Comprehensive logging and monitoring

---

**Built with ❤️ using LangGraph, LangChain, and modern Python practices.**
