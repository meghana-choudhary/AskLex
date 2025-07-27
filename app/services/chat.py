from app.llm.gemini_client import get_chat_chain, get_agg_query_chain
from app import config

top_k_results= config.TOP_K_RESULTS

def get_aggregated_query(queries, current_question):
    chain= get_agg_query_chain()
    response = chain.invoke(
        {"previous_questions": queries, "current_question": current_question}
    )
    result = response["aggregated_question"] if response.get("aggregated_question") else current_question

    return result

def get_similar_chunks(faiss_index, query):
    results = faiss_index.similarity_search(query, top_k_results)
    
    original_chunks = [doc.metadata.get("text", "") for doc in results]
    context = "\n\n".join(original_chunks)
    
    return context

def get_llm_response(context, query):
    chain= get_chat_chain()
    result = chain.invoke({"chunk_text": context, "query": query})
    return result


    


