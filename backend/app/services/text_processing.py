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

def extract_text(file_path):
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        text= _extract_pdf_text(file_path)
    elif ext == ".docx":
        text= _extract_docx_text(file_path)
    elif ext == ".doc":
        text= _extract_doc_text(file_path)
    elif ext == ".txt":
        text= _extract_txt_text(file_path)
    elif ext == ".md":
        text= _extract_md_text(file_path)
    elif ext == ".odt":
        text= _extract_odt_text(file_path)
    elif ext == ".rtf":
        text= _extract_rtf_text(file_path)
    elif ext == ".html":
        text= _extract_html_text(file_path)
    elif ext == ".epub":
        text= _extract_epub_text(file_path)
    else:
        raise ValueError(f"Unsupported file extension: {ext}")
    
    full_text = "\n\n".join([
    f"Page {page['page_number']}:\n{page['text']}"
    for page in text
])
    return full_text

def get_chunks(full_text):
    ordered_chunks= recursive_chunk_creation(full_text)
    chunks_with_summary= generate_chunk_descriptions_batched(ordered_chunks)
    embedded_summary_chunks= generate_embeddings(chunks_with_summary)
    stitched_chunks= chunks_stitching(embedded_summary_chunks)

    return stitched_chunks

def get_faiss_index(stitched_chunks):
    faiss_index = build_faiss_index(stitched_chunks)

    return faiss_index




