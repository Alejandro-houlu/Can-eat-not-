from typing import Literal
from datetime import datetime
from state import State, Message
from agents import trainer, nutritionist, food_specialist


def human_node(state: State) -> dict:
    """
    Human input node - gets user input and updates conversation state.
    """
    user_input = input("\nYou: ").strip()
    
    # Check for exit conditions
    if user_input.lower() in {"exit", "quit", ":q", "bye"}:
        return {
            "current_user_input": user_input,
            "session_complete": True,
            "awaiting_user_input": False
        }
    
    # Add user message to conversation
    messages = state.get("messages", []).copy()
    messages.append(Message(
        role="user",
        content=user_input,
        timestamp=datetime.now().isoformat()
    ))
    
    # Check if this looks like a specific food consumption request (not general meal planning)
    # Only trigger food specialist for specific food items the user wants to eat
    consumption_phrases = [
        "i want to eat", "can i eat", "i'm eating", "eating", "i'll eat", "let me eat",
        "should i eat", "is it ok to eat", "can eat", "want to eat"
    ]
    specific_foods = ["apple", "banana", "toast", "cappuccino", "cheese", "ham", "kfc", "pizza", "burger", "chicken"]
    
    user_lower = user_input.lower()
    
    # Check if user is asking about eating something specific
    has_consumption_intent = any(phrase in user_lower for phrase in consumption_phrases)
    has_specific_food = any(food in user_lower for food in specific_foods)
    
    # Only set as food request if both consumption intent AND specific food are present
    # OR if it's a clear food item with quantity (e.g., "2 apples", "kfc meal")
    is_food_request = (has_consumption_intent and has_specific_food) or \
                     any(f"{num} {food}" in user_lower for num in ["1", "2", "3", "4", "5", "one", "two", "three"] for food in specific_foods)
    
    return {
        "messages": messages,
        "current_user_input": user_input,
        "awaiting_user_input": False,
        "food_request": user_input if is_food_request and not state.get("food_request") else state.get("food_request"),
        "food_request_pending": is_food_request and state.get("profile_complete", False)
    }


def check_session_status(state: State) -> Literal["complete", "continue"]:
    """
    Check if session should end or continue.
    """
    if state.get("session_complete", False):
        return "complete"
    return "continue"


def determine_next_agent(state: State) -> Literal["trainer", "nutritionist", "food_specialist", "human"]:
    """
    Determine which agent should handle the next step based on current state.
    """
    current_phase = state.get("current_phase", "greeting")
    profile_complete = state.get("profile_complete", False)
    food_request = state.get("food_request")
    has_nutrition_profile = bool(state.get("nutrition_profile"))
    has_food_analysis = bool(state.get("food_analysis"))
    awaiting_food_request = state.get("awaiting_food_request", False)
    user_input = state.get("current_user_input", "").lower()
    
    print(f"🔄 Routing - Profile: {profile_complete}, Nutrition: {has_nutrition_profile}, Food Request: {bool(food_request)}, Food Analysis: {has_food_analysis}, Awaiting Food: {awaiting_food_request}")
    
    # Step 1: If profile not complete, collect it with trainer
    if not profile_complete:
        return "trainer"
    
    # Step 2: If profile complete but no nutrition analysis, do nutrition analysis
    if profile_complete and not has_nutrition_profile:
        return "nutritionist"
    
    # Step 3: Check if user is asking for meal planning/nutrition advice (not specific food)
    meal_planning_keywords = ["meal plan", "diet plan", "nutrition plan", "what should i eat", "meal ideas", "diet advice"]
    is_meal_planning_request = any(keyword in user_input for keyword in meal_planning_keywords)
    
    if profile_complete and has_nutrition_profile and is_meal_planning_request:
        return "nutritionist"  # Route to nutritionist for meal planning
    
    # Step 4: After nutrition analysis, trainer should ask for specific food to analyze
    if profile_complete and has_nutrition_profile and not food_request and not awaiting_food_request:
        return "trainer"  # Trainer asks for specific food
    
    # Step 5: If we have specific food request but no food analysis, analyze food
    if food_request and not has_food_analysis:
        return "food_specialist"
    
    # Step 6: If we have everything, make final recommendation
    if (profile_complete and has_nutrition_profile and has_food_analysis and 
        not state.get("final_recommendation")):
        return "trainer"  # Trainer gives final recommendation
    
    # Default back to human for more input
    return "human"


def trainer_node(state: State) -> dict:
    """
    Trainer node - handles profile collection and final recommendations.
    """
    print("\n🧑‍🏫 Trainer is thinking...")
    
    result = trainer(state)
    
    # Add trainer message to conversation
    messages = state.get("messages", []).copy()
    if result.get("message"):
        messages.append(Message(
            role="trainer",
            content=result["message"],
            timestamp=datetime.now().isoformat()
        ))
        print(f"\nTrainer 🧑‍🏫: {result['message']}")
    
    # Update state based on trainer's response
    updates = {
        "messages": messages,
        "awaiting_user_input": result.get("awaiting_user_input", False)
    }
    
    # Update profile if provided
    if result.get("user_profile"):
        updates["user_profile"] = result["user_profile"]
        updates["profile_complete"] = result.get("profile_complete", False)
    
    # Update phase if provided
    if result.get("current_phase"):
        updates["current_phase"] = result["current_phase"]
    
    # Update final recommendation if provided
    if result.get("final_recommendation"):
        updates["final_recommendation"] = result["final_recommendation"]
        updates["can_eat_verdict"] = result.get("can_eat_verdict", False)
        updates["session_complete"] = True
    
    return updates


def nutritionist_node(state: State) -> dict:
    """
    Nutritionist node - analyzes user profile and provides nutritional assessment.
    """
    print("\n🥼 Nutritionist is analyzing your profile...")
    
    result = nutritionist(state)
    
    # Add nutritionist message to conversation
    messages = state.get("messages", []).copy()
    if result.get("message"):
        messages.append(Message(
            role="nutritionist",
            content=result["message"],
            timestamp=datetime.now().isoformat()
        ))
        print(f"\nNutritionist 🥼: {result['message']}")
    
    return {
        "messages": messages,
        "nutrition_profile": result.get("nutrition_profile", state.get("nutrition_profile", {})),
        "current_phase": "nutrition_analysis",
        "awaiting_user_input": False
    }


def food_specialist_node(state: State) -> dict:
    """
    Food specialist node - analyzes requested food and provides nutritional information.
    """
    print("\n🍎 Food Specialist is analyzing your food...")
    
    result = food_specialist(state)
    
    # Add food specialist message to conversation
    messages = state.get("messages", []).copy()
    if result.get("message"):
        messages.append(Message(
            role="food_specialist",
            content=result["message"],
            timestamp=datetime.now().isoformat()
        ))
        print(f"\nFood Specialist 🍎: {result['message']}")
    
    return {
        "messages": messages,
        "food_analysis": result.get("food_analysis", state.get("food_analysis", {})),
        "current_phase": "food_analysis",
        "food_request_pending": False,
        "awaiting_user_input": False
    }


def completion_node(state: State) -> dict:
    """
    Completion node - handles session end.
    """
    print("\n=== SESSION COMPLETE ===")
    print("\nThank you for using Can-Eat-Not! Stay healthy! 🌟")
    
    return {
        "session_complete": True,
        "awaiting_user_input": False
    }
