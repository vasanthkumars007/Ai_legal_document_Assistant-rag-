import re

def chunk_by_section(text):
    lines = text.split("\n")
    chunks = []
    current_chunk = []

    section_pattern = re.compile(r"^(CHAPTER\s+[IVXLCDM]+|[0-9]+\.)")

    for line in lines:
        line = line.strip()
        if section_pattern.match(line) and current_chunk:
            # Start of new section, save current one
            chunks.append("\n".join(current_chunk).strip())
            current_chunk = [line]
        else:
            current_chunk.append(line)

    if current_chunk:
        chunks.append("\n".join(current_chunk).strip())

    return chunks


if __name__ == "__main__":

    chunk_by_section(text)
    