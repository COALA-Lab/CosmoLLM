import os
import subprocess
from argparse import ArgumentParser
from enum import Enum
from pprint import pprint

from agents.chat_agent import ChatAgent
from frontend.gui.consts import CHAT_INTRO_TEXT

root_dir = os.path.dirname(__file__)


class Actions(str, Enum):
    RUN = "RUN"
    SET_API_KEY = "SET_API_KEY"


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
    subprocess_env["PYTHONPATH"] = root_dir

    command = f"streamlit run --server.headless true --server.port 8000 {root_dir}/frontend/gui/main.py"
    subprocess.run(command, shell=True, env=subprocess_env, cwd=root_dir)


def main_admin() -> None:
    subprocess_env = os.environ.copy()
    subprocess_env["PYTHONPATH"] = root_dir

    command = f"streamlit run --server.headless true --server.port 8000 {root_dir}/frontend/admin/main.py"
    subprocess.run(command, shell=True, env=subprocess_env, cwd=root_dir)


def execute(console_mode: bool = False, gui_mode: bool = False, admin_mode: bool = False) -> None:
    if console_mode:
        main_console()
    elif gui_mode:
        main_gui()
    elif admin_mode:
        main_admin()
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
    parser.add_argument(
        '-a', '--admin',
        help="Run the admin gui.",
        action='store_true', default=False
    )
    parser.add_argument(
        '--action',
        help="Select the action to perform.",
        default=Actions.RUN.value,
        choices=[action.value for action in Actions]
    )
    args = parser.parse_args()

    if args.action.upper() == Actions.SET_API_KEY.value:
        api_key = input("Enter your OpenAI API key: ")
        file_location = root_dir + "/.env"
        try:
            with open(os.path.join(file_location), "w") as f:
                f.write(f"OPENAI_API_KEY={api_key}")
            print(f"Successfully saved key to {file_location}")
        except PermissionError:
            print("Failed to save key to .env file due to insufficient permissions.\n"
                  "Please rerun the command as `sudo` with the `--action set_api_key` flag.")
            exit(1)

    elif args.action.upper() == Actions.RUN.value:
        chosen_option_count = sum([args.console, args.gui, args.admin])
        if chosen_option_count > 1:
            raise ValueError("Cannot run in multiple modes at the same time (rerun with --help)!")
        try:
            execute(console_mode=args.console, gui_mode=args.gui, admin_mode=args.admin)
        except KeyboardInterrupt:
            pass
    else:
        raise ValueError(f"Unsupported action: {args.action}\n"
                         f"Available actions: {', '.join([action.value for action in Actions])}")

    print("\nExiting...")
