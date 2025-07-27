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

agg_query_prompt= PromptTemplate(
        input_variables=["previous_questions", "current_question"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
        template="""
        You are given a list of previously asked questions and a recently asked question. Your task is to analyze and combine all questions into a single, concise, and coherent question that captures the full intent and context provided across them.

        The final question should preserve the core meaning of each input question.

        Use pronoun resolution to replace ambiguous references like "this", "that" or "it" with the correct noun.

        Assume all questions are about the same underlying subject unless otherwise stated.

        Return the aggregated question in a JSON format with the key "aggregated_question". Do not give extra information.

        If the the recently asked question is of different subject then, return the recently asked question as it is in the "aggregated_question".

        Please follow instructions and give response in exact format without extra commentry.
        Format:

        {{
            "aggregated_question": "The aggregated question"
        }}

        Example Inputs:

        **Previously Asked Questions**
        1. What are the charges under this section?

        **Recently Asked Question**
        Explain the second one.

        **Output**:
        {{
            "aggregated_question": "Explain the second among charges under this section?"
        }}


        **Previously Asked Questions**
        1.What crime is described in section 1.5?
        2.What is its punishment?

        **Recently Asked Question**
        How long did he serve that punishment?

        **Output**:
        {{
            "aggregated_question": "How long he served the punishment for crime described in section 1.5?"
        }}

        {format_instructions}

        **Previously Asked Questions**
        {previous_questions}

        **Recently Asked Question**
        {current_question}

        **Final Answer**
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


