from typing import Union

import pandas as pd
import streamlit as st

from agents.chat_agent import ChatAgent
from consts import CHAT_INTRO_TEXT, ContentType
from frontend.utils.auth import Auth


def display_past_conversation() -> None:
    for message in st.session_state.messages:
        if message["type"] == ContentType.COLLECTION:
            display_collection(message["role"], message["content"], save_to_history=False)
        elif message["type"] == ContentType.TEXT:
            display_message(message["role"], message["content"], save_to_history=False)
        elif message["type"] == ContentType.IMAGE:
            display_image(message["role"], message["content"], save_to_history=False)
        elif message["type"] == ContentType.DATA_TABLE:
            display_data_table(message["role"], message["content"], save_to_history=False)


def display_message(role: str, content: str, save_to_history: bool = True) -> None:
    if not content:
        return

    with st.chat_message(role):
        st.markdown(content)

    if save_to_history:
        add_message_to_history(role, content, ContentType.TEXT)


def display_collection(role: str, content: dict, save_to_history: bool = True) -> None:
    if not content:
        return

    with st.chat_message(role):
        st.write(content)

    if save_to_history:
        add_message_to_history(role, content, ContentType.COLLECTION)


def display_image(role: str, image_path: str, save_to_history: bool = True) -> None:
    if not image_path:
        return

    with st.chat_message(role):
        st.image(image_path)

    if save_to_history:
        add_message_to_history(role, image_path, ContentType.IMAGE)


def display_data_table(role: str, data_table_path: str, save_to_history: bool = True) -> None:
    if not data_table_path:
        return

    with st.chat_message(role):
        data_table_type = data_table_path.split(".")[-1]
        if data_table_type == "csv":
            data_table = pd.read_csv(data_table_path)
        elif data_table_type == "json":
            data_table = pd.read_json(data_table_path)
        else:
            raise ValueError(f"Unsupported data table type: {data_table_type}")
        st.dataframe(data_table)

    if save_to_history:
        add_message_to_history(role, data_table_path, ContentType.DATA_TABLE)


def add_message_to_history(role: str, content: Union[str, dict, list], content_type: ContentType) -> None:
    st.session_state.messages.append({"role": role, "content": content, "type": content_type})


def clear_conversation() -> None:
    st.session_state.messages = []
    st.rerun()


def main():
    st.sidebar.title("Actions")

    auth = Auth()

    if not auth.login():
        return

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "agent" not in st.session_state:
        agent = ChatAgent()
        st.session_state.agent = agent

        for message in agent.history:
            add_message_to_history(message["role"], message["content"], ContentType.TEXT)
    else:
        agent = st.session_state.agent

    st.title("Cosmo LLM")

    display_message("system", CHAT_INTRO_TEXT, save_to_history=False)

    display_past_conversation()

    if user_input := st.chat_input("Enter your message here"):
        display_message("user", user_input)

        if user_input.lower() == "/reset":
            agent.reset()
            clear_conversation()
            return
        elif user_input.lower() == "/explain":
            display_collection("system", agent.prompt_explanation)
            return
        elif user_input.lower() == "/clear":
            clear_conversation()

        with st.spinner("Responding..."):
            response = agent.send_message(user_input)
            if not response:
                raise ValueError("The agent returned an empty response!")

        if agent.pending_images:
            for image_path in agent.pending_images:
                display_image("assistant", image_path)
            agent.pending_images = []
        if agent.pending_data_tables:
            for data_table_path in agent.pending_data_tables:
                display_data_table("assistant", data_table_path)
            agent.pending_data_tables = []
        display_message("assistant", response)


if __name__ == "__main__":
    main()
