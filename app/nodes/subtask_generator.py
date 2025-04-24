from app.config import LLM, get_prompt
from langchain.prompts import ChatPromptTemplate
import re
import ast

def subtask_generator_node(state: dict) -> dict:
    """Generate a list of subtasks from a complex analysis query."""

    # Get user input
    user_input = state.get("input", "")

    if not user_input:
        return {**state, "subtasks": [], "subtask_status": "error: no input"}
    
    # Load prompt
    prompt_text = get_prompt("subtask_generator")
    prompt = ChatPromptTemplate.from_template(prompt_text)

    # Generate subtasks
    # Run prompt through LLM
    chain = prompt | LLM
    result = chain.invoke({"input": user_input})
    
    # Extract content and clean it
    content = result.content
    
    # Remove any content between <think> and </think> tags
    content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL)
    
    # Try to extract the list from the response
    try:
        # Look for content that appears to be a list
        if '[' in content and ']' in content:
            list_content = content[content.find('['):content.rfind(']')+1]
            # Convert string representation of list to actual list
            subtasks = ast.literal_eval(list_content)
        else:
            # Check for numbered list format (1. Task one, 2. Task two)
            numbered_tasks = re.findall(r'^\d+\.\s*(.*?)$', content, re.MULTILINE)
            if numbered_tasks:
                subtasks = numbered_tasks
            else:
                # If no list format found, split by lines and clean
                lines = [line.strip() for line in content.split('\n') 
                         if line.strip() and not line.startswith('#')]
                
                # Further clean the lines to remove list markers if present
                subtasks = []
                for line in lines:
                    # Remove bullet points, dashes, or other list markers
                    cleaned = re.sub(r'^[-*•⦁◦▪▫■□●○]\s*', '', line)
                    if cleaned:
                        subtasks.append(cleaned)
    except Exception as e:
        # If parsing fails, split by newlines as a last resort
        subtasks = [line.strip() for line in content.split('\n') 
                   if line.strip() and not line.startswith(('#', '```'))]
        if not subtasks:
            subtasks = [content.strip()]

    return {**state, "subtasks": subtasks}