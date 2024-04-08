from typing import List, Optional

import openai

from . import settings


class ChatGPT:
    def __init__(
            self,
            model: Optional[str] = None,
            functions: Optional[List[dict]] = None,
            api_key: Optional[str] = None,
    ) -> None:
        self.model = model or settings.OPENAI_CHAT_GPT_MODEL
        self.functions = functions or []
        api_key = api_key or settings.OPENAI_API_KEY

        if not openai.api_key:
            raise ValueError("OpenAI API key not found! Please set it in the environment.")

        openai.api_key = api_key

    def complete(self, messages: List[dict]) -> dict:
        message = openai.ChatCompletion.create(
            model=self.model,
            messages=messages,
            tools=[{"type": "function", "function": function} for function in self.functions],
            tool_choice="auto",
        ).choices[0].message

        if not message:
            raise Exception("OpenAI returned an empty message.")

        return message
