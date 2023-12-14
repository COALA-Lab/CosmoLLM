from typing import Union, List
import openai
from . import consts
from .agent_base import AgentBase


class ChatGPT(AgentBase):
    def __init__(self) -> None:
        super().__init__()

    def send_message(self, message: str, role: str = "user", ignore_events: bool = False) -> Union[str, List[dict]]:
        messages = []
        messages.extend([
            {"role": "system", "content": self.intro_prompt},
        ])

        if role == "user":
            self.last_message = message
            self.history.append({"role": role, "content": message})
            messages.extend(self.history)
            self.trim_history()
        else:
            messages.append({"role": role, "content": message})

        if not ignore_events and len(self.events) > 0:
            messages.extend([
                {"role": "system", "content": f"A system event occurred: {event}"}
                for event in self.events
            ])
            self.events = []

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
            return functions
        else:
            response_message = response.content

            if not response_message:
                raise Exception("Empty response from OpenAI!")

            self.history.append({"role": "assistant", "content": response_message})

            return response_message

    def send_system_update(self, message: str) -> Union[str, List[dict]]:
        return self.send_message(message, role="system")

    def add_system_event(self, message: str) -> None:
        self.events.append(message)