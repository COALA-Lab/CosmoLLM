import os
import subprocess

from argparse import ArgumentParser
from pprint import pprint

from consts import CHAT_INTRO_TEXT
from llm_integrations.openai.repeatable_agent import RepeatableChatGPT


def main_console() -> None:
    agent = RepeatableChatGPT()
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

        response = agent.generate_answer(user_input)
        print("Bot: " + response)
        while True:
            user_input = input("Confirm? (Y/N): ").strip()
            if user_input.lower() in ["y", "yes"]:
                agent.confirm_answer()
                break
            elif user_input.lower() in ["n", "no"]:
                response = agent.regenerate_answer()
                print("Bot: " + response)
                continue;


def main_gui() -> None:
    subprocess_env = os.environ.copy()
    subprocess_env["PYTHONPATH"] = os.getcwd()

    command = f"streamlit run frontend/main.py"
    subprocess.run(command, shell=True, env=subprocess_env, cwd=os.getcwd())


def execute(console_mode: bool = False, gui_mode: bool = False) -> None:
    if console_mode:
        main_console()
    elif gui_mode:
        main_gui()
    else:
        raise NotImplementedError("No mode selected! Please select either console or GUI mode (rerun with --help).")


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
