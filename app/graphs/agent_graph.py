from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Dict, Any, Optional

from app.nodes.subtask_generator import subtask_generator_node
from app.nodes.executor_node import executor_step_node  # one subtask at a time
from app.nodes.aggregator_node import aggregator_node

# Define the state schema
class TaskOutput(TypedDict):
    subtask: str
    preview: Optional[str]
    error: Optional[str]

class AgentState(TypedDict):
    input: str
    dataset_path: str
    subtasks: List[str]
    executed: List[int]
    subtask_outputs: List[TaskOutput]
    final_summary: Optional[str]

def build_agent_graph():
    # Initialize with state schema
    graph = StateGraph(AgentState)

    # Add all nodes
    graph.add_node("subtask_generator", subtask_generator_node)
    graph.add_node("executor", executor_step_node)
    graph.add_node("aggregator", aggregator_node)

    # Set the entry point
    graph.set_entry_point("subtask_generator")

    # Routing logic
    def route_after_executor(state: dict) -> str:
        subtasks = state.get("subtasks", [])
        executed = state.get("executed", [])

        if not subtasks:
            return "aggregator"
        if len(executed) < len(subtasks):
            return "executor"
        return "aggregator"

    # Define graph edges
    graph.add_edge("subtask_generator", "executor")
    graph.add_conditional_edges("executor", route_after_executor)
    graph.add_edge("aggregator", END)

    return graph.compile()