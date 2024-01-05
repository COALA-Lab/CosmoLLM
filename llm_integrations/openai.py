from typing import List, Optional

import openai

from agents.cosmo_state_machine import State
from . import settings


class ChatGPT:
    def __init__(
            self,
            model: Optional[str] = None,
            api_key: Optional[str] = None,
    ) -> None:
        self.model = model or settings.OPENAI_CHAT_GPT_MODEL
        openai.api_key = api_key or settings.OPENAI_API_KEY

    def complete(self, messages: List[dict], state: State) -> dict:
        message = openai.ChatCompletion.create(
            model=self.model,
            messages=messages,
            tools=[{"type": "function", "function": function} for function in state.get_openai_functions()],
            tool_choice="auto",
        ).choices[0].message

        if not message:
            raise Exception("OpenAI returned an empty message.")

        return message
