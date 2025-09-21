from __future__ import annotations
import json
from typing import Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from state import State, UserProfile

def trainer(state: State) -> Dict[str, Any]:
    """
    Enhanced Trainer agent - handles profile collection, food requests, and final recommendations using LLM.
    """
    current_phase = state.get("current_phase", "greeting")
    profile_complete = state.get("profile_complete", False)
    user_input = state.get("current_user_input", "")
    user_profile = state.get("user_profile", {})
    has_nutrition_profile = bool(state.get("nutrition_profile"))
    has_food_analysis = bool(state.get("food_analysis"))
    food_request = state.get("food_request")
    
    print(f"🧑‍🏫 Trainer called - Profile: {profile_complete}, Nutrition: {has_nutrition_profile}, Food Request: {bool(food_request)}, Food Analysis: {has_food_analysis}")
    
    # If we have everything needed, provide final recommendation
    if (profile_complete and has_nutrition_profile and has_food_analysis and 
        not state.get("final_recommendation")):
        print("🧑‍🏫 Trainer: Generating final recommendation")
        return _generate_final_recommendation(state)
    
    # If we have a food request but no analysis, we should NOT be here - routing should go to food specialist
    if food_request and not has_food_analysis:
        print("🧑‍🏫 Trainer: Food request detected but no analysis - this should go to food specialist!")
        return {
            "message": "Let me get our food specialist to analyze that for you!",
            "awaiting_user_input": False
        }
    
    # If profile complete and nutrition done but no food request, ask for food
    if profile_complete and has_nutrition_profile and not food_request:
        print("🧑‍🏫 Trainer: Asking for food request")
        return _ask_for_food_request(state)
    
    # Otherwise, handle profile collection
    print("🧑‍🏫 Trainer: Handling profile collection")
    return _handle_profile_collection(state, user_input, user_profile)


def _handle_profile_collection(state: State, user_input: str, current_profile: Dict[str, Any]) -> Dict[str, Any]:
    """Handle profile collection with LLM assistance."""
    
    # Build conversation context
    messages = state.get("messages", [])
    conversation_context = ""
    for msg in messages[-5:]:  # Last 5 messages for context
        conversation_context += f"{msg['role']}: {msg['content']}\n"
    
    # Check what profile fields we still need
    required_fields = ["age", "sex", "height_cm", "weight_kg", "activity_level", "first_meal"]
    missing_fields = [field for field in required_fields if field not in current_profile]
    
    system_prompt = f"""You are a friendly Singaporean fitness trainer speaking in Singlish. Your job is to collect user profile information and provide guidance.

Required profile fields to collect:
- age (integer, 1-120)
- sex ("male" or "female") 
- height_cm (float, 80-250)
- weight_kg (float, 20-400)
- activity_level ("sedentary", "light", "moderate", "active", "very_active")
- first_meal (boolean - is this their first meal of the day?)

Current profile: {json.dumps(current_profile)}
Missing fields: {missing_fields}

Guidelines:
1. If this is the first interaction, give a warm greeting and explain what you do
2. Ask for ONE missing field at a time in a conversational Singlish way
3. Extract any profile information from the user's response
4. If user mentions food, note it but continue profile collection first
5. Be encouraging and friendly
6. Try talking like a Singaporean, with a little bit of 'lah' and 'leh'

Return JSON with:
- "message": Your response to the user
- "user_profile": Updated profile dict with any new info extracted
- "profile_complete": true if all required fields are collected
- "current_phase": "greeting" or "profile_collection"
- "awaiting_user_input": true if you need more info from user
- "food_request": copy any food mention from user input
"""

    user_prompt = f"""Conversation so far:
{conversation_context}

User just said: "{user_input}"

Respond appropriately based on the conversation flow and profile collection needs."""

    try:
        llm = ChatOpenAI(model="gpt-5-nano", temperature=1)
        
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ])
        
        result = json.loads(response.content)
        
        # Validate and clean the profile data
        if "user_profile" in result:
            cleaned_profile = _validate_profile_data(result["user_profile"])
            result["user_profile"] = {**current_profile, **cleaned_profile}
        
        return result
        
    except Exception as e:
        print(f"Error in trainer LLM call: {e}")
        # Fallback response
        if not current_profile:
            return {
                "message": "Hi there! I'm your fitness trainer lah! Let's see if you can eat that food. First, tell me your age?",
                "user_profile": current_profile,
                "profile_complete": False,
                "current_phase": "profile_collection",
                "awaiting_user_input": True
            }
        else:
            next_field = missing_fields[0] if missing_fields else None
            if next_field == "sex":
                question = "Are you male or female?"
            elif next_field == "height_cm":
                question = "What's your height in cm?"
            elif next_field == "weight_kg":
                question = "What's your current weight in kg?"
            elif next_field == "activity_level":
                question = "How active are you? (sedentary/light/moderate/active/very_active)"
            elif next_field == "first_meal":
                question = "Is this your first meal of the day?"
            else:
                question = "Can you tell me more about yourself?"
                
            return {
                "message": question,
                "user_profile": current_profile,
                "profile_complete": len(missing_fields) == 0,
                "current_phase": "profile_collection",
                "awaiting_user_input": True
            }


def _ask_for_food_request(state: State) -> Dict[str, Any]:
    """Ask user what food they want to analyze after nutrition profile is complete."""
    
    nutrition_profile = state.get("nutrition_profile", {})
    target_calories = nutrition_profile.get("target_calories", 2000)
    
    return {
        "message": f"Perfect! Now I know your nutritional needs - you should aim for about {target_calories} calories per day for weight loss. What food would you like me to analyze for you? For example, you can ask about apples, bananas, cappuccino, toast, ham, or cheese!",
        "awaiting_user_input": True,
        "awaiting_food_request": True,
        "current_phase": "food_request"
    }


def _generate_final_recommendation(state: State) -> Dict[str, Any]:
    """Generate final recommendation using all collected data."""
    
    nutrition_profile = state.get("nutrition_profile", {})
    food_analysis = state.get("food_analysis", {})
    user_profile = state.get("user_profile", {})
    
    system_prompt = """You are a friendly Singaporean fitness trainer giving final food recommendations.

Analyze the user's profile, nutritional needs, and food choice to give a comprehensive recommendation.

Consider:
- Their BMI, BMR, TDEE, and target calories
- The food's calories and nutritional content
- Whether this fits their weight loss goals
- Any health implications
- Suggestions for balance

Respond in Singlish style with:
- Clear verdict (can eat or should avoid)
- Reasoning based on the data
- Practical advice
- Encouragement

Return JSON with:
- "message": Your final recommendation
- "final_recommendation": Summary of your advice
- "can_eat_verdict": true/false based on analysis
"""

    user_prompt = f"""User Profile: {json.dumps(user_profile)}
Nutrition Analysis: {json.dumps(nutrition_profile)}
Food Analysis: {json.dumps(food_analysis)}

Provide your final recommendation."""

    try:
        llm = ChatOpenAI(model="gpt-5-nano", temperature=1)
        
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ])
        
        result = json.loads(response.content)
        return result
        
    except Exception as e:
        print(f"Error in final recommendation: {e}")
        # Fallback recommendation
        target_cals = nutrition_profile.get("target_calories", 2000)
        food_cals = food_analysis.get("total_calories", 0)
        can_eat = food_cals <= target_cals * 0.3  # Max 30% of daily calories in one meal
        
        return {
            "message": f"Based on your target of {target_cals} calories per day, this food has {food_cals} calories. {'Can eat lah!' if can_eat else 'Better reduce a bit lor.'}",
            "final_recommendation": f"Food analysis complete. {'Approved' if can_eat else 'Not recommended'} based on calorie targets.",
            "can_eat_verdict": can_eat
        }


def _validate_profile_data(profile_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and clean profile data."""
    cleaned = {}
    
    if "age" in profile_data:
        try:
            age = int(profile_data["age"])
            if 1 <= age <= 120:
                cleaned["age"] = age
        except (ValueError, TypeError):
            pass
    
    if "sex" in profile_data:
        sex = str(profile_data["sex"]).lower()
        if sex in ["male", "female"]:
            cleaned["sex"] = sex
    
    if "height_cm" in profile_data:
        try:
            height = float(profile_data["height_cm"])
            if 80 <= height <= 250:
                cleaned["height_cm"] = height
        except (ValueError, TypeError):
            pass
    
    if "weight_kg" in profile_data:
        try:
            weight = float(profile_data["weight_kg"])
            if 20 <= weight <= 400:
                cleaned["weight_kg"] = weight
        except (ValueError, TypeError):
            pass
    
    if "activity_level" in profile_data:
        activity = str(profile_data["activity_level"]).lower()
        valid_levels = ["sedentary", "light", "moderate", "active", "very_active"]
        if activity in valid_levels:
            cleaned["activity_level"] = activity
    
    if "first_meal" in profile_data:
        if isinstance(profile_data["first_meal"], bool):
            cleaned["first_meal"] = profile_data["first_meal"]
        else:
            # Try to parse from string
            first_meal_str = str(profile_data["first_meal"]).lower()
            if first_meal_str in ["true", "yes", "y", "first"]:
                cleaned["first_meal"] = True
            elif first_meal_str in ["false", "no", "n", "not first"]:
                cleaned["first_meal"] = False
    
    return cleaned
