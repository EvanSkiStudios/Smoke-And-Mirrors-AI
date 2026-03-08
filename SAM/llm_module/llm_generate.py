import asyncio

from llm_module.llm_create import model_name
from ollama import chat


async def run_model(messages, file_context=None):

    temperature = 1 if file_context else 0.5

    response = await asyncio.to_thread(
        chat,
        model=model_name,
        messages=messages,
        options={
            "num_ctx": 16384,
            "temperature": temperature,
            "think": True
        },
        stream=False
    )

    return response.message
