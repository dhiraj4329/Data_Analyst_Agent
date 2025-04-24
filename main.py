import streamlit as st
from app.graphs.agent_graph import build_agent_graph
from pathlib import Path
import tempfile
import os

st.title("Data Analyst Agent")

# User input for prompt
input_text = st.text_input("Enter your analysis request:", "Show a bar chart of sales by region.")

# File uploader for dataset
uploaded_file = st.file_uploader("Upload your CSV dataset", type=["csv"])

if uploaded_file is not None:
    # Save uploaded file to a temporary location
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp_file:
        tmp_file.write(uploaded_file.read())
        dataset_path = Path(tmp_file.name)

    if st.button("Run Analysis"):
        graph = build_agent_graph()
        final_state = graph.invoke({
            "input": input_text,
            "dataset_path": dataset_path
        })

        st.success("✅ FINAL SUMMARY:")
        st.write(final_state.get("final_summary", "[No summary generated]"))

        st.info("📋 SUBTASK OUTPUTS:")
        for idx, task in enumerate(final_state.get("subtask_outputs", [])):
            st.markdown(f"**Subtask {idx + 1}: {task.get('subtask')}**")
            if "preview" in task:
                st.write("Result Preview:", task["preview"])
            if "error" in task:
                st.error(f"Error: {task['error']}")

    # Clean up temp file after use
    os.unlink(dataset_path)
else:
    st.info("Please upload a CSV file to begin.")