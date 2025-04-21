"""import re

def chunk_by_act_sections(text):
    lines = text.split("\n")
    chunks = []
    current_chunk = []

    # Regex to match section headers like:
    # "1. Factory", "Minimum Wages Act 1948", etc.
    heading_pattern = re.compile(
        r"^\s*(\d+\.\s+[A-Z][a-zA-Z\s&]+|[A-Z][a-zA-Z\s&()]+Act\s+\d{4})"
    )

    for line in lines:
        line = line.strip()

        # If we find a new section heading
        if heading_pattern.match(line):
            if current_chunk:
                chunks.append(" ".join(current_chunk).strip())
                current_chunk = []
            current_chunk.append(line)
        else:
            current_chunk.append(line)

    if current_chunk:
        chunks.append(" ".join(current_chunk).strip())

    return chunks


# Example usage:
if __name__ == "__main__":
    #with open("Labour_Employment_Laws_India.txt", "r", encoding="utf-8") as f:
        #text = f.read()
    chunks = chunk_by_act_sections()
    for i, chunk in enumerate(chunks):
        print(f"--- Chunk {i+1} ---")
        print(chunk[:300] + "\n")"""

