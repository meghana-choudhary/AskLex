from langchain.vectorstores import FAISS
from langchain.schema import Document
from app import config

embedding_model = config.EMBEDDING_MODEL_NAME

def build_faiss_index(stitched_chunks, progress_callback=None, batch_size=10):
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

    total = len(documents)
    embedded_docs = []

    for i in range(0, total, batch_size):
        batch = documents[i:i+batch_size]
        # Embedding will be handled inside from_documents, so just track progress manually
        embedded_docs.extend(batch)

        if progress_callback:
            percent = int(((i + batch_size) / total) * 100)
            progress_callback("embedding_generation", min(percent, 100))

    # Final FAISS index creation
    vector_store = FAISS.from_documents(embedded_docs, embedding=embedding_model)

    return vector_store



