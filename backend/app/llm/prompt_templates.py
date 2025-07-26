from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser


parser = JsonOutputParser()

chunk_summary_prompt = PromptTemplate(
        input_variables=["chunk_text"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
        template="""
You are analyzing an excerpt from a legal or regulatory document.

Your task is to generate a short, informative description of this chunk. Focus on extracting any clause titles, section numbers, or semantic topic (e.g., "Termination Clause", "Confidentiality", "Jurisdiction", etc.).

The description should be brief but meaningful, so that chunks with similar purposes can later be grouped or merged together.

Return your response as a JSON object in the following format:

{{
  "description": "<short but specific semantic label for this chunk>"
}}

{format_instructions}

Text to analyze:
\"\"\"
{chunk_text}
\"\"\"
"""
    )

chat_prompt = PromptTemplate(
        input_variables=["chunk_text", "query"],
        template="""
You are a legal assistant. Based on the following legal content, answer the question clearly and concisely.

However, if someone greets with "Hi" or "Hello" greet them back or if someone asks some general question about you, then answer without relying on the chunks.
But if the question is out of context of legal scenarios, then respond with: 'I'm designed to assist with legal document-related queries. Please ask something relevant to the uploaded legal document.

Text to analyze:
\"\"\"
{chunk_text}
\"\"\"

Question: {query}
"""
    )


