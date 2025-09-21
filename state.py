from typing import TypedDict, List, Dict, Any, Optional, Literal


class Message(TypedDict):
    """Individual message in conversation"""
    role: Literal["user", "trainer", "nutritionist", "food_specialist"]
    content: str
    timestamp: Optional[str]


class UserProfile(TypedDict, total=False):
    """User profile information collected by trainer"""
    age: int
    sex: Literal["male", "female"]
    height_cm: float
    weight_kg: float
    activity_level: Literal["sedentary", "light", "moderate", "active", "very_active"]
    first_meal: bool
    dietary_restrictions: Optional[str]
    health_goals: Optional[str]


class NutritionProfile(TypedDict, total=False):
    """Nutritional analysis from nutritionist"""
    bmi: float
    bmi_class: str
    bmr: float
    tdee: float
    target_calories: int
    recommended_macros: Dict[str, float]
    health_assessment: str


class FoodAnalysis(TypedDict, total=False):
    """Food analysis from food specialist"""
    food_item: str
    quantity: str
    calories_per_unit: int
    total_calories: int
    macros: Dict[str, float]
    nutritional_notes: str
    health_impact: str


class State(TypedDict):
    """
    Overall state of the Can-Eat-Not LangGraph system.
    """
    # Conversation management
    messages: List[Message]
    current_user_input: str
    awaiting_user_input: bool
    
    # User data
    user_profile: UserProfile
    profile_complete: bool
    
    # Agent outputs
    nutrition_profile: NutritionProfile
    food_analysis: FoodAnalysis
    
    # Flow control
    current_phase: Literal["greeting", "profile_collection", "nutrition_analysis", "food_analysis", "recommendation", "complete"]
    next_agent: Literal["trainer", "nutritionist", "food_specialist", "human"]
    
    # Food request tracking
    food_request: Optional[str]
    food_request_pending: bool
    awaiting_food_request: bool
    
    # Final recommendation
    final_recommendation: str
    can_eat_verdict: bool
    
    # Session management
    session_complete: bool
