from app.llm.gemini_client import get_chat_chain
from app import config

top_k_results= config.TOP_K_RESULTS

def get_similar_chunks(faiss_index, query):
    results = faiss_index.similarity_search(query, top_k_results)
    
    original_chunks = [doc.metadata.get("text", "") for doc in results]
    context = "\n\n".join(original_chunks)
    
    return context

def get_llm_response(context, query):
    chain= get_chat_chain()
    result = chain.invoke({"chunk_text": context, "query": query})
    return result


    


