import os
import pdfplumber

def extract_text_from_pdf(pdf_path):
    """Extracts raw text from a PDF file."""
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text.strip()

def extract_text_from_all_pdfs(folder_path, output_folder):
    """Extracts text from all PDF files in the specified folder and saves them as text files."""
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(folder_path, filename)
            text = extract_text_from_pdf(pdf_path)
            output_file_path = os.path.join(output_folder, f"{os.path.splitext(filename)[0]}.txt")
            with open(output_file_path, "w", encoding="utf-8") as output_file:
                output_file.write(text)

# Example usage
folder_path = "D:/Data_Aces/Codes/ai_legal_assistant/data/legal_knowledge"  # Replace with your actual folder path
output_folder = "D:/Data_Aces/Codes/ai_legal_assistant/testing_codes/extracted_texts"  # Replace with your desired output folder path
extract_text_from_all_pdfs(folder_path, output_folder)
print(f"Extracted texts have been saved to {output_folder}")