import io
import json
from contextlib import redirect_stdout

import openai
from langchain.llms.openai import OpenAI

from llm_integrations.utils import is_valid_python_code, compile_python_code
from llm_integrations import settings
from executable_scripts.plot_graphs import execute as plot


class AgentBase:
    def __init__(self) -> None:
        self.intro_prompt = settings.OPENAI_CHAT_GPT_INTRO_PROMPT
        self.events_prompt = settings.OPENAI_CHAT_GPT_EVENTS_PROMPT
        self.model = settings.OPENAI_CHAT_GPT_MODEL
        self.history = []
        self.events = []
        self.last_human_message = None
        self.last_assistant_message = None

        openai.api_key = settings.OPENAI_API_KEY

    def reset(self) -> None:
        self.history = []
        self.events = []

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
        return response

    def handle_priori_generation(self, message: str) -> str:
        response = self._generate_code(message, settings.PRIORI_GENERATION_SYSTEM_PROMPT)
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
        self.add_system_event(self.handle_priori_generation(self.last_human_message))

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

    def plot_graphs(self, experiment_path: str) -> None:
        try:
            plot(experiment_path)
            self.add_system_event(f"Plotted from {experiment_path}")
        except FileNotFoundError:
            self.add_system_event(f"Failed to load results in {experiment_path} due to file not found error")
        except PermissionError:
            self.add_system_event(f"Failed to load results in {experiment_path} due to permission error")
        except Exception as e:
            self.add_system_event(f"Failed to load results in {experiment_path} with exception {e}")

    # Utils

    def trim_history(self) -> None:
        while self._get_history_length() > settings.MAX_HISTORY_LENGTH:
            self.history.pop(0)

    def _get_history_length(self) -> int:
        return sum([len(message["content"]) for message in self.history])
