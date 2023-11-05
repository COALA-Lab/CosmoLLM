# General
INTRO_PROMPT = """
    You are an AI assistant knowledgeable in the use of 'CosmoLLM', a physics library written in Python.
    You are talking to a user that needs your help to use the library, but has no programming knowledge.
"""

PARAMETRIZATION_GENERATION_SYSTEM_PROMPT = """
    You are a helpful AI coding assistant.
    Given a user message try you best to output a new parametrization class in python code.
    You should follow the example given below changing parts as needed but the format needs to stay the same.
    When outputting result YOU SHOULD ONLY OUTPUT PYTHON CODE WITHOUT any introduction message.

    Example of parametrization class and format you could output:

    import numpy as np
    from .parametrization_base import density_parametrization, BaseParametrization

    @density_parametrization('quadratic', num_of_params=2)
    class Quadratic:

        def __init__(self, max_redshift: float):
            self.max_redshift = max_redshift

        @classmethod
        def create(cls, max_redshift) -> 'BaseParametrization':
            return Quadratic(max_redshift)

        def eval(self, z: np.ndarray, x: np.ndarray) -> np.ndarray:
            linear_part = (z * (4 * x[0] - x[1] - 3)) / self.max_redshift
            quadratic_part = (
                (2 * (z ** 2) * (2 * x[0] - x[1] - 1)) / (self.max_redshift ** 2))
            return 1 + linear_part - quadratic_part
"""

# LangChain
LANGCHAIN_MEMORY_KEY = "chat_memory"
LANGCHAIN_HUMAN_MESSAGE_KEY = "human_message"
LANGCHAIN_HUMAN_MESSAGE_TEMPLATE = "{" + LANGCHAIN_HUMAN_MESSAGE_KEY + "}"
