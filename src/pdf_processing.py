import os
import pdfplumber

def extract_text_from_pdf(pdf_path):
    """Extracts raw text from a PDF file."""
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text.strip()

def extract_text_from_all_pdfs(folder_path):
    """Extracts text from all PDF files in the specified folder."""
    all_texts = {}
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(folder_path, filename)
            text = extract_text_from_pdf(pdf_path)
            all_texts[filename] = text
    return all_texts
 
if __name__ == "__main__":
    extract_text_from_all_pdfs()
    