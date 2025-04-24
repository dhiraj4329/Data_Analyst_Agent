from pathlib import Path
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

# =========
# 📁 Paths
# =========

# Project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Prompt templates folder
PROMPT_PATH = PROJECT_ROOT / "app" / "prompts"

# Data folder
DATA_PATH = PROJECT_ROOT / "data"

# Output folder (charts, summaries, logs)
OUTPUT_PATH = PROJECT_ROOT / "output"

# ===========
# 🤖 LLM Setup
# ===========

# Use DeepSeek R1 14B running locally with Ollama
LLM = ChatGroq(
    model="deepseek-r1-distill-llama-70b",  # or "deepseek:latest"
    temperature=0.2
)

# ============
# 🛠 Utilities
# ============

def get_prompt(name: str) -> str:
    """Load a prompt from the prompts folder by filename (without .txt)."""
    prompt_file = PROMPT_PATH / f"{name}.txt"
    if not prompt_file.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_file}")
    return prompt_file.read_text()

def log(msg: str):
    """Basic debug logger."""
    print(f"[log] {msg}")