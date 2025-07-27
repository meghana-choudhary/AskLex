import os
from app.utils.text_extraction import (
    _extract_pdf_text,
    _extract_docx_text,
    _extract_txt_text,
    _extract_md_text,
    _extract_odt_text,
    _extract_rtf_text,
    _extract_html_text,
    _extract_epub_text,
    _extract_doc_text,
)
from app.utils.chunks_creation import (
    recursive_chunk_creation,
    generate_chunk_descriptions_batched,
    generate_embeddings,
    chunks_stitching
)

from app.utils.embedding_generation import (
    build_faiss_index
)


def extract_text(file_path, progress_callback=None):
    ext = os.path.splitext(file_path)[1].lower()

    extractors = {
        ".pdf": _extract_pdf_text,
        ".docx": _extract_docx_text,
        ".doc": _extract_doc_text,
        ".txt": _extract_txt_text,
        ".md": _extract_md_text,
        ".odt": _extract_odt_text,
        ".rtf": _extract_rtf_text,
        ".html": _extract_html_text,
        ".epub": _extract_epub_text,
    }

    if ext not in extractors:
        raise ValueError(f"Unsupported file extension: {ext}")

    text = extractors[ext](file_path, progress_callback)  

    full_text = "\n\n".join([
        f"Page {page['page_number']}:\n{page['text']}"
        for page in text
    ])

    if progress_callback:
        progress_callback("text_extraction", 100)  

    return full_text



def get_chunks(full_text, task_id: str = None, progress_callback=None):
    total_steps = 4 
    current_step = 0

    # Step 1: Chunking
    ordered_chunks = recursive_chunk_creation(full_text)
    current_step += 1
    if progress_callback:
        progress_callback("chunk_creation", int((current_step / total_steps) * 100))

    # Step 2: Summarization
    chunks_with_summary = generate_chunk_descriptions_batched(ordered_chunks)
    current_step += 1
    if progress_callback:
        progress_callback("chunk_creation", int((current_step / total_steps) * 100))

    # Step 3: Embedding summaries
    embedded_summary_chunks = generate_embeddings(chunks_with_summary)
    current_step += 1
    if progress_callback:
        progress_callback("chunk_creation", int((current_step / total_steps) * 100))

    # Step 4: Stitching
    stitched_chunks = chunks_stitching(embedded_summary_chunks)
    current_step += 1
    if progress_callback:
        progress_callback("chunk_creation", int((current_step / total_steps) * 100))

    return stitched_chunks


def get_faiss_index(stitched_chunks, progress_callback=None):
    return build_faiss_index(stitched_chunks, progress_callback=progress_callback)







