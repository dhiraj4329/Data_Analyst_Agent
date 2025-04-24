from app.config import LLM, get_prompt, log
from langchain.prompts import ChatPromptTemplate

def aggregator_node(state: dict) -> dict:
    """Aggregates the results of all executed subtasks and generates a final summary."""
    subtask_outputs = state.get("subtask_outputs", [])

    if not subtask_outputs:
        return {**state, "final_summary": "No subtasks were completed."}

    # Format for the LLM
    text_block = ""
    for i, task in enumerate(subtask_outputs):
        text_block += f"\n{i+1}. {task['subtask']}\n"
        if "preview" in task:
            text_block += f"   Output: {task['preview']}\n"
        elif "error" in task:
            text_block += f"   Error: {task['error']}\n"

    # Load the prompt
    prompt_text = get_prompt("answer_combiner")
    prompt = ChatPromptTemplate.from_template(prompt_text)
    chain = prompt | LLM

    # Run the LLM
    result = chain.invoke({"subtask_outputs": text_block})
    summary = result.content.strip()

    return {
        **state,
        "final_summary": summary,
        "aggregator_status": "ok"
    }

# def answer_combiner_node(state: dict) -> dict:
#     subtask_outputs = state.get("subtask_outputs", [])

#     if not subtask_outputs:
#         return {**state, "final_summary": "No subtasks were completed."}

#     # Format for the LLM
#     text_block = ""
#     for i, task in enumerate(subtask_outputs):
#         text_block += f"\n{i+1}. {task['subtask']}\n"
#         if "preview" in task:
#             text_block += f"   Output: {task['preview']}\n"
#         elif "error" in task:
#             text_block += f"   Error: {task['error']}\n"

#     # Load the prompt
#     prompt_text = get_prompt("answer_combiner")
#     prompt = ChatPromptTemplate.from_template(prompt_text)
#     chain = prompt | LLM

#     # Run the LLM
#     result = chain.invoke({"subtask_outputs": text_block})
#     summary = result.content.strip()

#     return {
#         **state,
#         "final_summary": summary,
#         "combiner_status": "ok"
#     }