from llm_integrations.openai import ChatGPT


def execute():
    agent = ChatGPT()

    print("You are now chatting with a GPT powered chatbot. Type 'quit' to exit.")
    while True:
        user_input = input("You: ")
        if user_input == "quit":
            break

        response = agent.send_message(user_input)
        if not isinstance(response, str):
            if agent.events:
                response = agent.send_system_update(
                    "Respond to the system events for the user."
                    "The user does not see the events or know that they exist."
                    "The user didn't cause the events. They were caused either by you or an external system."
                    "It is likely that an event is the result of some action you did, for example loading a file."
                    "You have to be very user friendly when summarizing the events for the user."
                )
                if not isinstance(response, str):
                    raise Exception("Bot response should be a string after system update")
        # response = agent.handle_parametrization_generation(user_input)
        # response = agent.handle_priori_generation(user_input)
        print("Bot: " + response)


if __name__ == "__main__":
    execute()
