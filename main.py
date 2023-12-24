import os
import subprocess

from argparse import ArgumentParser
from pprint import pprint

from agents.chat_agent import ChatAgent
from frontend.consts import CHAT_INTRO_TEXT


def main_console() -> None:
    agent = ChatAgent()
    print(CHAT_INTRO_TEXT)
    print("Type 'quit' to exit.\n")
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ["quit", "exit", "q"]:
            break
        elif user_input.lower() == "reset":
            agent.reset()
            print("Bot: Resetting the chatbot")
            continue
        elif user_input.lower() == "history":
            print("History:")
            pprint(agent.history)
            continue

        response = agent.send_message(user_input)
        print("Bot: " + response)


def main_gui() -> None:
    subprocess_env = os.environ.copy()
    subprocess_env["PYTHONPATH"] = os.getcwd()

    command = "streamlit run frontend/main.py"
    subprocess.run(command, shell=True, env=subprocess_env, cwd=os.getcwd())


def execute(console_mode: bool = False, gui_mode: bool = False) -> None:
    if console_mode:
        main_console()
    elif gui_mode:
        main_gui()
    else:
        print("No display mode selected. Defaulting to GUI mode...")
        main_gui()


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        '-c', '--console',
        help="Run the bot in console mode.",
        action='store_true', default=False
    )
    parser.add_argument(
        '-g', '--gui',
        help="Run the bot in GUI mode.",
        action='store_true', default=False
    )
    args = parser.parse_args()

    if args.console and args.gui:
        raise ValueError("You cannot run the bot in both console and GUI mode at the same time (rerun with --help)!")

    try:
        execute(console_mode=args.console, gui_mode=args.gui)
    except KeyboardInterrupt:
        pass
    print("\nExiting...")
