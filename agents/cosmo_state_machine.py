from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List

from agents.consts.functions2 import OPENAI_FUNCTIONS


class State(ABC):
    @abstractmethod
    def get_openai_functions(self) -> List[dict]:
        pass

    @abstractmethod
    def get_state_system_prompt(self) -> str:
        pass


class DefineFunctionState(State):
    def get_openai_functions(self) -> List[dict]:
        return [
            OPENAI_FUNCTIONS["generate_parametrization"]
        ]
        pass

    def get_state_system_prompt(self) -> str:
        # kontekst za neko stanje mozes dodati preko self.context u chat_agent kao {result_info}
        return """
        asdasdsa
        <transition_action> -> <new_state>
        
        
        You are currently in the "Define function" state.
        
        You have following transitions available following the syntax:
        <set_parameters> -> <parameter_modification>
        
        State context:
        {result_info}
        """



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