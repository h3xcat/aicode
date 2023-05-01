#!/usr/bin/env python3
import random
import string
import time
import sys
import os
import configparser
from pathlib import Path
from colorama import Fore, Style, init
from typing import List, Dict
from util.command_parser import command_parser

import config_handler

init(autoreset=True)
import openai


config, config_path = config_handler.load_config()

APP_ROOT = Path(__file__).resolve().parent


def clear_console():
    os.system("cls" if os.name == "nt" else "clear")


def display_help():
    clear_console()
    print(Fore.YELLOW + "Supported Commands:")
    print(Fore.YELLOW + "  /apikey <api_key> - Set the OpenAI API key")
    print(Fore.YELLOW + "  /model <model_name> - Set the GPT model to use (default: gpt-3.5-turbo)")
    print(Fore.YELLOW + "  /project <folder_path> - Set the project folder path")
    print(Fore.YELLOW + "  /undo - Undo the previous prompt")
    print(Fore.YELLOW + "  /forget - Clear the entire conversation")
    print(Fore.YELLOW + "  /view - Display the full conversation")
    print(Fore.YELLOW + "  /help - Show this help screen")
    print(Fore.YELLOW + "  /exit - End the conversation and exit the chat")


def load_aiscope(project_path: Path) -> List[str]:
    aiscope_path = project_path / ".aiscope"
    patterns = []

    if aiscope_path.is_file():
        with open(aiscope_path, "r", encoding="utf-8") as f:
            for line in f.readlines():
                pattern = line.strip().partition("#")[0].strip()
                if pattern:
                    patterns.append(pattern)
    return patterns


def matches_root_pattern(root_path: Path, path: Path, pattern: str) -> bool:
    absolute_pattern = root_path.joinpath(*(Path(pattern.lstrip('/')).parts))
    return path == absolute_pattern.relative_to(root_path)


def exclude_files_from_scoped_list(scoped_files: List[Path], exclude_patterns: List[str]) -> List[Path]:
    final_list = []

    for filepath in scoped_files:
        excluded = any(
            filepath.match(pattern)
            for pattern in exclude_patterns
        )
        if not excluded:
            final_list.append(filepath)

    return final_list


def load_project_files(project_path: Path, aiscope_patterns: List[str]) -> List[Dict[str, str]]:
    scoped_files = set()

    for pattern in aiscope_patterns:
        relative_pattern = pattern[1:] if pattern.startswith("!") else pattern
        if pattern.startswith("!"):
            excluded_files = set(project_path.glob(relative_pattern))
            scoped_files = scoped_files - excluded_files
        else:
            included_files = set(project_path.glob(relative_pattern))
            scoped_files = scoped_files | included_files

    file_contents = []
    for filepath in scoped_files:
        if filepath.is_file():
            relative_path = filepath.relative_to(project_path)
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                file_contents.append({"filename": str(relative_path), "content": content})

    return file_contents


def write_output_file(project_path: Path, relative_file_path: Path, file_content: str):
    temp_folder = project_path / "aicode_out"
    file_path = temp_folder / relative_file_path

    if not file_path.is_relative_to(temp_folder):
        print(Fore.RED + f"Error: {relative_file_path} is not a valid path")
        return

    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(file_content)
    print(Fore.LIGHTBLACK_EX + f"Wrote the new content to {file_path}")


def generate_random_string() -> str:
    return "".join(random.choices(string.ascii_uppercase, k=10))


rand_code_block_id = generate_random_string()
initial_system_prompt = f"""
You are a code assistant.
Use following format when providing code responses:

START_ASSISTANT_FILE_{rand_code_block_id}:<filepath>
<content>
END_ASSISTANT_FILE_{rand_code_block_id}

Do not include markdown code notation, such as "```python" or "```"

Example:

START_ASSISTANT_FILE_{rand_code_block_id}:hello_world.py
print("hello world!")
END_ASSISTANT_FILE_{rand_code_block_id}
"""

messages = []
model = config.get("Settings", "model", fallback="gpt-3.5-turbo")
openai.api_key = config.get("Settings", "apikey", fallback=os.environ.get("OPENAI_KEY"))

clear_console()
display_help()

try:
    while True:
        try:
            user_input = input(Fore.BLUE + Style.BRIGHT + "You       > " + Style.RESET_ALL)
        except EOFError:
            break
        except KeyboardInterrupt:
            break

        user_input = user_input.strip()

        if user_input.startswith("/"):
            command_args = command_parser(user_input)
            command = command_args[0].lower()
            args = command_args[1:]

            if command == "/exit":
                break
            elif command == "/apikey":
                key = args[0]
                print(Fore.LIGHTBLACK_EX + f"Setting API key to {key}")
                config["Settings"]["apikey"] = key
                config_handler.save_config(config, config_path)

                openai.api_key = key
            elif command == "/model":
                model = args[0]
                print(Fore.LIGHTBLACK_EX + f"Setting model to {model}")
                config["Settings"]["model"] = model
                config_handler.save_config(config, config_path)
            elif command == "/project":
                project_path_str = args[0]

                project_path = Path(project_path_str).resolve()
                if not project_path.is_dir():
                    print(Fore.RED + "Invalid folder path. Please check the folder path and try again.")
                    continue

                config["Settings"]["project_path"] = str(project_path)
                config_handler.save_config(config, config_path)
                aiscope_patterns = load_aiscope(project_path)
                project_files = load_project_files(project_path, aiscope_patterns)
                system_prompt = {"role": "system", "content": f"{initial_system_prompt}\n\nCurrent files in the project:\n"}

                file_start_tag = f"START_ASSISTANT_FILE_{rand_code_block_id}:"
                file_end_tag = f"END_ASSISTANT_FILE_{rand_code_block_id}"
                print(Fore.LIGHTBLACK_EX + "Loaded files:")
                for file_item in project_files:
                    print(Fore.LIGHTBLACK_EX + f"  {file_item['filename']}")
                    system_prompt["content"] += f"START_USER_FILE_{rand_code_block_id}:{file_item['filename']}\n"
                    system_prompt["content"] += file_item['content'] + "\n"
                    system_prompt["content"] += f"END_USER_FILE_{rand_code_block_id}:{file_item['filename']}\n\n"

                messages.append(system_prompt)
                print(Fore.LIGHTBLACK_EX + f"Project folder set to {project_path}")
            elif user_input.lower() == "/undo":
                if messages:
                    messages.pop()
                    print(Fore.LIGHTBLACK_EX + "Last prompt removed")
                else:
                    print(Fore.LIGHTBLACK_EX + "No prompt to undo")
            elif user_input.lower() == "/forget":
                messages = []
                print(Fore.LIGHTBLACK_EX + "Conversation cleared")
            elif user_input.lower() == "/help":
                display_help()
            elif user_input.lower() == "/view":
                print(Fore.MAGENTA + "Conversation:")
                for m in messages:
                    if m["role"] == "user":
                        print(f"{Fore.BLUE}You:       {Fore.RESET}{m['content']}")
                    elif m["role"] == "assistant":
                        print(f"{Fore.GREEN}Assistant: {Fore.RESET}{m['content']}")
                    elif m["role"] == "system":
                        print(f"{Fore.MAGENTA}System: {Fore.RESET}{m['content']}")
            else:
                print(Fore.RED + f"Unknown command: {command}")
            continue

        messages.append({"role": "user", "content": user_input})

        start_time = time.time()

        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                temperature=0.5,
                stream=True
            )
        
        except openai.error.AuthenticationError:
            print(Fore.RED + "Error: Invalid API key, please use /apikey to set a valid API key.")
            continue
        except Exception as e:
            print(Fore.RED + f"Error: {repr(e)}")
            continue

        collected_chunks = []
        collected_messages = []

        buffer = ""

        sys.stdout.write(Fore.GREEN + Style.BRIGHT + "Assistant > " + Style.RESET_ALL)
        sys.stdout.write(Fore.CYAN)
        try:
            for chunk in response:
                chunk_time = time.time() - start_time
                collected_chunks.append(chunk)
                chunk_message = chunk["choices"][0]["delta"]
                collected_messages.append(chunk_message)
                buffer += chunk_message.get("content", "")

                sys.stdout.write(chunk_message.get("content", "") + Style.RESET_ALL)
                sys.stdout.flush()
            sys.stdout.write("\n")
        except KeyboardInterrupt:
            messages.pop()
            print(Fore.RED + "\nPrompt interrupted by the user.")
            continue

        assistant_message = {"role": "assistant", "content": buffer}

        file_start_tag = f"START_ASSISTANT_FILE_{rand_code_block_id}:"
        file_end_tag = f"END_ASSISTANT_FILE_{rand_code_block_id}"

        output_files = []
        current_file = None
        for line in buffer.splitlines():
            if line.startswith(file_start_tag):
                filepath = line[len(file_start_tag):].strip()
                current_file = {"filepath": filepath, "content": ""}
            elif line.startswith(file_end_tag):
                if current_file is not None:
                    output_files.append(current_file)
                    current_file = None
            else:
                if current_file is not None:
                    current_file["content"] += line + "\n"

        for output_file in output_files:
            write_output_file(project_path, output_file['filepath'], output_file['content'])

        messages.append(assistant_message)

except KeyboardInterrupt:
    print(Fore.RED + "\nThank you for using the AI code assistant. Have a great day!")
