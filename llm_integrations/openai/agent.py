import io
import json
from contextlib import redirect_stdout
from typing import Union, List

import openai

from llm_integrations.utils import is_valid_python_code, save_py_script, compile_python_code
from llm_integrations import settings
from executable_scripts.run_experiment import plot

from . import consts


class ChatGPT:
    def __init__(self) -> None:
        self.intro_prompt = settings.OPENAI_CHAT_GPT_INTRO_PROMPT
        self.model = settings.OPENAI_CHAT_GPT_MODEL
        self.history = []
        self.events = []
        self.last_message = None

        openai.api_key = settings.OPENAI_API_KEY

    def reset(self) -> None:
        self.history = []
        self.events = []

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
            [print("Event: " + event) for event in self.events]
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

    def handle_parametrization_generation(self, message: str) -> str:
        response = self._generate_code(message, settings.PARAMETRIZATION_GENERATION_SYSTEM_PROMPT)
        # if not is_valid_python_code(response):
        #     return 'Failed to generate code'
        # save_py_script(response, 'parametrization')
        return response

    def handle_priori_generation(self, message: str) -> str:
        response = self._generate_code(message, settings.PRIORI_GENERATION_SYSTEM_PROMPT)
        # if not is_valid_python_code(response):
        #     return 'Failed to generate code'
        # save_py_script(response, 'priori')
        return response

    # OpenAI function implementations

    def _handle_openai_function(self, function_call: dict) -> None:
        name = function_call["name"]

        if name == "python":
            code = function_call["arguments"]
            if not is_valid_python_code(code):
                self.add_system_event(f"Invalid python code:\n{code}")
                return

            try:
                output = io.StringIO()
                with redirect_stdout(output):
                    exec(compile_python_code(code))

                self.add_system_event(f"Executed python code:\n{code}\nOutput:\n{output.getvalue()}")
            except Exception as e:
                self.add_system_event(f"Failed to execute python code:\n{code}\nException:\n{e}")
                return
        else:
            params = {}
            if function_call.get("arguments", None):
                try:
                    params = json.loads(function_call["arguments"])
                except json.JSONDecodeError:
                    self.add_system_event(
                        f"Failed to parse parameters for function call {name}"
                        f"with arguments {function_call['arguments']}"
                    )
                    return

            if (function := getattr(self, name, None)) is not None:
                function(**params)
            else:
                self.add_system_event(f"Unknown function call {name}")
                return

    def generate_parametrization(self, parametrization_function_in_latex: str) -> None:
        self.add_system_event(self.handle_parametrization_generation(parametrization_function_in_latex))

    def generate_priori(self) -> None:
        self.add_system_event(self.handle_priori_generation(self.last_message))

    def save_to_file(self, data: str, filename: str) -> None:
        try:
            with open(filename, "w") as f:
                f.write(data)
            self.add_system_event(f"Saved data to file {filename}")
        except PermissionError:
            self.add_system_event(f"Failed to save data to file {filename} due to permission error")
        except Exception as e:
            self.add_system_event(f"Failed to save data to file {filename} with exception {e}")

    def load_from_file(self, filename: str, characters: int = -1) -> None:
        try:
            with open(filename, "r") as f:
                file_contents = f.read(characters)
            self.add_system_event(f"Loaded file {filename} with the contents:\n{file_contents}")
        except FileNotFoundError:
            self.add_system_event(f"Failed to load file {filename} due to file not found error")
        except PermissionError:
            self.add_system_event(f"Failed to load file {filename} due to permission error")
        except Exception as e:
            self.add_system_event(f"Failed to load file {filename} with exception {e}")

    def plot_graphs(self, filename: str) -> None:
        try:
            print("Plotting results...")
            plot(filename)
            print("Done!")
            self.add_system_event(f"Plotted from {filename}")
        except FileNotFoundError:
            self.add_system_event(f"Failed to load file {filename} due to file not found error")
        except PermissionError:
            self.add_system_event(f"Failed to load file {filename} due to permission error")
        except Exception as e:
            self.add_system_event(f"Failed to load file {filename} with exception {e}")

    # Utils

    def trim_history(self) -> None:
        while self._get_history_length() > settings.MAX_HISTORY_LENGTH:
            self.history.pop(0)

    def _get_history_length(self) -> int:
        return sum([len(message["content"]) for message in self.history])
