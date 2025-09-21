from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END

from state import State
from nodes import (
    human_node,
    check_session_status,
    determine_next_agent,
    trainer_node,
    nutritionist_node,
    food_specialist_node,
    completion_node
)

# Load environment variables
load_dotenv(override=True)


def build_graph():
    """
    Build the Can-Eat-Not LangGraph workflow.
    """
    builder = StateGraph(State)
    
    # Add all nodes
    builder.add_node("human", human_node)
    builder.add_node("trainer", trainer_node)
    builder.add_node("nutritionist", nutritionist_node)
    builder.add_node("food_specialist", food_specialist_node)
    builder.add_node("completion", completion_node)
    
    # Start with trainer for greeting
    builder.add_edge(START, "trainer")
    
    # From trainer, check if we need user input or can continue
    def after_trainer(state: State):
        if state.get("session_complete", False):
            return "completion"
        if state.get("awaiting_user_input", False):
            return "human"
        # Determine next agent based on state
        next_agent = determine_next_agent(state)
        return next_agent
    
    builder.add_conditional_edges(
        "trainer", 
        after_trainer, 
        {
            "human": "human",
            "nutritionist": "nutritionist", 
            "food_specialist": "food_specialist",
            "trainer": "trainer",
            "completion": "completion"
        }
    )
    
    # From human input, check session status
    builder.add_conditional_edges(
        "human",
        check_session_status,
        {
            "complete": "completion",
            "continue": "trainer"  # Always go to trainer first to handle input
        }
    )
    
    # From nutritionist, determine next step
    def after_nutritionist(state: State):
        return determine_next_agent(state)
    
    builder.add_conditional_edges(
        "nutritionist",
        after_nutritionist,
        {
            "trainer": "trainer",
            "food_specialist": "food_specialist",
            "human": "human"
        }
    )
    
    # From food specialist, determine next step
    def after_food_specialist(state: State):
        return determine_next_agent(state)
    
    builder.add_conditional_edges(
        "food_specialist",
        after_food_specialist,
        {
            "trainer": "trainer",
            "human": "human"
        }
    )
    
    # Completion node ends the flow
    builder.add_edge("completion", END)
    
    return builder.compile()


def main():
    """
    Main function to run the Can-Eat-Not application.
    """
    print("=== CAN-EAT-NOT: Multi-Agent Nutrition Assistant ===")
    print("🧑‍🏫 Trainer | 🥼 Nutritionist | 🍎 Food Specialist")
    print("Type 'exit', 'quit', or ':q' to end the session.\n")
    print("Let's help you make healthy food choices! 🌟\n")
    
    # Build the graph
    graph = build_graph()
    
    # Uncomment to see the graph structure
    # print("Graph structure:")
    # print(graph.get_graph().draw_ascii())
    # print("\n" + "="*50 + "\n")
    
    # Initialize state
    initial_state = State(
        messages=[],
        current_user_input="",
        awaiting_user_input=False,
        user_profile={},
        profile_complete=False,
        nutrition_profile={},
        food_analysis={},
        current_phase="greeting",
        next_agent="trainer",
        food_request=None,
        food_request_pending=False,
        awaiting_food_request=False,
        final_recommendation="",
        can_eat_verdict=False,
        session_complete=False
    )
    
    try:
        # Run the graph
        final_state = graph.invoke(initial_state)
        
        # Print final summary if available
        if final_state.get("final_recommendation"):
            print(f"\n{'='*50}")
            print("📋 FINAL SUMMARY:")
            print(f"{'='*50}")
            print(f"Recommendation: {final_state['final_recommendation']}")
            verdict = "✅ CAN EAT" if final_state.get("can_eat_verdict") else "❌ BETTER AVOID"
            print(f"Verdict: {verdict}")
            print(f"{'='*50}")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Session interrupted by user. Stay healthy! 👋")
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        print("Session ended. Please try again later.")


if __name__ == "__main__":
    main()
