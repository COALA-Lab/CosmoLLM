import io
import json
import os
from contextlib import redirect_stdout
from pathlib import Path
from typing import Union, List
import math
from PIL import Image
import copy
import json as json_module
import re
from utils.util import generate_experiment_id
from . import settings
from . import consts
from .consts import ResponseType
from .states import DefineParametrization, DefineParameterNames, UserChoice1, DefiningParametersIntervals, UserChoice2, UserChoice3, Calculation
from .utils import is_valid_python_code, compile_python_code, save_py_script, is_valid_json, save_json_file
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
            "latex_function": "",
            "params_names": List[str],
            "value_params": {},
            "params_filenames": {},
            "param_filename": str,
            "param_code": str,
            "results_path": str
        }
        self.prompt_explanation = []
        #self.llm = chatbot or ChatGPT(functions=consts.OPENAI_FUNCTIONS)
        self.llm = chatbot or ChatGPT()
        self.state = DefineParametrization()
        self.history_parametrization = []
        self.events_parametrization = []
        self.history_params_names = []
        self.events_params_names = []

    def reset(self) -> None:
        self.history = []
        self.events = []
        self.pending_images = []
        self.pending_data_tables = []
        self.context = {
            "last_message": "",
            "result_info": {},
            "latex_function": "",
            "params_names": List[str],
            "value_params": {},
            "params_filenames": {},
            "param_filename": str,
            "param_code": str,
            "results_path": str
        }
        self.prompt_explanation = []
        self.history_parametrization = []
        self.events_parametrization = []

    def send_message(self, message: str) -> str:
        if not message:
            raise ValueError("Empty message!")

        if message == "/help":
            return self.state.get_state_system_prompt()
        check_response = self.check_content_with_state(message)
        if "is not appropriate" in check_response:
            return f"{check_response}\n\nThis is a short description of the state:\n\n{self.state.get_state_system_prompt()}"
        response = self.choice_robustness(message)
        if response == "e":
            return "The query is not appropriate for this state. You have to choose between the keywords: transition or modify"
        print("bitno ", response)
        if response is None:
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

    #funkcija koja nije nuzno potrebana, ali povecava sigurnost dobrog odabira funkcije
    def choice_robustness(self, message):
        response = None
        if self.state.name == "User choice 1":
            if message == "transition":
                response = self.llm_complete(message, save_explanation=True, tool_choice={"type": "function", "function": {"name": "transition_new_state_selected"}})
            elif message == "modify":
                response = self.llm_complete(message, save_explanation=True, tool_choice={"type": "function", "function": {"name": "modify_parameterization_selected"}})
            else:
                return "e"
        if self.state.name == "User choice 2":
            if message == "transition":
                response = self.llm_complete(message, save_explanation=True, tool_choice={"type": "function", "function": {"name": "transition_new_state_selected"}})
            elif message == "modify":
                response = self.llm_complete(message, save_explanation=True, tool_choice={"type": "function", "function": {"name": "modify_parameter_names_selected"}})
            else:
                return "e"
        if self.state.name == "User choice 3":
            if message == "transition":
                response = self.llm_complete(message, save_explanation=True, tool_choice={"type": "function", "function": {"name": "transition_new_state_selected"}})
            elif message == "modify":
                response = self.llm_complete(message, save_explanation=True, tool_choice={"type": "function", "function": {"name": "modify_parameter_intervals_selected"}})
            else:
                return "e"
        return response


    def check_content_with_state(self, message: str) -> str:
        messages = []
        messages.extend(self.history)
        messages.extend([{"role": "system", "content": self.state.allowed_actions().format(**self.context, message=message)}])
        response1 = self.llm.complete(
            messages=messages,
            state=self.state,
            tool_choice="none"
        )
        print("response1.content ", response1.content)
        # response2 = self.llm.complete(
        #     [{"role": "system", "content": consts.NEGATIVE_OR_POSITIVE.format(text=response1.content)}],
        #     self.state,
        #     tool_choice="none"
        # )
        # print("response2.content ", response2)
        return response1.content

    def llm_complete(
            self, message: str, role: str = "user", ignore_events: bool = False, save_explanation: bool = False, tool_choice = "auto"
    ) -> dict:
        if not message:
            raise ValueError("Empty message!")

        messages = self._prepare_messages_and_events(message, role, ignore_events)
        if save_explanation:
            self.prompt_explanation = messages
        #response = self.llm.complete(messages)
        print("messages ", messages)
        response = {}
        response = self.llm.complete(messages, self.state, tool_choice=tool_choice)



        if response.get("tool_calls", None):
            functions = [tool_call["function"] for tool_call in response["tool_calls"]]
            for function in functions:
                name = function["name"]
                params = {}
                if function.get("arguments", None):
                    try:
                        params = json.loads(function["arguments"])
                    except json.JSONDecodeError:
                        self.add_system_event(
                            f"Failed to parse parameters for function call {name}"
                            f"with arguments {function['arguments']}"
                        )
                        return
                if list(params.values()):
                    param = list(params.values())[0]
                    if role == "user":
                        print("type(param)", type(param))
                        if type(param) == str:
                            if param not in message and message not in param:
                                response = self.llm.complete(messages, self.state, tool_choice="none")
                                return response
                        elif type(param) == list:
                            for p in param:
                                if type(p) == str:
                                    if p not in message and message not in p:
                                        response = self.llm.complete(messages, self.state, tool_choice="none")
                                        return response

                print(params, name)
                if (function := getattr(self, name, None)) is not None:
                    # get number of arguments of the function
                    num_args = function.__code__.co_argcount
                    print("num_args ", num_args)
                    print("len(params) ", len(params))
                    # get the name of the arguments of the function
                    args = function.__code__.co_varnames
                    # compare the number of arguments of the function and the number of arguments in the dictionary
                    if num_args - 1 != len(params):
                        response = self.llm.complete(messages, self.state, tool_choice="none")
                else:
                    self.add_system_event(f"Unknown function call {name}")
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
        print("self.events ", self.events)
        response = self.llm_complete(message, role="system", tool_choice="none")
        print("response1: ", response)
        print("response.get(tool_calls, None) ", response.get("tool_calls", None))
        # if response and response.get("tool_calls", None):
        #     raise Exception(
        #         "System update prompt should not result in a function call! (function chaining not yet supported)"
        #     )

        response = response.content
        if not response:
            raise Exception("Empty response from OpenAI!")
        return response

    def add_system_event(self, message: str) -> None:
        if not message:
            raise ValueError("Empty message!")

        self.events.append(message)

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
            self.state,
            tool_choice="none"
        )
        print("res: ", response)
        print("001. ", response.content)
        print("000. ", response.get("tool_calls", None))
        code = response.content.replace("```python\n", "").replace("\n```", "")
        if not is_valid_python_code(code):
            print("2222222")
            self.add_system_event(f"Invalid python code:\n{code}")
            return
        self.context["param_filename"] = save_py_script(code, module)
        print("ss", self.context["param_filename"])
        return code
        # if response.get("tool_calls", None):
        #     functions = [tool_call["function"] for tool_call in response["tool_calls"]]
        #     print("111. ", functions)
        #     for function in functions:
        #         print("222. ")
        #         if function["name"] == "python":
        #             code = function["arguments"]
        #             if not is_valid_python_code(code):
        #                 self.add_system_event(f"Invalid python code:\n{code}")
        #                 return
        #             self.param_filename = save_py_script(code, module)
        #             return code

    def handle_priori_generation(self, message: str) -> str:
        response = self._generate_code(message, settings.PRIORI_GENERATION_SYSTEM_PROMPT)
        return response

    def generate_priori(self) -> None:
        self.add_system_event(self.handle_priori_generation(self.context["last_message"]))

    def handle_parametrization_generation(self, message: str) -> str:
        response = self._generate_code(message, settings.PARAMETRIZATION_GENERATION_SYSTEM_PROMPT, "parametrization")
        self.context["param_code"] = response
        self.context["latex_function"] = message
        return response

    def generate_parametrization(self, parametrization_function_in_latex: str) -> None:
        code = self.handle_parametrization_generation(parametrization_function_in_latex)
        path = self.context["param_filename"]
        self.add_system_event(f"Generated parametrization code {code} with filename {path}")

    def transition_user_choice_1(self):
        self.history_parametrization = copy.deepcopy(self.history)
        self.events_parametrization = copy.deepcopy(self.events)
        self.state = DefineParameterNames()
        self.add_system_event("State changed. New state is Define parameter names")


    def transition_new_state_selected(self):
        if self.state.name == "User choice 1":
            self.transition_user_choice_1()
        elif self.state.name == "User choice 2":
            self.transition_user_choice_2()
        elif self.state.name == "User choice 3" or self.state.name == "Define parameters intervals":
            self.transition_user_choice_3()
        else:
            self.add_system_event("Wrong state for this function.")


    def modify_parameterization_selected(self):
        self.reset()
        self.state = DefineParametrization()
        self.add_system_event("State changed. New state is Define parametrization. The previous parameterization is deleted and the user can redefine the parameterization.")

    def transition_user_choice_2(self):
        self.history_params_names = copy.deepcopy(self.history)
        self.events_params_names = copy.deepcopy(self.events)
        self.state = DefiningParametersIntervals()
        self.add_system_event("State changed. New state is Defining parameter interval. ")

    def modify_parameter_names_selected(self):
        self.context["params_names"] = List[str]
        self.history = self.history_parametrization
        self.events = self.events_parametrization
        self.state = DefineParameterNames()
        self.add_system_event("State changed. New state is Define parameter names. Inform the user that the previous definition of the parameter name is deleted and the that user can redefine the parameters.")

    def extract_json(self, input_string, char_start='{', char_end='}'):
        idx_start = input_string.find(char_start)

        idx_end = input_string.rfind(char_end)

        if idx_start == -1 or idx_end == -1:
            return input_string

        return input_string[idx_start:idx_end + 1]

    def transition_user_choice_3(self):
        self.state = Calculation()
        param_filename = self.context["param_filename"].rstrip(".py")
        params_names = self.context["params_names"]
        params_filenames = self.context["params_filenames"]
        converted_params_names = "[" + ", ".join(f'"{item}"' for item in params_names) + "]"
        priori_config = ""
        params = list(params_filenames.keys())
        for parameter in params:
            priori_config += f'{params_filenames[parameter].rstrip(".py")}: "function"'
            if parameter != params[-1]:
                priori_config += ',\n'

        message = [{"role": "system", "content": consts.CONFIG_GENERATION_SYSTEM_PROMPT.format(parametrization_name=param_filename, params_names=converted_params_names, priori_config=priori_config)}]
        response1 = self.llm.complete(
            message,
            self.state,
            tool_choice="none"
        )
        print("1config- ", response1.content)
        #json = response1.content.replace("```json\n", "").replace("\n```", "")
        json = self.extract_json(response1.content)
        print("config- ", json)
        if not is_valid_json(json):
            self.add_system_event(f"Invalid json format:\n{json}")
            return
        json_dict = json_module.loads(json)
        saved_filename = save_json_file(json_dict, "configs")
        print("saved_filename", saved_filename)
        results_path = self.run_experiment(config_path=saved_filename, results_path="/Users/andrearakocija/Desktop/FER/Diplomskirad/CosmoLLM/results")
        self.generate_graphs(results_path)
        self.inspect_directory(results_path)
        self.context["results_path"] = results_path
        if results_path is not None:
            self.add_system_event(f"Notify the user that the calculation is complete. Show the user content of inspected directory. Tell him that you can show him some of the graph images or display numerical results, if he wants.")

    def modify_parameter_intervals_selected(self):
        self.history = self.history_params_names
        self.events = self.events_params_names
        self.context["value_params"] = {param: None for param in self.context["params_names"]}
        self.context["params_filenames"] = {}
        self.state = DefiningParametersIntervals()
        self.add_system_event("State changed. New state is Define parameters intervals. The previous parameter interval definition is deleted and the user can redefine the intervals.")
    def define_parameters_intervals(self, intervals_for_parameters: List[dict]) -> None:
        print(intervals_for_parameters)
        value_params_dict = self.context["value_params"]
        none_values = []
        defined_params = []
        python_codes = {}

        for interval_dict in intervals_for_parameters:
            if not interval_dict or not interval_dict["param_name"]:
                continue

            parameter = interval_dict["param_name"]
            low = interval_dict["low"]
            high = interval_dict["high"]
            if math.isinf(low) or math.isinf(high):
                continue

            index = self.context["params_names"].index(parameter)
            # Generate the Python code for priori generation
            message = [{"role": "system", "content": consts.PRIORI_GENERATION_SYSTEM_PROMPT.format(index=index, low=low, high=high)}]
            response1 = self.llm.complete(
                message,
                self.state,
                tool_choice="none"
            )
            code = response1.content.replace("```python\n", "").replace("\n```", "")
            print("code for priori ", code)
            if not is_valid_python_code(code):
                self.add_system_event(f"Invalid python code:\n{code}")
                return

            python_codes[parameter] = code  # Store the code in the dictionary

            value_params_dict[parameter] = {"low": low, "high": high}
            defined_params.append(parameter)

        # Save the Python scripts after the loop
        params_filenames_dict = self.context["params_filenames"]
        for parameter, code in python_codes.items():
            filename = save_py_script(code, "priori")
            params_filenames_dict[parameter] = filename

        none_values = [key for key, value in value_params_dict.items() if value is None]
        if not none_values:
            self.state = UserChoice3()
            self.add_system_event(f"{self.state.next_state()}")
        else:
            self.add_system_event(f"Defined parameter/s: {defined_params}. Not defined parameter/s: {none_values}. Inform the user that he does not have to define all the parameters and that he can move to a new state if he writes: transition to a new state.")



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
            return f"{results_path}/{experiment_id}"
        except FileNotFoundError:
            self.add_system_event(f"Failed to run experiment according to {config_path} due to file not found error")
        except PermissionError:
            self.add_system_event(f"Failed to run experiment according to {config_path} due to permission error")
        except Exception as e:
            print("exx ", e)
            self.add_system_event(f"Failed to run experiment according to {config_path} with exception {e}")


    def define_parameter_names(self, parameters: List[str]) -> None:

        parameters_independence_result = {param: self.check_valid_parameter(param, self.context["latex_function"]) for param in parameters}
        is_any_parameter_false = any(not value for value in parameters_independence_result.values())
        false_parameters = [param for param, is_independent in parameters_independence_result.items() if not is_independent]
        if is_any_parameter_false:
            self.add_system_event(f"Inform the user that these parameters are not within the parameterization: {false_parameters}. Must redefine the parameter names.")
        else:
            self.context["params_names"] = parameters
            self.context["value_params"] = {param: None for param in parameters}
            #self.handle_parametrization_generation(self.context["latex_function"])
            print("self.context[latex_function]", self.context["latex_function"])
            self.generate_parametrization(self.context["latex_function"])
            self.state = UserChoice2()
            self.add_system_event(f"Specified parameter names: {parameters}. {self.state.next_state()}")

    import re
    def check_valid_parameter(self, param, latex_str):
        # Kreiranje regularnog izraza za svaki parametar
        # Ovaj regularni izraz provjerava da li su znakovi neposredno prije i poslije parametra ne-slova
        regex = r'(?<![a-zA-Z])' + re.escape(param) + r'(?![a-zA-Z])'
        return bool(re.search(regex, latex_str))

    def define_parametrization(self, parametrization_function_in_latex: str) -> None:
        self.context["latex_function"] = parametrization_function_in_latex

        #self.send_message(f"{self.state.next_state()}")
        self.state = UserChoice1()
        self.add_system_event(f"Defined parametrization {parametrization_function_in_latex}. {self.state.next_state()}")



    def trim_history(self) -> None:
        while self._get_history_length() > settings.MAX_HISTORY_LENGTH:
            self.history.pop(0)

    def _get_history_length(self) -> int:
        return sum([len(message["content"]) for message in self.history] or 0)



    def display_image(self, image_path: str) -> None:
        try:
            path = self.context["results_path"]
            abs_path = path + "/" + image_path
            Image.open(abs_path)
            self.pending_images.append(abs_path)
            self.add_system_event(f"Displayed image from {abs_path}. {self.state.next_state()}")
        except FileNotFoundError:
            self.add_system_event(f"Failed to display image from {abs_path} due to file not found error")
        except PermissionError:
            self.add_system_event(f"Failed to display image from {abs_path} due to permission error")
        except Exception as e:
            self.add_system_event(f"Failed to display image from {abs_path} with exception {e}")

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
