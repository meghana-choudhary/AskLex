from app.state import progress_store, data_store
from app.services.text_processing import extract_text, get_chunks, get_faiss_index

def process_document(task_id: str, file_path: str):

    def callback(phase, progress):
        progress_store[task_id][phase] = progress

    text = extract_text(file_path, progress_callback=callback)
    chunks = get_chunks(text, task_id, progress_callback=callback)
    faiss_index = get_faiss_index(chunks, progress_callback=callback)

    data_store[task_id]["chunks"] = chunks
    data_store[task_id]["faiss_index"] = faiss_index

