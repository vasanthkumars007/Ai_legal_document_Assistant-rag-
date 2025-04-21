import re

def smart_chunk(text, max_words=250, overlap=50):
    # 1. Try splitting by structure if available
    section_pattern = re.compile(r"^(CHAPTER\s+[IVXLCDM]+|SECTION\s+\d+|[0-9]+\.)", re.IGNORECASE)
    lines = text.split("\n")
    
    chunks = []
    current_chunk = []
    
    for line in lines:
        line = line.strip()
        if section_pattern.match(line) and current_chunk:
            chunks.append(" ".join(current_chunk))
            current_chunk = [line]
        else:
            current_chunk.append(line)

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    # 2. If chunks are too long, break them further into word chunks
    final_chunks = []
    for chunk in chunks:
        words = chunk.split()
        if len(words) <= max_words:
            final_chunks.append(chunk)
        else:
            # Sliding window over the chunk
            for i in range(0, len(words), max_words - overlap):
                window = words[i:i + max_words]
                final_chunks.append(" ".join(window))

    return final_chunks

if __name__ == "main":
    text = open("my_legal_document.txt", "r").read()
chunks = smart_chunk(text)

for i, chunk in enumerate(chunks):
    print(f"--- Chunk {i+1} ---")
    print(chunk[:300] + "...")
