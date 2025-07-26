from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import JsonOutputParser
from app.llm.prompt_templates import chunk_summary_prompt, chat_prompt
from app import config

llm = ChatGoogleGenerativeAI(
        model=config.LLM_MODEL_NAME,
        temperature=0.2,
        api_key=config.GOOGLE_API_KEY
    )

def get_summary_chain():
    parser = JsonOutputParser()
    return chunk_summary_prompt | llm | parser

def get_chat_chain():
    return chat_prompt | llm