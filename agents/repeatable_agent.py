from llm_integrations.openai.repeatable_agent import RepeatableChatGPT


class RepeatableAgent:
    def __init__(self, chatbot: RepeatableChatGPT = None):
        if chatbot is None:
            chatbot = ()
        self.chatbot = chatbot

    def send_message(self, message: str) -> str:
        response = self.chatbot.generate_answer(message)
        if not isinstance(response, str):
            if self.chatbot.events:
                response = self.chatbot.generate_events_answer(
                    "Respond to the system events for the user."
                    "The user does not see the events or know that they exist."
                    "The user didn't cause the events. They were caused either by you or an external system."
                    "It is likely that an event is the result of some action you did, for example loading a file."
                    "You have to be very user friendly when summarizing the events for the user."
                )
                if not isinstance(response, str):
                    raise Exception("Bot response should be a string after system update")
        return response

    def reset(self) -> None:
        self.chatbot.reset()
