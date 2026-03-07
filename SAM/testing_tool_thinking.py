import os
import asyncio
from typing import Union
from dotenv import load_dotenv

from ollama import (
    Client,
    chat,
    web_search,
    web_fetch,
    WebSearchResponse,
    WebFetchResponse,
)

from utility_scripts.system_logging import setup_logger


# --- Logger ---
logger = setup_logger(__name__)


# --- Environment ---
load_dotenv()
os.environ["OLLAMA_API_KEY"] = os.getenv("OLLAMA_API")

# --- LLM Session Class ---
class LLMChatSession:
    def __init__(self, model: str):
        self.model = model
        self.messages = []
        self.available_tools = {
            "web_search": web_search,
            "web_fetch": web_fetch,
        }
        api_key = os.getenv("OLLAMA_API_KEY")
        self.client = Client(headers={"Authorization": f"Bearer {api_key}"} if api_key else None)

    # -----------------------------
    # Tool Result Formatter
    # -----------------------------
    def format_tool_results(
        self,
        results: Union[WebSearchResponse, WebFetchResponse],
        user_search: str,
    ) -> str:
        output = []

        if isinstance(results, WebSearchResponse):
            output.append(f'Search results for "{user_search}":')
            for result in results.results:
                output.append(result.title if result.title else result.content)
                output.append(f"   URL: {result.url}")
                output.append(f"   Content: {result.content}")
                output.append("")
            return "\n".join(output).rstrip()

        elif isinstance(results, WebFetchResponse):
            output.append(f'Fetch results for "{user_search}":')
            output.extend(
                [
                    f"Title: {results.title}",
                    f"URL: {user_search}" if user_search else "",
                    f"Content: {results.content}",
                ]
            )
            if results.links:
                output.append(f"Links: {', '.join(results.links)}")
            output.append("")
            return "\n".join(output).rstrip()

        return ""

    # -----------------------------
    # Tool Handler
    # -----------------------------
    async def handle_tool_calls(self, response) -> bool:
        if not response.message.tool_calls:
            return False

        for tool_call in response.message.tool_calls:
            function_name = tool_call.function.name
            args = tool_call.function.arguments

            # Map function name to client method
            if function_name == "web_search":
                func = self.client.web_search
            elif function_name == "web_fetch":
                func = self.client.web_fetch
            else:
                self.messages.append({
                    "role": "tool",
                    "content": f"Tool {function_name} not found",
                    "tool_name": function_name,
                })
                continue

            # Run tool in thread
            result: Union[WebSearchResponse, WebFetchResponse] = await asyncio.to_thread(
                func,
                **args
            )

            user_search = args.get("query", "") or args.get("url", "")
            formatted = self.format_tool_results(result, user_search=user_search)

            self.messages.append({
                "role": "tool",
                "content": formatted[: 2000 * 4],
                "tool_name": function_name,
            })
        print("Tool Call")
        return True

    # -----------------------------
    # Main Chat Loop
    # -----------------------------
    async def chat(self, user_prompt: str) -> str:
        self.messages.append({
            "role": "user",
            "content": user_prompt,
        })

        while True:
            response = await asyncio.to_thread(
                chat,
                model=self.model,
                messages=[
                    *self.messages,
                ],
                tools=[web_search, web_fetch],
                options={
                    "num_ctx": 16384,
                    "temperature": 0.6,
                    "think": True,
                },
                stream=False,
            )

            # If no tool calls → final answer
            if not response.message.tool_calls:
                print("No Tool Call")
                self.messages.append({
                    "role": "assistant",
                    "content": response.message.content,
                })
                return response.message.content

            # Otherwise execute tools and loop again
            await self.handle_tool_calls(response)


# --- Entrypoint ---
if __name__ == "__main__":
    llm_model = "huihui_ai/lfm2.5-abliterated:1.2b-thinking"
    session = LLMChatSession(llm_model)

    while True:
        user_input = input("> ")
        response = asyncio.run(session.chat(user_input))
        logger.info(response)