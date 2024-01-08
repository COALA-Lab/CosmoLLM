from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List

from agents.consts.functions2 import OPENAI_FUNCTIONS


class State:
    @abstractmethod
    def get_openai_functions(self) -> List[dict]:
        pass


    def get_state_system_prompt(self) -> str:
        return """
        the syntax of the transition from the current state to another is this:
        <transition_action> -> <new_state
        """


class DefineFunctionState(State):
    def get_openai_functions(self) -> List[dict]:
        return [
            OPENAI_FUNCTIONS.get("generate_parametrization")
        ]
        pass

    def get_state_system_prompt(self) -> str:
        # kontekst za neko stanje mozes dodati preko self.context u chat_agent kao {result_info}
        return """
        The syntax of the transition from the current state to another is this:
        <transition_action> -> <new_state>
        
        You are currently in the "Define function" state.
        
        You have following transitions available following the syntax:
        <set_parameters> -> <parameter_modification>
        
        na kakav nacin rada da se fokusira u tom stanju
        obavjesti korisnika da definira funkciju...
       
        """
        #State context:
        #{result_info}

class ParameterModificationState(State):
    def get_openai_functions(self) -> List[dict]:
        return [
            OPENAI_FUNCTIONS["generate_parametrization"]
        ]
        pass

    def get_state_system_prompt(self) -> str:
        return """
        asdasdsa
        <transition_action> -> <new_state>


        You are currently in the "Define function" state.

        You have following transitions available following the syntax:
        <set_parameters> -> <parameter_modification>
        """


class ComputationState(State):
    def get_openai_functions(self) -> List[dict]:
        return [
            OPENAI_FUNCTIONS["generate_parametrization"]
        ]
        pass

    def get_state_system_prompt(self) -> str:
        return """
        asdasdsa
        <transition_action> -> <new_state>


        You are currently in the "Define function" state.

        You have following transitions available following the syntax:
        <set_parameters> -> <parameter_modification>
        """

class GraphPlotingAndResultPresentationState(State):
    def get_openai_functions(self) -> List[dict]:
        return [
            OPENAI_FUNCTIONS["generate_parametrization"]
        ]
        pass

    def get_state_system_prompt(self) -> str:
        return """
        asdasdsa
        <transition_action> -> <new_state>


        You are currently in the "Define function" state.

        You have following transitions available following the syntax:
        <set_parameters> -> <parameter_modification>
        """


