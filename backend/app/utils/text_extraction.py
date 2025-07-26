import fitz  # PyMuPDF
import docx
import pypandoc
import os


def _extract_pdf_text(file_path, progress_callback=None):
    doc = fitz.open(file_path)
    total_pages = len(doc)
    all_text = []

    for i, page in enumerate(doc):
        text = page.get_text()
        all_text.append({
            "page_number": i + 1,
            "text": text.strip()
        })

        if progress_callback:
            percent = int(((i + 1) / total_pages) * 100)
            progress_callback("text_extraction", percent)

    return all_text

def _extract_docx_text(file_path, progress_callback=None):
    doc = docx.Document(file_path)
    paragraphs = doc.paragraphs
    total = len(paragraphs)
    text_lines = []

    for i, para in enumerate(paragraphs):
        text_lines.append(para.text)
        if progress_callback and total > 0:
            percent = int(((i + 1) / total) * 100)
            progress_callback("text_extraction", percent)

    full_text = "\n".join(text_lines)
    return [{"page_number": 1, "text": full_text.strip()}]


def _extract_txt_text(file_path, progress_callback=None):
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()

    total = len(lines)
    text_lines = []

    for i, line in enumerate(lines):
        text_lines.append(line.strip())
        if progress_callback and total > 0:
            percent = int(((i + 1) / total) * 100)
            progress_callback("text_extraction", percent)

    return [{"page_number": 1, "text": "\n".join(text_lines)}]


def _extract_md_text(file_path, progress_callback=None):
    return _extract_txt_text(file_path, progress_callback)  # Similar handling


def _extract_odt_text(file_path, progress_callback=None):
    output = pypandoc.convert_file(file_path, "plain")
    lines = output.splitlines()
    total = len(lines)
    collected = []

    for i, line in enumerate(lines):
        collected.append(line)
        if progress_callback and total > 0:
            percent = int(((i + 1) / total) * 100)
            progress_callback("text_extraction", percent)

    return [{"page_number": 1, "text": "\n".join(collected)}]


def _extract_rtf_text(file_path, progress_callback=None):
    return _extract_odt_text(file_path, progress_callback)  # Same logic


def _extract_html_text(file_path, progress_callback=None):
    return _extract_odt_text(file_path, progress_callback)  # Same logic


def _extract_epub_text(file_path, progress_callback=None):
    return _extract_odt_text(file_path, progress_callback)  # Same logic


def _extract_doc_text(file_path, progress_callback=None):
    return _extract_odt_text(file_path, progress_callback)  # Same logic


if __name__ == "__main__":
    file_path="file_path"

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
    
    print(text)