def chunk_by_word_count(text, max_words=200, overlap=50):
    words = text.split()
    chunks = []

    for i in range(0, len(words), max_words - overlap):
        chunk = words[i:i + max_words]
        if chunk:
            chunks.append(" ".join(chunk))

    return chunks
"""
       if you want to continue with sentce level chunking, you can use the following code:

       

       import re

def chunk_by_sentences(text, max_sentences=6, overlap=2):
    # Split the text into sentences using period (.) as delimiter
    sentences = re.split(r'(?<=[.?!])\s+', text.strip())
    chunks = []

    for i in range(0, len(sentences), max_sentences - overlap):
        chunk = sentences[i:i + max_sentences]
        if chunk:
            chunks.append(" ".join(chunk))

    return chunks

"""