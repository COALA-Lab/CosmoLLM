import io
import json
import os
from contextlib import redirect_stdout
from pathlib import Path
from typing import Union, List

from PIL import Image

from utils.util import generate_experiment_id
from . import settings
from . import consts
from .consts import ResponseType
from .cosmo_state_machine import DefineFunctionState, SelectionPriorState, ComputationState
from .utils import is_valid_python_code, compile_python_code, save_py_script
from executable_scripts.plot_graphs import execute as plot
from run_calculation import execute as run_experiment
from llm_integrations.openai import ChatGPT


class ChatAgent:
    def __init__(self, chatbot: ChatGPT = None):
        self.intro_prompt = consts.INTRO_PROMPT
        self.history = []
        self.events = []
        self.pending_images = []
        self.pending_data_tables = []
        self.context = {
            "last_message": "",
            "result_info": {},
        }
        self.prompt_explanation = []
        #self.llm = chatbot or ChatGPT(functions=consts.OPENAI_FUNCTIONS)
        self.llm = chatbot or ChatGPT()
        self.state = DefineFunctionState()
        self.param_code = str
        self.param_code1 = str
        self.param_path = str
        self.param_path1 = str
        self.latex_function = str
        self.prior = str
        self.config = str
        self.result_path = str

    def reset(self) -> None:
        self.history = []
        self.events = []
        self.pending_images = []
        self.pending_data_tables = []
        self.context = {
            "last_message": "",
            "result_info": {},
        }
        self.prompt_explanation = []

    def send_message(self, message: str) -> str:
        if not message:
            raise ValueError("Empty message!")

        response = self.llm_complete(message, save_explanation=True) #res1
        response_type = self._process_response(response)
        response_text = None
        if response_type == ResponseType.FUNCTION:
            # Notify the user about the function call
            if self.events:
                response_text = self.send_system_update(consts.SYSTEM_UPDATE_PROMPT)
                print("respose_text: ", response_text)
                self.history.append({"role": "assistant", "content": response_text})
        elif response_type == ResponseType.TEXT:
            response_text = response.content
        elif response_type == ResponseType.NONE:
            raise Exception("Empty response from OpenAI!")

        if not response_text:
            raise Exception("Empty response from OpenAI!")
        return response_text

    def llm_complete(
            self, message: str, role: str = "user", ignore_events: bool = False, save_explanation: bool = False
    ) -> dict:
        if not message:
            raise ValueError("Empty message!")

        messages = self._prepare_messages_and_events(message, role, ignore_events)
        if save_explanation:
            self.prompt_explanation = messages
        #response = self.llm.complete(messages)
        response = self.llm.complete(messages, self.state)
        print("res1 ", response)
        if not response:
            raise Exception("Empty response from OpenAI!")

        return response

    def _prepare_messages_and_events(self, message: str, role: str = "user", ignore_events: bool = False) -> List[dict]:
        messages = []
        messages.extend([
            {"role": "system", "content": self.intro_prompt.format(**self.context)},
            #{"role": "system", "content": self.state.get_state_system_prompt().format(**self.context)},
        ])
        messages.extend([
            #{"role": "system", "content": self.intro_prompt.format(**self.context)},
            {"role": "system", "content": self.state.get_state_system_prompt().format(**self.context)},
        ])

        if role == "user":
            self.context["last_message"] = message
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

        return messages

    def _process_response(self, response: dict) -> ResponseType:
        # Function call
        if response.get("tool_calls", None):
            functions = [tool_call["function"] for tool_call in response["tool_calls"]]
            for function in functions:
                self._handle_openai_function(function)
            return ResponseType.FUNCTION
        # Text response
        else:
            response_message = response.content

            if not response_message:
                return ResponseType.NONE

            self.history.append({"role": "assistant", "content": response_message})

            return ResponseType.TEXT

    def send_system_update(self, message: str) -> Union[str, List[dict]]:
        if not self.events:
            raise ValueError("No pending events in the system!")
        response = self.llm_complete(message, role="system")
        print("response1: ", response)
        print("response.get(tool_calls, None) ", response.get("tool_calls", None))
        if response and response.get("tool_calls", None):
            raise Exception(
                "System update prompt should not result in a function call! (function chaining not yet supported)"
            )

        response = response.content
        if not response:
            raise Exception("Empty response from OpenAI!")
        return response

    def add_system_event(self, message: str) -> None:
        if not message:
            raise ValueError("Empty message!")

        self.events.append(message)

    # Code generation functions
    def _generate_code(self, message: str, system_prompt: str, module: str) -> str:
        if not message:
            raise ValueError("Empty message!")
        if not system_prompt:
            raise ValueError("Empty system prompt!")
        print("mess: ", message)
        response = self.llm.complete(
            [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            self.state
        )
        print("res: ", response)
        if response.get("tool_calls", None):
            functions = [tool_call["function"] for tool_call in response["tool_calls"]]
            for function in functions:
                if function["name"] == "python":
                    code = function["arguments"]
                    if not is_valid_python_code(code):
                        self.add_system_event(f"Invalid python code:\n{code}")
                        return
                    self.param_path = save_py_script(code, module)
                    return code


    def handle_parametrization_generation(self, message: str) -> str:
        response = self._generate_code(message, settings.PARAMETRIZATION_GENERATION_SYSTEM_PROMPT, "parametrization")
        self.param_code = response
        print("ooo ", response)
        self.latex_function = message
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
                print("AAA")
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
            print(params, name)
            if (function := getattr(self, name, None)) is not None:
                function(**params)
            else:
                self.add_system_event(f"Unknown function call {name}")
                return

    def generate_parametrization(self, parametrization_function_in_latex: str) -> None:
        #self.state = DefineFunctionState()
        code = self.handle_parametrization_generation(parametrization_function_in_latex)
        self.add_system_event(f"Generated parametrization code {code} in path {self.param_path}")

    def prior_selection(self) -> None:
        self.state = SelectionPriorState()
        self.context["result_info"] = {
            "directory": "priori"
        }
        self.add_system_event(f"{self.state.get_state_system_prompt().format(**self.context)}")

    def prior_selected(self, prior_file):
        self.prior = prior_file
        self.add_system_event(f"Prior is selected, it is: {prior_file}!")

    def config_selected(self, config_filename):
        self.config = config_filename
        self.add_system_event(f"Config is selected, it is: {config_filename}")

    def result_path_selected(self, result_path):
        self.result_path = result_path
        self.add_system_event(f"Result path is selected, it is: {result_path}")
        self.run_experiment(config_path=self.config, results_path=self.result_path)

    def start_calculation(self):
        self.state = ComputationState()
        self.add_system_event(f"{self.state.get_state_system_prompt().format(**self.context)}")

    # def start_calculation(self):
    #     self.state = DefineConfig()
    #     response1 = self.llm.complete(
    #         [
    #             {"role": "system", "content": consts.ELEMENTS_PARAMETRIZATION.format(parametrization_class=self.param_code)},
    #         ],
    #         self.state
    #     )
    #     print("response1", response1.content)
    #
    #     characters: int = -1
    #     try:
    #         with open(self.prior, "r") as f:
    #             file_contents = f.read(characters)
    #             response2 = self.llm.complete(
    #                 [
    #                     {"role": "system", "content": consts.ELEMENTS_PRIOR.format(prior_filename=self.prior, prior_content=file_contents)},
    #                 ],
    #                 self.state
    #             )
    #             print("response2 ", response2.content)
    #     except Exception as e:
    #         raise ValueError("Failed to load!")



    def generate_priori(self) -> None:
        self.add_system_event(self.handle_priori_generation(self.context["last_message"]))

    def save_to_file(self, data: str, filename: str) -> None:
        try:
            if not data:
                raise ValueError("Empty data!")

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

    def display_image(self, image_path: str) -> None:
        try:
            Image.open(image_path)

            self.pending_images.append(image_path)
            self.add_system_event(f"Displayed image from {image_path}")
        except FileNotFoundError:
            self.add_system_event(f"Failed to display image from {image_path} due to file not found error")
        except PermissionError:
            self.add_system_event(f"Failed to display image from {image_path} due to permission error")
        except Exception as e:
            self.add_system_event(f"Failed to display image from {image_path} with exception {e}")

    def display_data_table(self, data_table_path: str) -> None:
        try:
            if not os.access(data_table_path, os.R_OK):
                raise PermissionError

            self.pending_data_tables.append(data_table_path)
            self.add_system_event(f"Displayed data table from {data_table_path}")
        except FileNotFoundError:
            self.add_system_event(f"Failed to display data table from {data_table_path} due to file not found error")
        except PermissionError:
            self.add_system_event(f"Failed to display data table from {data_table_path} due to permission error")
        except Exception as e:
            self.add_system_event(f"Failed to display data table from {data_table_path} with exception {e}")

    def handle_parameters_modification(self, message: str) -> str:
        function = self.latex_function
        code = self.param_code
        response = self.llm.complete(
            [
                {"role": "system", "content": consts.PARAMETERS_MODIFICATION_SYSTEM_PROMPT.format(code=code)},
                {"role": "user", "content": message}
            ],
            self.state
        )
        print("eee ", response)
        if response.get("tool_calls", None):
            functions = [tool_call["function"] for tool_call in response["tool_calls"]]
            for function in functions:
                if function["name"] == "python":
                    code1 = function["arguments"]
                    if not is_valid_python_code(code1):
                        print("2222")
                        self.add_system_event(f"Invalid python code:\n{code1}")
                        return
                    print("self.param_path1 ", self.param_path1)
                    self.param_path1 = save_py_script(code1, "parametrization")
                    return code1


    def parameters_modification(self, parameters: str):
        """
        print("ssss")
        if not self.param_code:
            raise ValueError("Empty code!")

        code = self.param_code
        function = self.latex_function
        self.history.append({"role": "system", "content": consts.PARAMETERS_MODIFICATION_SYSTEM_PROMPT2.format(function=function)})
        self.history.append({"role": "user", "content": parameters})
        self.add_system_event(f"Parameters added to parametrization class: {parameters}")

        if not self.param_path:
            raise ValueError("Empty path!")
        """
        code = self.handle_parameters_modification(parameters)
        self.param_code1 = code
        self.add_system_event(f"New code {code} with parameters {parameters} in path {self.param_path1}")



    def inspect_directory(self, directory: str) -> None:
        try:
            contents = "\n".join([str(path) for path in Path(directory).iterdir()])
            self.add_system_event(f"Inspected directory {directory} with the contents:\n{contents}")
        except FileNotFoundError:
            self.add_system_event(f"Failed to inspect directory {directory} due to file not found error")
        except PermissionError:
            self.add_system_event(f"Failed to inspect directory {directory} due to permission error")
        except Exception as e:
            self.add_system_event(f"Failed to inspect directory {directory} with exception {e}")

    def run_experiment(self, config_path: str, results_path: str) -> None:
        try:
            if not config_path:
                raise ValueError("Empty config path!")
            if not results_path:
                raise ValueError("Empty results path!")

            experiment_id = generate_experiment_id()
            run_experiment(
                workers=-1, config_path=config_path, results_path=results_path, experiment_id=experiment_id, quiet=True
            )
            self.context["result_info"] = {
                "experiment_id": experiment_id,
                "config_path": config_path,
                "results_dir": results_path + "/" + experiment_id,
            }
            self.add_system_event(
                f"Ran experiment according to config {config_path} with results saved to {results_path}/{experiment_id}"
            )
        except FileNotFoundError:
            self.add_system_event(f"Failed to run experiment according to {config_path} due to file not found error")
        except PermissionError:
            self.add_system_event(f"Failed to run experiment according to {config_path} due to permission error")
        except Exception as e:
            self.add_system_event(f"Failed to run experiment according to {config_path} with exception {e}")

    def generate_graphs(self, experiment_path: str) -> None:
        try:
            if not experiment_path:
                raise ValueError("Empty experiment path!")

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
        return sum([len(message["content"]) for message in self.history] or 0)
