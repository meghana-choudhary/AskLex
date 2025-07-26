import fitz  # PyMuPDF
import docx
import pypandoc
import os


def _extract_pdf_text(file_path):
    doc = fitz.open(file_path)
    all_text = []

    for page_number in range(len(doc)):
        page = doc[page_number]
        text = page.get_text()
        all_text.append({
            "page_number": page_number + 1,
            "text": text.strip()
        })

    return all_text


def _extract_docx_text(file_path):
    doc = docx.Document(file_path)
    full_text = "\n".join([para.text for para in doc.paragraphs])
    return [{"page_number": 1, "text": full_text.strip()}]


def _extract_txt_text(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        text = file.read()
    return [{"page_number": 1, "text": text.strip()}]


def _extract_md_text(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        text = file.read()
    return [{"page_number": 1, "text": text.strip()}]


def _extract_odt_text(file_path):
    output = pypandoc.convert_file(file_path, "plain")
    return [{"page_number": 1, "text": output.strip()}]


def _extract_rtf_text(file_path):
    output = pypandoc.convert_file(file_path, "plain")
    return [{"page_number": 1, "text": output.strip()}]


def _extract_html_text(file_path):
    output = pypandoc.convert_file(file_path, "plain")
    return [{"page_number": 1, "text": output.strip()}]


def _extract_epub_text(file_path):
    output = pypandoc.convert_file(file_path, "plain")
    return [{"page_number": 1, "text": output.strip()}]


def _extract_doc_text(file_path):
    output = pypandoc.convert_file(file_path, "plain")
    return [{"page_number": 1, "text": output.strip()}]

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