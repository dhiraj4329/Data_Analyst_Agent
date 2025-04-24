import pandas as pd
from app.config import DATA_PATH, get_prompt, LLM, log
from langchain.prompts import ChatPromptTemplate
import traceback
import re

def extract_python_code(text):
    # Extract content between ```python and ``` tags
    pattern = r'```python\s*(.*?)\s*```'
    match = re.search(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return None

def executor_step_node(state: dict) -> dict:
    """Executes a single subtask and updates the state."""
    subtasks = state.get("subtasks", [])
    executed = state.get("executed", [])
    subtask_outputs = state.get("subtask_outputs", [])
    dataset_name = state.get("dataset", "subway_ridership.csv")
    dataset_path = f"{DATA_PATH}/{dataset_name}"
    
    # Determine which subtask to execute next
    current_index = len(executed)
    if current_index >= len(subtasks):
        return {**state, "executor_status": "complete"}
    
    current_subtask = subtasks[current_index]
    log(f"Executing subtask [{current_index + 1}/{len(subtasks)}]: {current_subtask}")
    
    # Load the dataset
    try:
        df = pd.read_csv(dataset_path)
    except Exception as e:
        return {
            **state, 
            "subtask_outputs": subtask_outputs,
            "executor_status": f"error loading CSV: {e}"
        }

    # Prepare prompt
    prompt_text = get_prompt("executor_agent")
    prompt = ChatPromptTemplate.from_template(prompt_text)
    
    max_retries = 5
    retry_count = 0
    success = False
    
    # Initial code generation
    try:
        chain = prompt | LLM
        response = chain.invoke({
            "subtask": current_subtask,
            "columns": df.columns.tolist(),
            "preview": df.sample(5).to_dict(orient="records"),
        })
        code = extract_python_code(response.content.strip())
        log(f"Generated Code:\n{code}")
    except Exception as e:
        output = {
            "subtask": current_subtask,
            "error": f"Error generating initial code: {str(e)}",
            "traceback": traceback.format_exc()
        }
        subtask_outputs.append(output)
        executed.append(current_subtask)
        return {
            **state,
            "subtask_outputs": subtask_outputs,
            "executed": executed
        }
        
    # Retry loop
    while retry_count < max_retries and not success:
        try:
            # Run the code safely
            local_vars = {"df": df.copy(), "pd": pd}
            exec(code, {}, local_vars)
            result = local_vars.get("result", None)
            
            if result is None:
                raise ValueError("No result variable found.")
            
            # If we get here, code executed successfully
            success = True
            
        except Exception as e:
            error_message = str(e)
            error_traceback = traceback.format_exc()
            retry_count += 1
            
            if retry_count >= max_retries:
                log(f"Failed after {max_retries} attempts. Last error: {error_message}")
                break
                
            # Send error to LLM for fixing
            fix_prompt = ChatPromptTemplate.from_template(
                """You are a Python expert. Fix this code that produced an error.
                
                    Original code:
                    ```python
                    {code}
                    ```

                    Error message:
                    ```
                    {error}
                    ```

                    Fixed code (return only the code):"""
                )
            
            try:
                fix_chain = fix_prompt | LLM
                fix_response = fix_chain.invoke({
                    "code": code,
                    "error": f"{error_message}\n{error_traceback}"
                })
                
                # Extract code from response
                code = re.sub(r'```python\s*(.*?)\s*```', r'\1', fix_response.content, flags=re.DOTALL)
                code = code.replace('```', '').strip()
                
                log(f"Retry {retry_count}/{max_retries}. Fixed code:\n{code}")
            except Exception as fix_error:
                log(f"Error while trying to fix code: {str(fix_error)}")
                break
    
    # After retry loop, record results
    if success:
        preview = result.head().to_dict("records") if isinstance(result, pd.DataFrame) else str(result)
        output = {
            "subtask": current_subtask,
            "code": code,
            "preview": preview,
            "retries": retry_count
        }
    else:
        output = {
            "subtask": current_subtask,
            "code": code,
            "error": error_message if 'error_message' in locals() else "Unknown error",
            "traceback": error_traceback if 'error_traceback' in locals() else "",
            "retries": retry_count
        }
    
    # Update state
    subtask_outputs.append(output)
    executed.append(current_subtask)
    
    return {
        **state,
        "subtask_outputs": subtask_outputs,
        "executed": executed,
        "executor_status": "ok"
    }

# def executor_agent_node(state: dict) -> dict:
#     subtasks = state.get("subtasks", [])
#     dataset_name = state.get("dataset", "subway_ridership.csv")
#     dataset_path = f"{DATA_PATH}/{dataset_name}"
#     subtask_outputs = []

#     # Load the dataset once
#     try:
#         df = pd.read_csv(dataset_path)
#     except Exception as e:
#         return {**state, "subtask_outputs": [], "executor_status": f"error loading CSV: {e}"}

#     # Prepare prompt
#     prompt_text = get_prompt("executor_agent")
#     prompt = ChatPromptTemplate.from_template(prompt_text)

#     for idx, subtask in enumerate(subtasks):
#         log(f"Executing subtask [{idx + 1}]: {subtask}")
        
#         max_retries = 5
#         retry_count = 0
#         success = False
        
#         # Initial code generation
#         try:
#             chain = prompt | LLM
#             response = chain.invoke({
#                 "subtask": subtask,
#                 "columns": df.columns.tolist(),
#                 "preview": df.sample(5).to_dict(orient="records"),
#             })
#             code = extract_python_code(response.content.strip())
#             log(f"Generated Code:\n{code}")
#         except Exception as e:
#             subtask_outputs.append({
#                 "subtask": subtask,
#                 "error": f"Error generating initial code: {str(e)}",
#                 "traceback": traceback.format_exc()
#             })
#             continue
            
#         # Retry loop
#         while retry_count < max_retries and not success:
#             try:
#                 # Run the code safely
#                 local_vars = {"df": df.copy(), "pd": pd}
#                 exec(code, {}, local_vars)
#                 result = local_vars.get("result", None)
                
#                 if result is None:
#                     raise ValueError("No result variable found.")
                
#                 # If we get here, code executed successfully
#                 success = True
                
#             except Exception as e:
#                 error_message = str(e)
#                 error_traceback = traceback.format_exc()
#                 retry_count += 1
                
#                 if retry_count >= max_retries:
#                     log(f"Failed after {max_retries} attempts. Last error: {error_message}")
#                     break
                    
#                 # Send error to LLM for fixing
#                 fix_prompt = ChatPromptTemplate.from_template(
#                     """You are a Python expert. Fix this code that produced an error.
                    
#                         Original code:
#                         ```python
#                         {code}
#                         ```

#                         Error message:
#                         ```
#                         {error}
#                         ```

#                         Fixed code (return only the code):"""
#                     )
                
#                 try:
#                     fix_chain = fix_prompt | LLM
#                     fix_response = fix_chain.invoke({
#                         "code": code,
#                         "error": f"{error_message}\n{error_traceback}"
#                     })
                    
#                     # Extract code from response
#                     code = re.sub(r'```python\s*(.*?)\s*```', r'\1', fix_response.content, flags=re.DOTALL)
#                     code = code.replace('```', '').strip()
                    
#                     log(f"Retry {retry_count}/{max_retries}. Fixed code:\n{code}")
#                 except Exception as fix_error:
#                     log(f"Error while trying to fix code: {str(fix_error)}")
#                     break
        
#         # After retry loop, record results
#         if success:
#             preview = result.head().to_dict("records") if isinstance(result, pd.DataFrame) else str(result)
#             subtask_outputs.append({
#                 "subtask": subtask,
#                 "code": code,
#                 "preview": preview,
#                 "retries": retry_count
#             })
#         else:
#             subtask_outputs.append({
#                 "subtask": subtask,
#                 "code": code,
#                 "error": error_message if 'error_message' in locals() else "Unknown error",
#                 "traceback": error_traceback if 'error_traceback' in locals() else "",
#                 "retries": retry_count
#             })
    
#     return {
#         **state,
#         "subtask_outputs": subtask_outputs,
#         "executor_status": "ok"
#     }