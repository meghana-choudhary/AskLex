from langchain.vectorstores import FAISS
from langchain.schema import Document
from app import config

embedding_model= config.EMBEDDING_MODEL_NAME

def build_faiss_index(stitched_chunks):
    print("🔄 Pushing stitched chunks to FAISS...")

    # Filter only valid chunks
    valid_chunks = [
        chunk for chunk in stitched_chunks
        if chunk.get("description") 
    ]

    # Convert to LangChain Documents
    documents = []
    for chunk in valid_chunks:
        doc = Document(
            page_content=chunk["description"],  # what will be embedded
            metadata={
                "start_chunk_id": chunk["start_chunk_id"],
                "end_chunk_id": chunk["end_chunk_id"],
                "text": chunk["text"],  # optional, for context
            }
        )
        documents.append(doc)

    # Build FAISS index using LangChain
    vector_store = FAISS.from_documents(documents, embedding=embedding_model)

    return vector_store


