from typing import Union, List

import openai

from . import consts
from .agent_base import AgentBase


class RepeatableChatGPT(AgentBase):
    def __init__(self) -> None:
        super().__init__()

    def generate_answer(self, message: str) -> Union[str, List[dict]]:
        self.last_human_message = message
        self.history.append({"role": "user", "content": message})
        messages = [{"role": "system", "content": self.intro_prompt}]
        messages.extend(self.history)

        self.trim_history()
        completion = openai.ChatCompletion.create(
            model=self.model,
            messages=messages,
            tools=[{"type": "function", "function": function} for function in consts.OPENAI_FUNCTIONS],
            tool_choice="auto",
        )

        response = completion.choices[0].message
        if not response:
            raise Exception("Empty response from OpenAI!")

        if response.get("tool_calls", None):
            functions = [tool_call["function"] for tool_call in response["tool_calls"]]
            for function in functions:
                self._handle_openai_function(function)
            return self.generate_events_answer()

        else:
            response_message = response.content
            if not response_message:
                raise Exception("Empty response from OpenAI!")

            self.last_assistant_message = response_message
            return response_message

    def generate_events_answer(self, ignore_events: bool = False) -> Union[str, List[dict]]:
        messages = [{"role": "system", "content": self.intro_prompt},
                    {"role": "user", "content": self.last_human_message},
                    {"role": "system", "content": self.events_prompt}]
        if not ignore_events and len(self.events) > 0:
            messages.extend([
                {"role": "system", "content": f"A system event occurred: {event}"}
                for event in self.events
            ])

        completion = openai.ChatCompletion.create(
            model=self.model,
            messages=messages,
        )

        response = completion.choices[0].message
        if not response:
            raise Exception("Empty response from OpenAI!")

        response_message = response.content
        if not response_message:
            raise Exception("Empty response from OpenAI!")

        self.last_assistant_message = response_message
        return response_message

    def add_system_event(self, message: str) -> None:
        self.events.append(message)

    def confirm_answer(self):
        self.history.append({"role": "assistant", "content": self.last_assistant_message})
        self.events = []

    def regenerate_answer(self):
        self.events = []
        self.history.pop()  # human
        return self.generate_answer(self.last_human_message)