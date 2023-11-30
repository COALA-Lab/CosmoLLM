from llm_integrations.openai import ChatGPT


def execute():
    agent = ChatGPT()

    print("You are now chatting with a GPT powered chatbot. Type 'quit' to exit.")
    while True:
        user_input = input("You: ")
        if user_input == "quit":
            break

        #response = agent.send_message(user_input)
        response = agent.handle_parametrization_generation(user_input)
        # response = agent.handle_priori_generation(user_input)
        print("Bot: " + response)


if __name__ == "__main__":
    execute()
