# Agents module for Can-Eat-Not multi-agent system

from .trainer import trainer
from .nutritionist import nutritionist
from .food_specialist import food_specialist

__all__ = ["trainer", "nutritionist", "food_specialist"]
