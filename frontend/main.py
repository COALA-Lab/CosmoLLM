from typing import Union

import streamlit as st

from agents.chat_agent import ChatAgent
from consts import CHAT_INTRO_TEXT


def display_past_conversation() -> None:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if isinstance(message["content"], dict) or isinstance(message["content"], list):
                st.write(message["content"])
            elif isinstance(message["content"], str):
                st.markdown(message["content"])


def display_message(role: str, content: str, save_to_history: bool = True) -> None:
    with st.chat_message(role):
        st.markdown(content)

    if save_to_history:
        add_message_to_history(role, content)


def display_collection(role: str, content: dict, save_to_history: bool = True) -> None:
    with st.chat_message(role):
        st.write(content)

    if save_to_history:
        add_message_to_history(role, content)


def add_message_to_history(role: str, content: Union[str, dict]) -> None:
    st.session_state.messages.append({"role": role, "content": content})


def main():
    if "agent" not in st.session_state:
        agent = ChatAgent()
        st.session_state.agent = agent
    else:
        agent = st.session_state.agent

    st.title("Cosmo LLM")

    display_message("system", CHAT_INTRO_TEXT, save_to_history=False)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    display_past_conversation()

    if user_input := st.chat_input("Enter your message here"):
        display_message("user", user_input)

        if user_input.lower() == "/reset":
            agent.reset()
            display_message("system", "Resetting the chatbot")
            return
        elif user_input.lower() == "/explain":
            display_collection("system", agent.prompt_explanation)
            return

        with st.spinner("Responding..."):
            response = agent.send_message(user_input)
        display_message("assistant", response)


if __name__ == "__main__":
    main()
