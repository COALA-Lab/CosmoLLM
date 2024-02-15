from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List

from agents.consts.functions2 import OPENAI_FUNCTIONS


class State(ABC):

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def get_openai_functions(self) -> List[dict]:
        pass

    @abstractmethod
    def get_state_system_prompt(self) -> str:
        pass

    @abstractmethod
    def allowed_actions(self) -> str:
        pass

    @abstractmethod
    def next_state(self) -> str:
        pass



class DefineParametrization(State):


    def __init__(self):
        self.name = "Define parametrization"

    def get_openai_functions(self) -> List[dict]:
        return [
            OPENAI_FUNCTIONS.get("define_parametrization")
        ]


    def get_state_system_prompt(self) -> str:
        return """You are currently in Define parametrization state.\nIn this state, the user can define parametrization/function in LaTeX."""

    def allowed_actions(self) -> str:
        return """
            You are currently in "Define parametrization" state. \
            The goal of this state is for the user to define the function in LaTeX. \
            In this state, the user can do actions that are allowed. \
            Actions that are allowed to the user are: \
            - to greet, \
            - define parametrization/function in latex, \
            - ask questions about the parameterization, \
            - ask questions about the parametrization that he was defined, \
            - ask questions about the state of the system. \
            - ask questions what he should do, and you explain the state to him. \
            Actions that are not allowed to the user: \
            - any other actions.\
            Specifically, we want the system to remain in this state. \
            We want the system to be robust. \
            This is the action: {message} \
            The action is appropriate if it is allowed, it is not appropriate if it is not allowed. \
            Your task is to evaluate is the action appropriate for this state. \
            If it is appropriate, explain why you decide it. \
            If it is not appropriate, explain why you decide it.  
        """
    def next_state(self) -> str:
        return """
           
        """

class UserChoice1(State):

    def __init__(self):
        self.name = "User choice 1"

    def get_openai_functions(self) -> List[dict]:
        return [
            OPENAI_FUNCTIONS.get("transition_new_state_selected"),
            OPENAI_FUNCTIONS.get("modify_parameterization_selected")
        ]

    def get_state_system_prompt(self) -> str:
        return """You are currently in "User choice" state.\nIn this state, the user can choose between the keywords: "transition" or "modify"."""

    def allowed_actions(self) -> str:
        return """
            You are currently in "User choice" state. \
            The goal of this state is for the user to select an option by writing keywords. \
            In this state, the user can do actions that are allowed. \
            Actions that are allowed to the user are: \
            - select an option by writing keywords, \
            Actions that are not allowed to the user: \
            - any other actions.\
            Specifically, we want the system to remain in this state. \
            We want the system to be robust. \
            This is the action: {message} \
            The action is appropriate if it is allowed, it is not appropriate if it is not allowed. \
            Your task is to evaluate is the action appropriate for this state. \
            If it is appropriate, explain why you decide it. \
            If it is not appropriate, explain why you decide it.  
        """

    def next_state(self) -> str:
        return  """
            TASK:
            Inform the user that he has defined the parameterization and \
            that it can now pass to the next state: Defining the parameter name. \
            Tell him to choose between two options by writing keywords: \
                - keyword: "modify" for modify the parameterization
                - keyword: "transition" for transition to a new state
             
            
        """



class DefineParameterNames(State):

    def __init__(self):
        self.name = "Define parameter names"


    def get_openai_functions(self) -> List[dict]:
        return [
            OPENAI_FUNCTIONS.get("define_parameter_names"),
        ]

    def get_state_system_prompt(self) -> str:
        return """You are currently in "Define parameter names" state.\nIn this state, the user can define the names of the parameters of this parameterization."""

    def allowed_actions(self) -> str:
        return """
            You are currently in "Define parameter names" state. \
            The goal of this state is for the user to define the names of the parameters of this parameterization: {latex_function}. \
            In this state, the user can do actions that are allowed. \
            Actions that are allowed to the user are: \
            - define the names of the parameters, \
            - ask questions about the parameterization, \
            - ask questions about the parametrization that he was defined, \
            - ask questions about the state of the system. \
            - ask questions what he should do, and you explain the state to him. \
            Actions that are not allowed to the user: \
            - any other actions.\
            Specifically, we want the system to remain in this state. \
            We want the system to be robust. \
            This is the action: {message} \
            The action is appropriate if it is allowed, it is not appropriate if it is not allowed. \
            Your task is to evaluate is the action appropriate for this state. \
            If it is appropriate, explain why you decide it. \
            If it is not appropriate, explain why you decide it. 
        """

    def next_state(self) -> str:
        return """
            
        """

class UserChoice2(State):

    def __init__(self):
        self.name = "User choice 2"

    def get_openai_functions(self) -> List[dict]:
        return [
            OPENAI_FUNCTIONS.get("transition_new_state_selected"),
            OPENAI_FUNCTIONS.get("modify_parameter_names_selected")
        ]

    def get_state_system_prompt(self) -> str:
        return """You are currently in "User choice" state.\nIn this state, the user can choose between the keywords: "transition" or "modify"."""

    def allowed_actions(self) -> str:
        return """
            You are currently in "User choice" state. \
            The goal of this state is for the user to select an option by writing keywords. \
            In this state, the user can do actions that are allowed. \
            Actions that are allowed to the user are: \
            - select an option by writing keywords, \
            Actions that are not allowed to the user: \
            - any other actions.\
            Specifically, we want the system to remain in this state. \
            We want the system to be robust. \
            This is the action: {message} \
            The action is appropriate if it is allowed, it is not appropriate if it is not allowed. \
            Your task is to evaluate is the action appropriate for this state. \
            If it is appropriate, explain why you decide it. \
            If it is not appropriate, explain why you decide it.  
        """

    def next_state(self) -> str:
        return  """
            TASK:
            Inform the user that he has specified parameter names and \
            that it can now transition to the next state: Defining parameters within certain intervals. \
            Tell him to choose between two options by writing keywords: \
                - keyword: "modify" for modify the parameter names
                - keyword: "transition" for transition to a new state
             
            
        """

class DefiningParametersIntervals(State):

    def __init__(self):
        self.name = "Define parameters intervals"


    def get_openai_functions(self) -> List[dict]:
        return [
            OPENAI_FUNCTIONS.get("define_parameters_intervals"),
            OPENAI_FUNCTIONS.get("transition_new_state_selected")
        ]

    def get_state_system_prompt(self) -> str:
        return """You are currently in "Define parameters intervals" state.\nIn this state, the user can define parameters within specified intervals to precisely limit values."""

    def allowed_actions(self) -> str:
        return """
            You are currently in "Define parameters intervals" state. \
            The goal of this state is for the user to define parameters within specified intervals to precisely limit values. \
            In this state, the user can do actions that are allowed. \
            Actions that are allowed to the user are: \
            - define parameters within specified intervals, \
            - ask questions about the parameterization, \
            - ask questions about the parametrization that he was defined, \
            - ask questions about the state of the system. \
            - ask questions what he should do, and you explain the state to him. \
            Actions that are not allowed to the user: \
            - any other actions.\
            Specifically, we want the system to remain in this state. \
            We want the system to be robust. \
            This is the action: {message} \
            The action is appropriate if it is allowed, it is not appropriate if it is not allowed. \
            Your task is to evaluate is the action appropriate for this state. \
            If it is appropriate, explain why you decide it. \
            If it is not appropriate, explain why you decide it. 
        """

    def next_state(self) -> str:
        return """
            
        """

class UserChoice3(State):

    def __init__(self):
        self.name = "User choice 3"

    def get_openai_functions(self) -> List[dict]:
        return [
            OPENAI_FUNCTIONS.get("transition_new_state_selected"),
            OPENAI_FUNCTIONS.get("modify_parameter_intervals_selected")
        ]

    def get_state_system_prompt(self) -> str:
        return """You are currently in "User choice" state.\nIn this state, the user can choose between the keywords: "transition" or "modify"."""

    def allowed_actions(self) -> str:
        return """
            You are currently in "User choice" state. \
            The goal of this state is for the user to select an option by writing keywords. \
            In this state, the user can do actions that are allowed. \
            Actions that are allowed to the user are: \
            - select an option by writing keywords, \
            Actions that are not allowed to the user: \
            - any other actions.\
            Specifically, we want the system to remain in this state. \
            We want the system to be robust. \
            This is the action: {message} \
            The action is appropriate if it is allowed, it is not appropriate if it is not allowed. \
            Your task is to evaluate is the action appropriate for this state. \
            If it is appropriate, explain why you decide it. \
            If it is not appropriate, explain why you decide it.  
        """

    def next_state(self) -> str:
        return  """
            TASK:
            Inform the user that he has defined all parameter intervals and \
            that it can now transition to the next state: Calculation. \
            Tell him to choose between two options by writing keywords: \
                - keyword: "modify" for modify the parameter intervals
                - keyword: "transition" for transition to a new state
             
            
        """

class Calculation(State):

    def __init__(self):
        self.name = "Calculation and result presentation"



    def get_openai_functions(self) -> List[dict]:
        return [
            OPENAI_FUNCTIONS.get("display_image"),
            OPENAI_FUNCTIONS.get("modify_parameter_intervals_selected"),
            OPENAI_FUNCTIONS.get("modify_parameterization_selected")
        ]

    def get_state_system_prompt(self) -> str:
        return """You are currently in "Calculation and result presentation" state.\nIn this state, the user can ask for display image."""

    def allowed_actions(self) -> str:
        return """
            You are currently in "Calculation and result presentation" state. \
            In this state, the user can do actions that are allowed. \
            Actions that are allowed to the user are: \
            - define parameters within specified intervals, \
            - ask for display image, \
            - ask questions about the parameterization, \
            - ask questions about the parametrization that he was defined, \
            - ask questions about the parameter names that he was defined, \
            - ask questions about the parameter intervals that he was defined, \
            - ask questions about the state of the system. \
            - ask questions what he should do, and you explain the state to him. \
            - modify parameterization \
            - modify intervals \
            Actions that are not allowed to the user: \
            - any other actions.\
            Specifically, we want the system to remain in this state. \
            We want the system to be robust. \
            This is the action: {message} \
            The action is appropriate if it is allowed, it is not appropriate if it is not allowed. \
            Your task is to evaluate is the action appropriate for this state. \
            If it is appropriate, explain why you decide it. \
            If it is not appropriate, explain why you decide it. 
        """

    def next_state(self) -> str:
        return """
            TASK:
            
            Inform the user that he can continue viewing the results or if he has viewed all the results \
            he was interested in, he can try other intervals within \
            the same parameterization or a completely new parameterization. \
            Tell him that if he wants to try another parametrization, \
            type the keyword "modify parameterization", and if he wants to try other intervals, \
            type the keyword "modify intervals".
             
            
        """




