from pathlib import Path
from datetime import datetime

from utility_scripts.system_logging import setup_logger

# configure logging
logger = setup_logger(__name__)


def get_timestamp() -> str:
    return datetime.now().strftime("%m-%d__%H_%M_%S")


def format_details(summary: str, content: str) -> str:
    """
    Wrap text inside an HTML <details> block.

    This format is useful for Markdown log files because it allows
    collapsible sections when viewed in many editors or Git platforms.

    Args:
        summary (str): Title displayed when the section is collapsed.
        content (str): Body text contained inside the expandable section.

    Returns:
        str: HTML <details> block containing the provided content.
    """
    return (
        "<details>\n"
        f"   <summary>{summary}</summary>\n"
        f"{content}\n"
        "</details>\n"
    )


async def log_message(response: dict, sent_message, user_message: dict, full_history: dict) -> None:
    """
    Write a Markdown log file capturing a full message interaction.

    The log includes:
        - User metadata
        - User message content
        - Assistant response
        - Optional file text data
        - Token usage statistics
        - Internal reasoning ("thinking") if present
        - Complete chat history
        - The system prompt used for the request

    A unique filename is generated using a timestamp and the
    message ID of the sent response.

    Args:
        response (dict):
            Response payload returned from the model handler.
            May include keys such as:
                "prompt"       -> system prompt dictionary
                "message"      -> model message object
                "file_txt"     -> extracted file text
                "token_usage"  -> token statistics

        sent_message:
            The final message object sent by the system (must contain
            `id` and `content` attributes).

        user_message (dict):
            Dictionary describing the user message.
            Expected fields:
                "id"
                "name"
                "content"

        full_history (dict):
            Iterable containing the full conversation history where each
            item has:
                {
                    "role": str,
                    "content": str
                }

    Returns:
        None
    """

    # Ensure the log directory exists relative to this module.
    save_dir = Path(__file__).resolve().parent / "logs"
    save_dir.mkdir(exist_ok=True)

    # Construct the output log file path.
    path = save_dir / f"{get_timestamp()}__{sent_message.id}.md"

    # Flatten the full conversation history into a readable text block.
    full_chat_history = "\n".join(
        f'{m["role"]}: {m["content"]}\n' for m in full_history
    )

    # Extract the system prompt used for the model request.
    system_prompt = response.get("prompt")
    sys_prompt_string = (
        "role: " + system_prompt["role"] + "\n"
        "content:\n" + system_prompt["content"]
    )

    # Extract optional internal reasoning from the response message.
    msg = response.get("message")
    thinking = getattr(msg, "thinking", "No Thinking")

    # --------------------------------------------
    # Optional Sections
    # --------------------------------------------

    # Attachment data (e.g., extracted text from uploaded files).
    attachment_section = ""
    text_data = response.get("file_txt")
    if text_data:
        attachment_section = f"{format_details('File Text Data', text_data)}\n"

    # Token usage information returned by the model API.
    token_section = ""
    token_usage = response.get("token_usage")
    if token_usage:
        prompt_tokens = token_usage.get("prompt_tokens", 0)
        tokens_generated = token_usage.get("tokens_generated", 0)
        total_tokens = token_usage.get("total_tokens", 0)
        model_load_time = token_usage.get("model_load_time", 0)
        prompt_processing_time = token_usage.get("prompt_processing_time", 0)
        generation_time = token_usage.get("generation_time", 0)
        total_duration = token_usage.get("total_duration", 0)

        token_text = (
            f"Tokens in Prompt: {prompt_tokens}<br>"
            f"Tokens Generated: {tokens_generated}<br>"
            f"Total Tokens: {total_tokens}<br>"
            # Timing in nanoseconds to seconds
            f"Model Load Time: {model_load_time / 1e9:.2f}<br>"
            f"Prompt Process Time: {prompt_processing_time / 1e9:.2f}<br>"
            f"Generation Time: {generation_time / 1e9:.2f}<br>"
            f"Total Duration: {total_duration / 1e9:.2f}"
        )

        token_section = f"{format_details('Token Usage', token_text)}\n"

    # --------------------------------------------
    # Final Log Output
    # --------------------------------------------

    output = (
        f"User Message ID:    {user_message['id']}  "
        "\n"
        f"User:    {user_message['name']}  "
        "\n"
        f"{format_details('Message Content', user_message['content'])}"
        "\n"
        f"{attachment_section}"
        f"{token_section}"
        f"Message ID:    {sent_message.id}  "
        f"{format_details('Thinking', thinking)}"
        "\n"
        f"{format_details('Response', sent_message.content)}"
        "\n"
        f"{format_details('Full History', full_chat_history)}"
        "\n"
        f"{format_details('Full Prompt', sys_prompt_string)}"
    )

    # Write the formatted log file to disk.
    path.write_text(output, encoding="utf-8")

    # Record the logging event in the application logger.
    logger.info(f"Logged: {sent_message.id}")