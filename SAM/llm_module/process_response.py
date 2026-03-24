from discord_module.utilities.split_message import split_response


def process_response(response, system_prompt, message_cache):

    cleaned = response.message.content.replace("'", "\\'")

    # Extract token usage from response
    token_usage = {
        "prompt_tokens": getattr(response, "prompt_eval_count", 0),
        "tokens_generated": getattr(response, "eval_count", 0),
        "total_tokens": getattr(response, "prompt_eval_count", 0) + getattr(response, "eval_count", 0),
        "model_load_time": getattr(response, "load_duration", 0),
        "prompt_processing_time": getattr(response, "prompt_eval_duration", 0),
        "generation_time": getattr(response, "eval_duration", 0),
        "total_duration": getattr(response, "total_duration", 0)
    }

    return {
            "content": split_response(cleaned),
            "message": response.message,
            "prompt": system_prompt,
            "history": message_cache,
            "token_usage": token_usage
        }

