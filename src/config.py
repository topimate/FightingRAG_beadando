
import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()

# Groq
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")

# Local Transformer
EMBEDDING_MODEL = "intfloat/multilingual-e5-small"

# Retrieval
TOP_K = 6
COLLECTION_NAME = "fight_rules"

# Paths
CHUNKS_PATH = Path("data/processed/chunks.jsonl")
DB_PATH = "data/chroma_db"

# LLM generation
MAX_COMPLETION_TOKENS = 2000
TEMPERATURE = 0
REASONING_EFFORT = "low"

if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY is missing from the .env file."
    )
