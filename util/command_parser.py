def command_parser(input_string):
    arguments = []
    current_arg = []
    quote_char = None
    escape_next = False

    for char in input_string:
        if escape_next:
            if char in {'"', "'", '\\'}:
                current_arg.append(char)
            else:
                current_arg.append('\\')
                current_arg.append(char)
            escape_next = False
        elif char == '\\':
            escape_next = True
        elif char in {'"', "'"}:
            if quote_char is None:
                quote_char = char
            elif quote_char == char:
                quote_char = None
            else:
                current_arg.append(char)
        elif char.isspace() and quote_char is None:
            if current_arg:
                arguments.append(''.join(current_arg))
                current_arg = []
        else:
            current_arg.append(char)

    if current_arg:
        arguments.append(''.join(current_arg))

    return arguments