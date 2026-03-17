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
        remaining_line = line
        while remaining_line:
            remaining_space = limit - len(current_chunk)
            if remaining_space <= 0:
                if in_code_block:
                    current_chunk += "```\n"
                chunks.append(current_chunk)
                current_chunk = ""
                if in_code_block:
                    current_chunk += f"```{code_lang}\n"
                remaining_space = limit - len(current_chunk)

            # If line fits, just add it
            if len(remaining_line) <= remaining_space:
                current_chunk += remaining_line
                remaining_line = ""
            else:
                # Try to split at the last space within remaining_space
                split_pos = remaining_line.rfind(" ", 0, remaining_space)
                if split_pos == -1:
                    # No space found, force split at limit
                    split_pos = remaining_space
                chunk_piece = remaining_line[:split_pos]
                current_chunk += chunk_piece
                # Remove leading space from next chunk
                remaining_line = remaining_line[split_pos:]
                if remaining_line.startswith(" "):
                    remaining_line = remaining_line[1:]
                if in_code_block:
                    current_chunk += "```\n"
                chunks.append(current_chunk)
                current_chunk = ""
                if in_code_block:
                    current_chunk += f"```{code_lang}\n"

        # Detect code block toggles
        stripped = line.strip()
        if stripped.startswith("```"):
            if not in_code_block:
                code_lang = stripped[3:].strip()
            in_code_block = not in_code_block

    if current_chunk:
        if in_code_block:
            current_chunk += "```\n"
        chunks.append(current_chunk)

    return chunks

