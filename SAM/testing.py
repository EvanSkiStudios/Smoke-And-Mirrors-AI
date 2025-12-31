import ollama

emoji_model = 'llama3.2'

OLD_dictation_rules = f"""
System rules (highest priority):

You must output exactly ONE of the following:
- A single Unicode emoji
- The exact string: No reaction

Decision rule:
- If the user message implies a strong emotional reaction (shock, anger, joy, fear, sadness, disgust), output ONE relevant emoji.
- Otherwise, output: No reaction

Hard constraints:
- Do not output text, explanations, or punctuation.
- Do not include whitespace or formatting.
- Any output not matching these rules is invalid.
"""

dictation_rules = f"""
System rules (highest priority):

The user will provide you with a message. Extract and return the emojis in the message.
If the message has no emojis, respond with "No Reaction"
"""


class EmojiReactor:
    def __init__(self):
        self.model = emoji_model
        self.system_prompt = dictation_rules
        self.options = {
            'temperature': 0.5,
            'think': False
        }

    def generate(self, prompt: str) -> str:
        response = ollama.generate(
            model=self.model,
            system=self.system_prompt,
            prompt=prompt,
            options=self.options,
            stream=False
        )
        return response["response"]


if __name__ == "__main__":
    emoji_reactor = EmojiReactor()

    while True:
        prompt = input("> ")
        response = emoji_reactor.generate(prompt)
        print(response)
