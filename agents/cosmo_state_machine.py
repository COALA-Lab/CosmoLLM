from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List

from agents.consts.functions2 import OPENAI_FUNCTIONS


class State(ABC):
    @abstractmethod
    def get_openai_functions(self) -> List[dict]:
        pass


    def get_state_system_prompt(self) -> str:
        pass


class DefineFunctionState(State):
    def get_openai_functions(self) -> List[dict]:
        return [
            OPENAI_FUNCTIONS.get("generate_parametrization"),
            OPENAI_FUNCTIONS.get("prior_selection")
            #OPENAI_FUNCTIONS.get("parameters_modification")
        ]

    def get_state_system_prompt(self) -> str:
        # kontekst za neko stanje mozes dodati preko self.context u chat_agent kao {result_info}
        return """
        You are currently in the "Define function" state.
        Firstly, expect a physicist to probably send a function in latex that needs to be converted 
        to a parameterized class.
        """
        #na kakav nacin rada da se fokusira u tom stanju
        #obavjesti korisnika da definira funkciju...
        #State context:
        #{result_info}

class ParameterModificationState(State):
    def get_openai_functions(self) -> List[dict]:
        return [
            OPENAI_FUNCTIONS.get("parameters_modification"),
            #OPENAI_FUNCTIONS.get("prior_selection")
        ]


    def get_state_system_prompt(self) -> str:
        return """
        You are currently in the "Parameters modification" state.

        You have following transitions available following the syntax:
        <change_function> -> <Define function>
        <run_experiment> -> <Selection Prior>
        
        """

class SelectionPriorState(State):
    def get_openai_functions(self) -> List[dict]:
        return [
            OPENAI_FUNCTIONS.get("inspect_directory"),
            OPENAI_FUNCTIONS.get("prior_selection"),
            OPENAI_FUNCTIONS.get("prior_selected"),
            OPENAI_FUNCTIONS.get("start_calculation")
        ]

    def get_state_system_prompt(self) -> str:
        return """
        
        You are currently in the "Selection Prior" state. 
        Firstly, a physicist wants to choose a prior for his calculation. 
        Inform him that all priors are in the directory and ask him if he wants to see 
        what is in directory or he already knows what he want to select.
        Then, if he wants to see directory, show him. 
        After he selected dont ask him again about selection of prior and showing the directory!
        Then, ask him if he wants to select another one or start the calculation.
        if he select start the calculation dont ask him anything just let him know that you will start the calculation.
        
        if he choose start the calculation you need to change state to "Run experiment"
        
        State context:
        {result_info}
        """



class DefineConfig(State):
    def get_openai_functions(self) -> List[dict]:
        return [
            OPENAI_FUNCTIONS["run_experiment"]
        ]

    def get_state_system_prompt(self) -> str:
        return """
        You are currently in the "DefineConfig" state.


        """


class ComputationState(State):
    def get_openai_functions(self) -> List[dict]:
        return [
            OPENAI_FUNCTIONS["config_selected"],
            OPENAI_FUNCTIONS["result_path_selected"],
            OPENAI_FUNCTIONS["inspect_directory"],

        ]

    def get_state_system_prompt(self) -> str:
        return """
        You are currently in the "Computation" state.
        Firstly, inform the physicist that all configs are in the directory and ask him if he wants to see 
        what is in directory or he already knows what he want to select.
        Then, if he wants to see directory, show him. 
        After he selected dont ask him again about selection of config and showing the directory!
        Then, ask him to write the path where he wants to save the results.
        After he selected dont ask him again about selection of path!
        Then, write him a message that you started calculating.
        
        State context:
        {result_info}
        """

class GraphPlotingAndResultPresentationState(State):
    def get_openai_functions(self) -> List[dict]:
        return [
        ]

    def get_state_system_prompt(self) -> str:
        return """
        asdasdsa
        <transition_action> -> <new_state>


        You are currently in the "Define function" state.

        You have following transitions available following the syntax:
        <set_parameters> -> <parameter_modification>
        """

