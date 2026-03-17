DISCORD_CHAR_LIMIT = 2000


def split_response(text, limit=DISCORD_CHAR_LIMIT):
    if len(text) <= limit:
        return [text]

    chunks = []
    current_chunk = ""
    in_code_block = False
    code_lang = ""
    lines = text.splitlines(keepends=True)

    for line in lines:
        line_length = len(line)
        # Check if adding the line would exceed the limit
        if len(current_chunk) + line_length > limit:
            if in_code_block:
                # Close the code block at the end of the chunk
                current_chunk += "```\n"
            chunks.append(current_chunk)
            current_chunk = ""
            if in_code_block:
                # Reopen the code block for the next chunk, preserving language
                current_chunk += f"```{code_lang}\n"

        current_chunk += line

        # Detect code block toggles
        stripped = line.strip()
        if stripped.startswith("```"):
            if not in_code_block:
                # Entering a code block, capture the language
                code_lang = stripped[3:].strip()
            in_code_block = not in_code_block

    if current_chunk:
        if in_code_block:
            current_chunk += "```\n"
        chunks.append(current_chunk)

    return chunks

