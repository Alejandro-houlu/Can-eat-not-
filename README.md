# Can-Eat-Not — Multi-Agent Nutrition Assistant

A sophisticated multi-agent CLI application that helps you make informed food choices by analyzing whether you can eat specific foods while staying within your daily calorie targets for weight loss.

## 🤖 Multi-Agent Architecture

This application uses **3 intelligent LLM-powered agents** working together in a coordinated workflow:

### **🧑‍🏫 Trainer Agent**
- **Role**: Profile collection, conversation coordination, and final recommendations
- **Technology**: LLM-powered (gpt-5-nano) with Singlish persona
- **Responsibilities**: 
  - Collects user profile (age, sex, height, weight, activity level)
  - Asks for food requests after nutrition analysis
  - Provides final "can eat or not" recommendations

### **🥼 Nutritionist Agent** 
- **Role**: Health and nutrition analysis
- **Technology**: LLM-enhanced calculations with professional expertise
- **Responsibilities**:
  - Calculates BMI, BMR, TDEE using Mifflin-St Jeor equation
  - Determines target calories for weight loss
  - Provides personalized health assessments and recommendations

### **🍎 Food Specialist Agent**
- **Role**: Food analysis and nutritional insights
- **Technology**: **Fully LLM-powered** - no database dependencies!
- **Responsibilities**:
  - Analyzes ANY food using comprehensive AI nutritional knowledge
  - Provides detailed nutritional breakdowns (calories, macros)
  - Offers portion recommendations and health tips

## 🔄 Intelligent Workflow

The agents work together in a carefully orchestrated sequence:

1. **Profile Collection** → 🧑‍🏫 Trainer collects user's health profile
2. **Nutrition Analysis** → 🥼 Nutritionist calculates BMI, target calories, etc.
3. **Food Request** → 🧑‍🏫 Trainer asks what food user wants to analyze
4. **Food Analysis** → 🍎 Food Specialist analyzes ANY food using AI knowledge
5. **Final Recommendation** → 🧑‍🏫 Trainer provides verdict based on all data

## 🛠️ Technology Stack

- **Framework**: [LangGraph](https://langchain-ai.github.io/langgraph/) for multi-agent orchestration
- **LLM**: OpenAI gpt-5-nano via [LangChain](https://python.langchain.com/)
- **Language**: Python 3.10+ with type hints
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

Trainer 🧑‍🏫: Hi there! I'm your fitness trainer lah! What's your age?
You: 25

Trainer 🧑‍🏫: Great! Are you male or female?
You: male

[... profile collection continues ...]

Nutritionist 🥼: Based on your profile: BMI 22.5 (normal), target 1800 cal/day for weight loss.

Trainer 🧑‍🏫: Perfect! What food would you like me to analyze?
You: 2 slices of pizza

Food Specialist 🍎: 2 slices of pizza contain approximately 560 calories with 24g protein, 58g carbs, 26g fat. That's about 31% of your daily target!

Trainer 🧑‍🏫: Hmm, quite high in calories leh! Maybe can eat 1 slice instead? ⚠️
```

## 📁 Project Structure

```
can-eat-not/
├── main.py                 # Application entry point & graph building
├── state.py                # State management with TypedDict definitions
├── nodes.py                # Node functions & intelligent routing logic
├── agents/                 # Multi-agent system
│   ├── trainer.py          # LLM-powered trainer agent
│   ├── nutritionist.py     # LLM-enhanced nutrition analysis
│   └── food_specialist.py  # Fully LLM-powered food analysis
└── pyproject.toml          # Dependencies & project config
```

## 🎯 Key Features

- **🧠 Fully AI-Powered**: All agents use LLM intelligence - no hardcoded databases!
- **🌍 Universal Food Analysis**: Can analyze ANY food using AI nutritional knowledge
- **💬 Natural Conversations**: Singlish-style interactions feel authentic
- **📊 Comprehensive Health Analysis**: BMI, BMR, TDEE with personalized insights
- **🤝 Smart Agent Coordination**: Seamless handoffs between specialized agents
- **🛡️ Graceful Fallbacks**: Robust error handling when LLM calls fail
- **🔍 Debug Transparency**: Clear routing decisions visible during execution

## 🌟 Why This Architecture?

### **No Database Dependencies**
- **Flexibility**: Can analyze any food, not limited to a predefined database
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
- Multi-agent coordination
- LangGraph workflows
- Clean architecture patterns
- LLM-powered applications

## 📄 License

Educational project for learning multi-agent AI systems.
