from message_logs.log_message import log_message


async def post_process(bot, message, response, sent_message):
    """
    Final processing step after the assistant response is sent.

    Responsibilities:
    1. Update the in-memory chat history (user message + assistant reply).
    2. Prepare metadata required for logging.
    3. Write the interaction to the logging system.
    """

    # Retrieve the existing chat history cache
    chat_history = response.get("history")

    # ---- Update chat history ----
    # Add the processed user message that generated this response
    user_message = response.get("user")
    chat_history.append(user_message)

    # Add the assistant response to the chat history
    bot_message = {
        "role": "assistant",
        "content": response.get("message").content
    }
    chat_history.append(bot_message)

    # ---- Prepare logging data ----
    # Minimal representation of the original Discord user message
    user_message_log = {
        "id": message.id,
        "content": message.clean_content,
        "name": message.author.name
    }

    # Extract optional internal reasoning if present
    msg = response.get("message")
    thinking = getattr(msg, "thinking", "No Thinking")

    # append values to response
    response["thinking"] = thinking

    # ---- Persist interaction to log ----
    await log_message(
        response,
        sent_message,
        user_message_log,
        chat_history,
    )

