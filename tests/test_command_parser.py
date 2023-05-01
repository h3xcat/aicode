import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from util.command_parser import command_parser

def test_command_parser():
    test_cases = [
        {
            'input': '''arg1 "arg 2 with spaces" 'arg 3 with spaces' "arg 4 with \\"quotes\\"" 'arg 5 with \\'quotes\\'' arg\\6''',
            'expected': ['arg1', 'arg 2 with spaces', 'arg 3 with spaces', 'arg 4 with "quotes"', "arg 5 with 'quotes'", 'arg\\6']
        },
        {
            'input': 'arg1 arg2 arg3',
            'expected': ['arg1', 'arg2', 'arg3']
        },
        {
            'input': 'arg1\targ2\targ3',
            'expected': ['arg1', 'arg2', 'arg3']
        },
        {
            'input': 'arg1   arg2   arg3',
            'expected': ['arg1', 'arg2', 'arg3']
        },
        {
            'input': '"arg with \\"double quotes\\"" \'arg with single quotes\'',
            'expected': ['arg with "double quotes"', "arg with single quotes"]
        },
        {
            'input': 'arg\\1 arg\\2 arg\\3',
            'expected': ['arg\\1', 'arg\\2', 'arg\\3']
        },
        {
            'input': '',
            'expected': []
        },
        {
            'input': '   ',
            'expected': []
        },
    ]

    for test_case in test_cases:
        input_string = test_case['input']
        expected_output = test_case['expected']
        result = command_parser(input_string)
        assert result == expected_output, f"Expected {expected_output} but got {result} for input {input_string}"
