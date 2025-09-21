# Can-Eat-Not — Multi-Agent Nutrition Assistant

A sophisticated multi-agent CLI application that helps you make informed food choices by analyzing whether you can eat specific foods while staying within your daily calorie targets for weight loss.

## 🤖 Multi-Agent Architecture

This application uses **3 intelligent LLM-powered agents** working together in a coordinated workflow:

### **🧑‍🏫 Trainer Agent**
- **Role**: Profile collection, conversation coordination, and final recommendations
- **Technology**: LLM-powered (gpt-5-nano) with Singlish persona
- **Responsibilities**: 
  - Collects user profile (age, sex, height, weight, activity level)
  - Asks for specific food items to analyze
  - Provides final "can eat or not" recommendations
  - Coordinates the overall conversation flow

### **🥼 Nutritionist Agent** 
- **Role**: Health analysis and meal planning
- **Technology**: LLM-enhanced calculations with professional expertise
- **Responsibilities**:
  - Calculates BMI, BMR, TDEE using Mifflin-St Jeor equation
  - Determines target calories for weight loss
  - Provides personalized health assessments and meal plans
  - Handles nutrition advice and dietary guidance

### **🍎 Food Specialist Agent**
- **Role**: Specific food analysis for consumption decisions
- **Technology**: **Fully LLM-powered** - analyzes ANY food using AI knowledge
- **Responsibilities**:
  - Analyzes specific food items when user wants to eat something
  - Provides detailed nutritional breakdowns (calories, macros)
  - Offers portion recommendations and health impact assessment
  - **Only triggered for specific consumption requests**

## 🔄 Intelligent Workflow

The agents work together with smart routing logic:

### **Profile & Nutrition Setup:**
1. **Profile Collection** → 🧑‍🏫 Trainer collects user's health profile
2. **Nutrition Analysis** → 🥼 Nutritionist calculates BMI, target calories, etc.

### **User Request Routing:**
3. **Meal Planning Request** → 🥼 Nutritionist provides diet plans and nutrition advice
4. **Specific Food Request** → 🍎 Food Specialist analyzes the food item
5. **Final Recommendation** → 🧑‍🏫 Trainer provides verdict based on analysis

### **Smart Detection:**
- **Meal Planning**: "meal plan", "diet advice", "what should I eat" → Routes to Nutritionist
- **Food Consumption**: "I want to eat pizza", "can I eat KFC" → Routes to Food Specialist

## 🛠️ Technology Stack

- **Framework**: [LangGraph](https://langchain-ai.github.io/langgraph/) for multi-agent orchestration
- **LLM**: OpenAI gpt-5-nano via [LangChain](https://python.langchain.com/)
- **Language**: Python 3.10+ with comprehensive type hints
- **Package Manager**: [uv](https://docs.astral.sh/uv/) for fast dependency management
- **Architecture**: Clean separation with `state.py`, `nodes.py`, `agents/`
- **Food Analysis**: **100% LLM-powered** - no external databases required!

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- OpenAI API key
- uv package manager

### Installation & Setup

```bash
# Install dependencies
uv sync

# Set your OpenAI API key
export OPENAI_API_KEY="sk-..."   # Linux/Mac
# OR
$env:OPENAI_API_KEY="sk-..."     # PowerShell

# Run the application
uv run python main.py
```

### Example Usage

```
=== CAN-EAT-NOT: Multi-Agent Nutrition Assistant ===
🧑‍🏫 Trainer | 🥼 Nutritionist | 🍎 Food Specialist

# Profile Collection Phase
Trainer 🧑‍🏫: Hi there! I'm your fitness trainer lah! What's your age?
You: 25
Trainer 🧑‍🏫: Great! Are you male or female?
You: male
[... profile collection continues ...]

# Nutrition Analysis Phase  
Nutritionist 🥼: Based on your profile: BMI 22.5 (normal), target 1800 cal/day for weight loss.

# Meal Planning Request
You: Can you give me a meal plan?
Nutritionist 🥼: Here's a personalized meal plan for your 1800 calorie target...

# Specific Food Analysis Request
You: I want to eat 2 slices of pizza
Food Specialist 🍎: 2 slices of pizza contain approximately 560 calories...

# Final Recommendation
Trainer 🧑‍🏫: Based on the analysis, that's 31% of your daily calories. Can eat lah, but maybe balance with lighter meals today! ✅
```

## 📁 Project Structure

```
can-eat-not/
├── .gitignore              # Comprehensive git ignore rules
├── README.md               # Complete documentation  
├── main.py                 # Application entry point & graph building
├── state.py                # State management with TypedDict definitions
├── nodes.py                # Node functions & intelligent routing logic
├── pyproject.toml          # Dependencies & project config
└── agents/                 # Multi-agent system
    ├── __init__.py
    ├── trainer.py          # LLM-powered trainer agent
    ├── nutritionist.py     # LLM-enhanced nutrition analysis
    └── food_specialist.py  # Fully LLM-powered food analysis
```

## 🎯 Key Features

- **🧠 Fully AI-Powered**: All agents use LLM intelligence - no hardcoded databases!
- **🌍 Universal Food Analysis**: Can analyze ANY food using AI nutritional knowledge
- **🎯 Smart Request Routing**: Distinguishes between meal planning and food consumption requests
- **💬 Natural Conversations**: Singlish-style interactions feel authentic
- **📊 Comprehensive Health Analysis**: BMI, BMR, TDEE with personalized insights
- **🤝 Intelligent Agent Coordination**: Seamless handoffs between specialized agents
- **🛡️ Graceful Fallbacks**: Robust error handling when LLM calls fail
- **🔍 Debug Transparency**: Clear routing decisions visible during execution

## 🌟 Why This Architecture?

### **Smart Agent Routing**
- **Context-Aware**: Routes requests to the most appropriate agent
- **Meal Planning**: Nutritionist handles diet advice and meal plans
- **Food Analysis**: Food specialist only analyzes specific consumption requests
- **Coordination**: Trainer manages the overall conversation flow

### **No Database Dependencies**
- **Flexibility**: Can analyze any food, not limited to predefined databases
- **Scalability**: No need to maintain or update food databases
- **Intelligence**: LLM provides contextual, nuanced nutritional analysis
- **Simplicity**: Fewer moving parts, easier to deploy and maintain

### **True Multi-Agent Intelligence**
- Each agent has distinct expertise and responsibilities
- Proper coordination ensures each agent contributes meaningfully
- Clean separation of concerns following software engineering best practices

### **LangGraph Architecture**
- Sophisticated routing logic ensures proper agent flow
- State management tracks conversation and analysis progress
- Conditional edges enable intelligent decision-making

## 🤝 Contributing

This project demonstrates advanced multi-agent architecture patterns using LangGraph with fully LLM-powered agents. Perfect for learning:
- Multi-agent coordination and routing
- LangGraph workflows and conditional edges
- Clean architecture patterns
- LLM-powered applications
- Intelligent conversation management

## 📄 License

Educational project for learning multi-agent AI systems.
