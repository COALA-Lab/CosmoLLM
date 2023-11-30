from unittest import TestCase

from llm_integrations.openai import ChatGPT  # noqa: F401
from llm_integrations.langchain import Chat  # noqa: F401


# TODO: remove this test after MVP

class TestChatSimple(TestCase):
    user_message = """
        this is the code of my function:
        def bla(a,b):
            return a*b
        write me a script that calls this function for all numbers a=1..20 and b=3..40.
        The code must make a 3d plot of the returned results,
        with a on the x axis, b on the y axis and the function's result on z axis.
    """

    followup_message = """
        Great, and what if I wanted bla to do addition?
    """

    def ask_and_print(self, agent, message: str) -> None:
        print(f"User: {message}", "\n")
        print("(Generating response...)")
        response = agent.send_message(message)
        print("+++++++++++++++++++++++++++++++++++++")
        print(f"Agent: {response}")
        print("+++++++++++++++++++++++++++++++++++++", "\n")

    def test_chat_simple(self):
        pass

        # for agent in [ChatGPT(), Chat()]:
        #     print("=====================================")
        #     print(f"{agent.__module__}.{agent.__class__.__name__}")
        #     print("=====================================")
        #     self.ask_and_print(agent, self.user_message)
        #     self.ask_and_print(agent, self.followup_message)
