from __future__ import annotations
import json
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from state import State, FoodAnalysis

def food_specialist(state: State) -> Dict[str, Any]:
    """
    Enhanced Food Specialist agent - analyzes food requests with full LLM-powered insights.
    """
    food_request = state.get("food_request", "")
    user_profile = state.get("user_profile", {})
    nutrition_profile = state.get("nutrition_profile", {})
    
    if not food_request:
        return {
            "message": "I need to know what food you want to analyze! Please tell me what you'd like to eat.",
            "food_analysis": {}
        }
    
    # Generate complete LLM-powered food analysis
    return _generate_complete_food_analysis(food_request, user_profile, nutrition_profile)


def _generate_complete_food_analysis(
    food_request: str, 
    user_profile: Dict[str, Any], 
    nutrition_profile: Dict[str, Any]
) -> Dict[str, Any]:
    """Generate complete food analysis using LLM without any database dependency."""
    
    system_prompt = """You are a professional food specialist and nutritionist with comprehensive knowledge of food nutrition.

    Analyze the requested food item and provide:
    1. Accurate caloric and nutritional content based on your knowledge
    2. Detailed macronutrient breakdown (protein, carbs, fat, fiber, sugar)
    3. How it fits into the user's dietary goals and weight loss plan
    4. Health benefits and potential concerns
    5. Portion size recommendations specific to this user
    6. Practical tips for preparation or pairing
    
    Use your extensive nutritional knowledge to provide accurate estimates. Be specific about quantities and measurements.
    
    Respond in a friendly, professional tone with some natural Singlish expressions.
    
    Return JSON with:
    - "message": Your detailed food analysis and recommendations
    - "food_analysis": Complete food analysis object with all nutritional data
    - "health_tips": List of 2-3 practical tips related to this food
    - "portion_recommendation": Specific portion advice for this user's goals
    """
    
    user_prompt = f"""Food Request: "{food_request}"

User Profile:
- Age: {user_profile.get('age', 'Unknown')}
- Sex: {user_profile.get('sex', 'Unknown')}
- Weight: {user_profile.get('weight_kg', 'Unknown')} kg
- Activity Level: {user_profile.get('activity_level', 'Unknown')}
- First Meal: {user_profile.get('first_meal', 'Unknown')}

Nutrition Goals:
- Target Calories: {nutrition_profile.get('target_calories', 'Unknown')} per day
- BMI: {nutrition_profile.get('bmi', 'Unknown')} ({nutrition_profile.get('bmi_class', 'Unknown')})
- Recommended Daily Protein: {nutrition_profile.get('recommended_macros', {}).get('protein_g', 'Unknown')}g
- Recommended Daily Carbs: {nutrition_profile.get('recommended_macros', {}).get('carbs_g', 'Unknown')}g
- Recommended Daily Fat: {nutrition_profile.get('recommended_macros', {}).get('fat_g', 'Unknown')}g

Please analyze this food request and provide comprehensive nutritional information and recommendations tailored to this user's weight loss goals."""

    try:
        llm = ChatOpenAI(model="gpt-5-nano", temperature=1)
        
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ])
        
        result = json.loads(response.content)
        
        # Extract food analysis data from LLM response
        food_analysis_data = result.get("food_analysis", {})
        
        # Create comprehensive food analysis
        food_analysis = FoodAnalysis(
            food_item=food_analysis_data.get("food_item", food_request),
            quantity=food_analysis_data.get("quantity", food_request),
            calories_per_unit=food_analysis_data.get("calories_per_unit", 0),
            total_calories=food_analysis_data.get("total_calories", 0),
            macros=food_analysis_data.get("macros", {
                "protein_g": 0,
                "carbs_g": 0,
                "fat_g": 0,
                "fiber_g": 0,
                "sugar_g": 0
            }),
            nutritional_notes=food_analysis_data.get("nutritional_notes", "LLM-powered nutritional analysis"),
            health_impact=food_analysis_data.get("health_impact", "Analyzed using AI nutritional knowledge")
        )
        
        return {
            "message": result.get("message", f"Complete nutritional analysis for {food_request}."),
            "food_analysis": food_analysis,
            "health_tips": result.get("health_tips", []),
            "portion_recommendation": result.get("portion_recommendation", "")
        }
        
    except Exception as e:
        print(f"Error in food specialist LLM call: {e}")
        
        # Fallback analysis with reasonable estimates
        target_cals = nutrition_profile.get("target_calories", 2000)
        estimated_calories = 100  # Conservative estimate
        
        food_analysis = FoodAnalysis(
            food_item=food_request,
            quantity=food_request,
            calories_per_unit=estimated_calories,
            total_calories=estimated_calories,
            macros={
                "protein_g": 5.0,
                "carbs_g": 15.0,
                "fat_g": 3.0,
                "fiber_g": 2.0,
                "sugar_g": 8.0
            },
            nutritional_notes=f"Estimated nutritional content for {food_request}. Approximately {estimated_calories} calories.",
            health_impact="Moderate caloric impact. Consider portion size and daily intake balance."
        )
        
        percentage_of_daily = round((estimated_calories / target_cals) * 100, 1) if target_cals > 0 else 0
        
        return {
            "message": f"Food analysis for {food_request}: Estimated {estimated_calories} calories ({percentage_of_daily}% of your daily target). This is a general estimate - actual values may vary based on preparation and portion size.",
            "food_analysis": food_analysis,
            "health_tips": [
                "Consider portion sizes when eating",
                "Balance with other nutrients throughout the day"
            ],
            "portion_recommendation": "Moderate portion recommended for weight loss goals"
        }
