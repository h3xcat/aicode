# AI Code Assistant

AI Code Assistant is a command-line tool that allows you to interact with OpenAI's GPT model to generate code, answer questions, and assist with your software development projects. It provides an interactive chat interface that helps you get code snippets, suggestions, and explanations for various programming concepts.

**Note:** Most of this readme was generated using aicode.

## Features

- Interactive chat interface with OpenAI's GPT model
- Supports multiple programming languages
- Customizable model and temperature settings
- Project-specific file scoping
- Undo and forget functionality
- Command history and conversation view
- Easy integration with your development workflow

## Installation

1. Clone the repository:

```bash
git clone https://github.com/h3xcat/aicode.git
```

2. Navigate to the project directory:

```bash
cd aicode
```

3. Install the required dependencies:

```bash
pip install -r requirements.txt
```

4. Set up your OpenAI API key:

Create a `settings.ini` file in the project root directory and add your OpenAI API key:

```ini
[Settings]
apikey = your_api_key_here
```

Replace `your_api_key_here` with your actual OpenAI API key.

## Usage

1. Run the `run.py` script:

```bash
python run.py
```

2. Follow the on-screen instructions to interact with the AI Code Assistant.

## Commands

- `/apikey <api_key>`: Set the OpenAI API key
- `/model <model_name>`: Set the GPT model to use (default: gpt-3.5-turbo)
- `/project <folder_path>`: Set the project folder path
- `/undo`: Undo the previous prompt
- `/forget`: Clear the entire conversation
- `/view`: Display the full conversation
- `/help`: Show the help screen
- `/exit`: End the conversation and exit the chat

## Examples

Here are some examples of how AI Code Assistant can help you with your coding tasks:

- Generate a function to calculate the factorial of a number
- Explain the difference between a list and a tuple in Python
- Provide a code snippet to read a CSV file using Pandas
- Help you debug a piece of code or suggest improvements
- Answer questions about programming concepts and best practices

## Contributing

If you have any suggestions, bug reports, or feature requests, feel free to open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.