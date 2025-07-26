from app.services.text_processing import *
from app.services.chat import *

if __name__ == "__main__":
    file_path="../documents/LegalCase1.PDF"
    query="your query here"
    text=extract_text(file_path)
    stitched_chunks= get_chunks(text)
    faiss_index= get_faiss_index(stitched_chunks)
    similar_chunks= get_similar_chunks(faiss_index, query)
    response= get_llm_response(similar_chunks, query)
    print(response)


