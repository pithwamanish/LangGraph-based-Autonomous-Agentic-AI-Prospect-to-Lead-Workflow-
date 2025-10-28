# Demo Video Script: LangGraph Prospect-to-Lead Workflow System

**Duration:** 4-5 minutes  
**Format:** Screen recording with voiceover

---

## 🎬 **Video Structure**

### **Opening (30 seconds)**
- **Screen:** Show project folder structure
- **Voiceover:** "Hi! I'm going to demonstrate the LangGraph-based Prospect-to-Lead Workflow System I built. This is an autonomous AI agent system that discovers, enriches, scores, and contacts B2B prospects using a dynamic workflow configuration."

### **1. Project Overview (45 seconds)**
- **Screen:** Open README.md and show key features
- **Voiceover:** "The system consists of 7 specialized agents orchestrated by LangGraph. Each agent handles a specific part of the prospect-to-lead process. The entire workflow is defined in a single JSON configuration file, making it highly maintainable and flexible."

- **Screen:** Show workflow.json structure
- **Voiceover:** "Here's our workflow configuration. It defines 7 steps: prospect search, data enrichment, scoring, content generation, outreach execution, response tracking, and feedback training."

### **2. Agent Architecture Walkthrough (60 seconds)**
- **Screen:** Navigate to /agents/ directory
- **Voiceover:** "Let me show you the agent architecture. Each agent inherits from a BaseAgent class that provides common functionality like logging, error handling, and tool management."

- **Screen:** Open base_agent.py
- **Voiceover:** "The BaseAgent handles input validation, execution timing, and structured logging. Each agent implements its own _execute_agent method for specific business logic."

- **Screen:** Show prospect_search_agent.py
- **Voiceover:** "For example, the ProspectSearchAgent integrates with Clay and Apollo APIs to find B2B prospects matching our Ideal Customer Profile criteria."

- **Screen:** Show scoring_agent.py
- **Voiceover:** "The ScoringAgent uses configurable criteria to rank leads. It supports range-based scoring for company size and revenue, and boolean scoring for signals like recent funding."

### **3. LangGraph Builder Demonstration (90 seconds)**
- **Screen:** Open langgraph_builder.py
- **Voiceover:** "The LangGraphBuilder is the core orchestrator. It loads the JSON workflow, dynamically creates agents, and builds the execution graph."

- **Screen:** Run demo.py
- **Voiceover:** "Let me run our demonstration script to show the system in action."

- **Screen:** Show demo output
- **Voiceover:** "The system loads the workflow configuration, creates all 7 agents, builds the LangGraph, and executes a scoring workflow with sample data. Notice how Acme Corp scored 0.46 and Beta Inc scored 0.14 based on our criteria."

### **4. End-to-End Execution (60 seconds)**
- **Screen:** Run test_system.py
- **Voiceover:** "Let me run the complete test suite to show all components working together."

- **Screen:** Show test results
- **Voiceover:** "All 5 tests pass successfully. The system can load workflows, create agents, build graphs, handle missing environment variables gracefully, and execute workflows with real data."

- **Screen:** Show structured logging output
- **Voiceover:** "Notice the comprehensive structured logging. Each agent logs its reasoning steps, making the system transparent and debuggable."

### **5. Design Choices Explanation (45 seconds)**
- **Screen:** Show workflow.json again
- **Voiceover:** "Key design choices: First, JSON-driven configuration allows non-technical users to modify workflows without code changes."

- **Screen:** Show agent base class
- **Voiceover:** "Second, the modular agent architecture makes it easy to add new agents or modify existing ones. Each agent is self-contained with its own tools and logic."

- **Screen:** Show environment variable substitution
- **Voiceover:** "Third, environment variable substitution keeps sensitive API keys secure while allowing flexible configuration."

- **Screen:** Show error handling in base_agent.py
- **Voiceover:** "Fourth, comprehensive error handling ensures the system continues running even if individual agents fail."

### **6. Production Readiness (30 seconds)**
- **Screen:** Show README.md setup instructions
- **Voiceover:** "The system is production-ready with comprehensive documentation, testing, and monitoring. To use it, simply set up your API keys, customize the workflow JSON, and run the builder."

- **Screen:** Show requirements.txt
- **Voiceover:** "All dependencies are clearly defined, and the system includes both unit tests and integration tests."

### **Closing (15 seconds)**
- **Screen:** Show final project structure
- **Voiceover:** "This LangGraph-based system demonstrates how AI agents can work together autonomously to handle complex B2B lead generation workflows. The modular design and JSON configuration make it both powerful and maintainable."

---

## 🎥 **Recording Tips**

### **Technical Setup**
- Use a high-resolution screen recording (1920x1080 or higher)
- Record at 30fps for smooth playback
- Use a clear, professional voiceover
- Keep cursor movements smooth and deliberate

### **Screen Layout**
- Use a clean desktop background
- Close unnecessary applications
- Use a consistent terminal/editor theme
- Zoom in on code when showing specific sections

### **Content Flow**
- Pause briefly between sections for clarity
- Highlight important code sections with cursor
- Use consistent terminology throughout
- Keep explanations concise but comprehensive

### **Timing Breakdown**
- Opening: 30s
- Project Overview: 45s
- Agent Architecture: 60s
- LangGraph Builder: 90s
- End-to-End Execution: 60s
- Design Choices: 45s
- Production Readiness: 30s
- Closing: 15s
- **Total: ~5 minutes**

---

## 📝 **Key Points to Emphasize**

1. **Dynamic Configuration**: JSON-driven workflow definition
2. **Modular Architecture**: Each agent is independent and reusable
3. **AI Integration**: Uses OpenAI for content generation
4. **Multi-API Support**: Integrates with multiple external services
5. **Production Ready**: Comprehensive testing and documentation
6. **Observability**: Structured logging and performance monitoring
7. **Scalability**: Easy to add new agents or modify workflows

---

## 🚀 **Next Steps for Video**

1. **Record the demo** following this script
2. **Edit the video** to ensure smooth transitions
3. **Add captions** for key technical terms
4. **Upload to YouTube** or Google Drive
5. **Share the public link** as requested

The video should demonstrate both the technical implementation and the business value of the autonomous prospect-to-lead workflow system.
