# transcript_processor.py
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.graph import END, StateGraph
from typing import TypedDict, List, Dict, Any
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

# Load environment variables
load_dotenv()

# Configure the LLM using Groq API
llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama3-70b-8192"  # Using Llama 3 as specified
)

# Define the state structure for our graph
class AgentState(TypedDict):
    transcript: str
    summary: str
    action_items: List[Dict[str, str]]
    current_step: str

# Define the nodes for our graph (each represents a processing step)
def summarize_transcript(state: AgentState) -> AgentState:
    """Generate a comprehensive summary of the meeting transcript."""
    system_prompt = """
    You are an expert meeting assistant. Your task is to create a comprehensive 
    summary of the provided meeting transcript. Focus on key discussion points, 
    decisions made, and the overall narrative of the meeting. Be concise yet thorough.
    """
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Here is the meeting transcript to summarize:\n\n{state['transcript']}")
    ]
    
    response = llm.invoke(messages)
    state["summary"] = response.content
    state["current_step"] = "summarize_transcript_completed"
    
    return state

def extract_action_items(state: AgentState) -> AgentState:
    """Extract action items from the meeting transcript."""
    system_prompt = """
    You are an expert meeting assistant. Your task is to extract all action items from 
    the provided meeting transcript. For each action item, identify:
    1. The task to be completed
    2. The person responsible (if mentioned)
    3. The deadline (if mentioned)
    
    Format each action item as a dictionary with keys: "task", "assignee", "deadline".
    If some information is not available, use null for that field.
    """
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Here is the meeting transcript to extract action items from:\n\n{state['transcript']}")
    ]
    
    response = llm.invoke(messages)
    
    try:
        # Process the response to structure action items
        # This is simplified; in a real implementation, you might want more robust parsing
        action_text = response.content
        
        # Simple parsing approach - we're assuming the LLM returns a formatted list
        # A more robust approach would be to have the LLM return JSON directly
        items = []
        for line in action_text.split("\n"):
            line = line.strip()
            if line and not line.startswith("Action Items") and not line.startswith("---"):
                # Basic parsing - in a production system, use a more robust approach
                if ":" in line and line[0].isdigit():
                    task = line.split(":", 1)[1].strip()
                    items.append({"task": task, "assignee": None, "deadline": None})
                elif "Task:" in line:
                    task_parts = line.split("Task:", 1)
                    if len(task_parts) > 1:
                        task = task_parts[1].strip()
                        assignee = None
                        deadline = None
                        
                        # Look for assignee and deadline in subsequent lines
                        if "Assignee:" in action_text:
                            assignee_parts = action_text.split("Assignee:", 1)
                            if len(assignee_parts) > 1:
                                assignee = assignee_parts[1].split("\n", 1)[0].strip()
                        
                        if "Deadline:" in action_text:
                            deadline_parts = action_text.split("Deadline:", 1)
                            if len(deadline_parts) > 1:
                                deadline = deadline_parts[1].split("\n", 1)[0].strip()
                        
                        items.append({"task": task, "assignee": assignee, "deadline": deadline})
        
        # If parsing fails or no items found, ask LLM to format more explicitly
        if not items:
            clarify_messages = [
                SystemMessage(content="Extract the action items as a Python list of dictionaries, with each dictionary having 'task', 'assignee', and 'deadline' keys."),
                HumanMessage(content=f"Based on this meeting transcript:\n\n{state['transcript']}\n\nProvide the action items in the specified format.")
            ]
            clarify_response = llm.invoke(clarify_messages)
            # This would need additional parsing in a production system
            items = eval(clarify_response.content) if "action_items = [" in clarify_response.content else []
        
        state["action_items"] = items
        
    except Exception as e:
        # Fallback for production - handle parsing errors
        state["action_items"] = [{"task": "Error parsing action items", "assignee": None, "deadline": None}]
        print(f"Error extracting action items: {e}")
    
    state["current_step"] = "extract_action_items_completed"
    return state

# Define the agent workflow as a graph
def create_agent_graph():
    # Initialize the graph
    workflow = StateGraph(AgentState)
    
    # Add nodes to the graph
    workflow.add_node("summarize_transcript", summarize_transcript)
    workflow.add_node("extract_action_items", extract_action_items)
    
    # Define the edges (the flow between nodes)
    workflow.add_edge("summarize_transcript", "extract_action_items")
    workflow.add_edge("extract_action_items", END)
    
    # Set the entry point
    workflow.set_entry_point("summarize_transcript")
    
    # Compile the graph
    return workflow.compile()

# Main function to process a transcript
def process_transcript(transcript_text: str) -> Dict[str, Any]:
    """
    Process a meeting transcript using the LangGraph agent.
    
    Args:
        transcript_text: The text of the meeting transcript
        
    Returns:
        A dictionary containing the summary and action items
    """
    # Create the agent graph
    agent = create_agent_graph()
    
    # Initialize the state
    initial_state = AgentState(
        transcript=transcript_text,
        summary="",
        action_items=[],
        current_step="start"
    )
    
    # Run the agent
    result = agent.invoke(initial_state)
    
    # Return the processed results
    return {
        "summary": result["summary"],
        "action_items": result["action_items"]
    }

# For testing purposes
if __name__ == "__main__":
    sample_transcript = """
    Meeting Start: 10:00 AM, April 1, 2025
    
    John: Good morning everyone. Let's get started with our product roadmap discussion.
    
    Sarah: I've prepared the Q3 feature list as we discussed last week.
    
    John: Great! Can you walk us through the priorities?
    
    Sarah: Sure. We need to finish the authentication system by May 15th. Michael, can you lead that?
    
    Michael: Yes, I'll take care of it and provide weekly updates.
    
    John: Perfect. What about the reporting dashboard?
    
    Sarah: That's scheduled for June deployment. Emily will handle the design by April 15th, and then the development team will implement it by June 1st.
    
    Emily: I'll have the mockups ready by next Friday for review.
    
    John: Sounds good. Let's also make sure we address the customer feedback about mobile responsiveness.
    
    Michael: I'll add that to my backlog and aim to complete it by the end of April.
    
    John: Excellent. Anything else we need to discuss?
    
    Sarah: We should schedule a user testing session for the new features.
    
    John: Good point. Emily, can you organize that for mid-June?
    
    Emily: Will do. I'll send calendar invites by the end of this week.
    
    John: Thanks everyone. Let's meet again next Tuesday to check progress.
    
    Meeting End: 10:45 AM
    """
    
    results = process_transcript(sample_transcript)
    print("Summary:", results["summary"])
    print("\nAction Items:", results["action_items"])