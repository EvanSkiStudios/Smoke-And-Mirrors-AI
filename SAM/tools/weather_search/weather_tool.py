import asyncio
import json
import re

from ollama import ChatResponse, chat

import sam_config
from tools.weather_search.weather_api import get_weather
from utility_scripts.utility import split_response
from utility_scripts.system_logging import setup_logger

# configure logging
logger = setup_logger(__name__)

tool_model = 'huihui_ai/llama3.2-abliterate'
chat_model = 'SAM-deepseek-r1'


def get_the_weather(state: str, city: str = None) -> dict:
    """
    Returns a dict of information from the given city and/or state
    """
    return get_weather(state, city)


available_functions = {
    'get_the_weather': get_the_weather,
}

# Updated system prompt
system_prompt = f"""
{sam_config.SAM_personality}

All weather information from tool calls is provided between __TOOL_DATA__ and __END_TOOL_DATA__. 
Rules:
1. Only use the information inside __TOOL_DATA__ and __END_TOOL_DATA__.
2. Do not invent, guess, or assume any facts that are not explicitly included.
3. You may write in natural, conversational language, but every statement must come from the input.
4. Do not add extra locations, times, temperatures, weather conditions, or wind details not present.
5. Include all facts provided; do not omit anything.

Example input:
__TOOL_DATA__
{{
  "location": "Columbus, Ohio",
  "summary": "Tonight: 40 F, Mostly Cloudy",
  "details": "Mostly cloudy, with a low around 40. Southwest wind 6 to 13 mph, with gusts as high as 24 mph."
}}
__END_TOOL_DATA__

Example output:
In Columbus, Ohio, tonight it will be mostly cloudy with a low around 40°F. Southwest winds will range from 6 to 13 mph, with gusts up to 24 mph.
"""


async def weather_search(message):
    messages = [
        {'role': 'user', 'content': message}
    ]
    response: ChatResponse = await asyncio.to_thread(
        chat,
        model=tool_model,
        messages=messages,
        tools=[get_the_weather],
        options={'temperature': 0.2},  # deterministic
        stream=False
    )

    tool_output = None
    if response.message.tool_calls:
        for tool in response.message.tool_calls:
            if function_to_call := available_functions.get(tool.function.name):
                logger.info(f'Calling function: {tool.function.name}\nArguments: {tool.function.arguments}')
                tool_output = function_to_call(**tool.function.arguments)
                logger.info(f'Function output: {tool_output}')
            else:
                logger.error(f'Function {tool.function.name} not found')

    if tool_output:
        # Wrap JSON in special markers for the model
        tool_message_content = f"__TOOL_DATA__\n{json.dumps(tool_output)}\n__END_TOOL_DATA__"
        messages.append({'role': 'tool', 'content': tool_message_content, 'tool_name': tool.function.name})
    else:
        logger.info("No tool output available to pass to the model.")

    # Final model call with system prompt
    final_response: ChatResponse = chat(
        model=chat_model,
        messages=[{'role': 'system', 'content': system_prompt}] + messages,
        stream=False,
        options={
            'num_ctx': 16384,
            'temperature': 0.2,  # low for deterministic output
            'think': True
        }
    )

    output = final_response.message.content
    output = re.sub(r'\bEvanski_\b', 'Evanski', output, flags=re.IGNORECASE)

    logger.info(response)
    logger.info(final_response)
    logger.info(f"""
    ===================================
    CONTENT:  {message}\n
    RESPONSE:  {output}
    ===================================
    """)

    cleaned = output.replace("'", "\\'")
    return {
        "content": split_response(cleaned),
        "message": final_response,
        "prompt": system_prompt
    }


# ===============
# TESTING
# ===============
async def main():
    query = "whats the weather_search in Hell Gate, Georgia?"
    response = await weather_search(query)
    print(response)


if __name__ == "__main__":
    asyncio.run(main())
