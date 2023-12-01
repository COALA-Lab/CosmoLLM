import json
from typing import Union, List

import openai

from llm_integrations.utils import is_valid_python_code, save_py_script
from llm_integrations import settings

from . import consts


class ChatGPT:
    def __init__(self) -> None:
        self.intro_prompt = settings.OPENAI_CHAT_GPT_INTRO_PROMPT
        self.model = settings.OPENAI_CHAT_GPT_MODEL
        self.history = []
        self.events = []

        openai.api_key = settings.OPENAI_API_KEY

    def send_message(self, message: str, role: str = "user", ignore_events: bool = False) -> Union[str, List[dict]]:
        messages = []
        messages.extend([
            {"role": "system", "content": self.intro_prompt},
        ])

        if role == "user":
            self.history.append({"role": role, "content": message})
            messages.extend(self.history)
        else:
            messages.append({"role": role, "content": message})

        if not ignore_events:
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

            if len(self.history) > settings.HISTORY_LENGTH:
                self.history.pop(0)

            return response_message

    def send_system_update(self, message: str) -> Union[str, List[dict]]:
        return self.send_message(message, role="system")

    def add_system_event(self, message: str) -> None:
        self.events.append(message)

    # Code generation functions

    def _generate_code(self, message: str, system_prompt: str) -> str:
        completion = openai.ChatCompletion.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ]
        )
        return completion.choices[0].message.content

    def handle_parametrization_generation(self, message: str):
        response = self._generate_code(message, settings.PARAMETRIZATION_GENERATION_SYSTEM_PROMPT)
        if not is_valid_python_code(response):
            return 'Failed to generate code'
        save_py_script(response, 'parametrization')
        return response

    def handle_priori_generation(self, message: str):
        response = self._generate_code(message, settings.PRIORI_GENERATION_SYSTEM_PROMPT)
        if not is_valid_python_code(response):
            return 'Failed to generate code'
        save_py_script(response, 'priori')
        return response

    # OpenAI function implementations

    def _handle_openai_function(self, function_call: dict) -> None:
        name = function_call["name"]
        params = {}
        if function_call.get("arguments", None):
            try:
                params = json.loads(function_call["arguments"])
            except json.JSONDecodeError:
                raise Exception(f"Failed to parse parameters for function call! params: {function_call['arguments']}")

        if (function := getattr(self, name, None)) is not None:
            function(**params)
        else:
            raise NotImplementedError(f"Function {name} not implemented")

    def save_to_file(self, data: str, filename: str) -> None:
        with open(filename, "w") as f:
            f.write(data)
        self.add_system_event(f"Saved data to file {filename}")

    def load_from_file(self, filename: str) -> str:
        with open(filename, "r") as f:
            file_contents = f.read()
        self.add_system_event(f"Loaded file {filename} with the contents:\n{file_contents}")
        return file_contents
