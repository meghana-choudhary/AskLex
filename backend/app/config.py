# config.py
import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# Load environment variables from .env file
load_dotenv()

# API and Model Configurations
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
EMBEDDING_MODEL_NAME = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-exp-03-07")
LLM_MODEL_NAME = "gemini-2.5-flash-lite"

# Text Processing Configurations
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 100
STITCHING_THRESHOLD = 0.75 # Cosine similarity threshold for stitching chunks
THRESHOLD_MARGIN = 1e-5

# Vector Store Configurations
TOP_K_RESULTS = 5