from __future__ import annotations
import json
from typing import Dict, Any, Literal
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from state import State, NutritionProfile

Activity = Literal["sedentary", "light", "moderate", "active", "very_active"]

def nutritionist(state: State) -> Dict[str, Any]:
    """
    Enhanced Nutritionist agent - analyzes user profile and provides intelligent nutritional assessment using LLM.
    """
    user_profile = state.get("user_profile", {})
    
    # First calculate basic metrics
    basic_nutrition = _calculate_basic_metrics(user_profile)
    
    # Then enhance with LLM analysis
    enhanced_analysis = _generate_enhanced_analysis(user_profile, basic_nutrition)
    
    return {
        "message": enhanced_analysis.get("message", "Nutritional analysis complete."),
        "nutrition_profile": enhanced_analysis.get("nutrition_profile", basic_nutrition)
    }


def _calculate_basic_metrics(profile: Dict[str, Any]) -> NutritionProfile:
    """Calculate basic nutritional metrics (BMI, BMR, TDEE, etc.)"""
    try:
        weight = float(profile["weight_kg"])
        height_m = float(profile["height_cm"]) / 100.0
        age = int(profile["age"])
        sex = profile["sex"]
        activity_level = profile["activity_level"]
        
        # Calculate BMI
        bmi = round(weight / (height_m ** 2), 2)
        bmi_class = _get_bmi_class(bmi)
        
        # Calculate BMR using Mifflin-St Jeor Equation
        if sex == "male":
            bmr = 10 * weight + 6.25 * (height_m * 100) - 5 * age + 5
        else:
            bmr = 10 * weight + 6.25 * (height_m * 100) - 5 * age - 161
        
        # Calculate TDEE
        activity_multiplier = _get_activity_multiplier(activity_level)
        tdee = bmr * activity_multiplier
        
        # Calculate target calories for weight loss (500 cal deficit, minimum 1200)
        target_calories = max(int(round(tdee - 500)), 1200)
        
        # Calculate recommended macros (example ratios for weight loss)
        recommended_macros = {
            "protein_g": round(weight * 1.6, 1),  # 1.6g per kg body weight
            "carbs_g": round(target_calories * 0.4 / 4, 1),  # 40% of calories
            "fat_g": round(target_calories * 0.3 / 9, 1)  # 30% of calories
        }
        
        return NutritionProfile(
            bmi=bmi,
            bmi_class=bmi_class,
            bmr=round(bmr, 1),
            tdee=round(tdee, 1),
            target_calories=target_calories,
            recommended_macros=recommended_macros,
            health_assessment=""  # Will be filled by LLM
        )
        
    except (KeyError, ValueError, TypeError) as e:
        # Fallback values if calculation fails
        return NutritionProfile(
            bmi=22.0,
            bmi_class="normal",
            bmr=1500.0,
            tdee=1800.0,
            target_calories=1300,
            recommended_macros={"protein_g": 100.0, "carbs_g": 130.0, "fat_g": 43.0},
            health_assessment="Unable to calculate precise metrics due to missing data."
        )


def _generate_enhanced_analysis(user_profile: Dict[str, Any], basic_nutrition: NutritionProfile) -> Dict[str, Any]:
    """Generate enhanced nutritional analysis using LLM."""
    
    system_prompt = """You are a professional nutritionist with expertise in weight management and healthy eating. 
    
    Analyze the user's profile and basic nutritional metrics to provide:
    1. Health assessment based on BMI and other factors
    2. Personalized recommendations for their weight loss journey
    3. Insights about their metabolic profile
    4. Practical advice in a friendly, encouraging tone
    
    Consider:
    - Their current BMI status and health implications
    - Age and sex-specific nutritional needs
    - Activity level and caloric requirements
    - Realistic and sustainable weight loss approach
    
    Respond in a professional but warm tone. Use some Singlish expressions naturally but keep it informative.
    
    Return JSON with:
    - "message": Your detailed nutritional analysis and recommendations
    - "nutrition_profile": Enhanced nutrition profile with "health_assessment" field filled
    - "key_insights": List of 3-4 key insights about their profile
    """
    
    user_prompt = f"""User Profile:
Age: {user_profile.get('age', 'Unknown')}
Sex: {user_profile.get('sex', 'Unknown')}
Height: {user_profile.get('height_cm', 'Unknown')} cm
Weight: {user_profile.get('weight_kg', 'Unknown')} kg
Activity Level: {user_profile.get('activity_level', 'Unknown')}
First Meal: {user_profile.get('first_meal', 'Unknown')}

Calculated Metrics:
BMI: {basic_nutrition['bmi']} ({basic_nutrition['bmi_class']})
BMR: {basic_nutrition['bmr']} calories/day
TDEE: {basic_nutrition['tdee']} calories/day
Target Calories: {basic_nutrition['target_calories']} calories/day
Recommended Macros: {basic_nutrition['recommended_macros']}

Provide your professional nutritional analysis and recommendations."""

    try:
        llm = ChatOpenAI(model="gpt-5-nano", temperature=1)
        
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ])
        
        result = json.loads(response.content)
        
        # Merge the enhanced nutrition profile with basic metrics
        enhanced_nutrition = {**basic_nutrition}
        if "nutrition_profile" in result and "health_assessment" in result["nutrition_profile"]:
            enhanced_nutrition["health_assessment"] = result["nutrition_profile"]["health_assessment"]
        
        return {
            "message": result.get("message", "Nutritional analysis complete."),
            "nutrition_profile": enhanced_nutrition,
            "key_insights": result.get("key_insights", [])
        }
        
    except Exception as e:
        print(f"Error in nutritionist LLM call: {e}")
        
        # Fallback analysis
        bmi_status = basic_nutrition["bmi_class"]
        if bmi_status == "underweight":
            health_msg = "Your BMI indicates you're underweight. Focus on healthy weight gain with nutrient-dense foods."
        elif bmi_status == "normal":
            health_msg = "Great! Your BMI is in the healthy range. Maintain this with balanced nutrition and regular exercise."
        elif bmi_status == "overweight":
            health_msg = "Your BMI indicates you're overweight. A gradual weight loss approach will help you reach a healthier weight."
        else:  # obese
            health_msg = "Your BMI indicates obesity. Consider consulting a healthcare provider for a comprehensive weight management plan."
        
        enhanced_nutrition = {**basic_nutrition}
        enhanced_nutrition["health_assessment"] = health_msg
        
        return {
            "message": f"Based on your profile: BMI {basic_nutrition['bmi']} ({bmi_status}), BMR {basic_nutrition['bmr']} cal/day, TDEE {basic_nutrition['tdee']} cal/day. Target: {basic_nutrition['target_calories']} cal/day for weight loss. {health_msg}",
            "nutrition_profile": enhanced_nutrition
        }


def _get_bmi_class(bmi: float) -> str:
    """Classify BMI into standard categories."""
    if bmi < 18.5:
        return "underweight"
    elif bmi < 25:
        return "normal"
    elif bmi < 30:
        return "overweight"
    else:
        return "obese"


def _get_activity_multiplier(level: Activity) -> float:
    """Get activity multiplier for TDEE calculation."""
    multipliers = {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "active": 1.725,
        "very_active": 1.9,
    }
    return multipliers.get(level, 1.2)
