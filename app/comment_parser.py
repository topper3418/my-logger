from app.models import Comment
from app import default_log_types

from typing import Tuple, List

def strip_submission(submission: str) -> Tuple[List[str], str]:
    """takes in a comment, and returns a list of commands, and the stripped comment"""
    commands = []
    while '[' in submission and ']' in submission:
        # get the text between the brackets
        bracket_text = submission[submission.find('[')+1:submission.find(']')]
        commands.append(bracket_text)
        # remove the text between the brackets
        submission = submission.replace(f'[{bracket_text}]', '')
    return commands, submission.strip()


def get_command_type(command: str) -> str:
    """takes in a command, and returns the type of command it is"""
    if command.isnumeric() or not command:
        return 'parent_id'
    if command in [log_type['log_type'] for log_type in default_log_types]:
        return 'log_type'
    
    
def get_parent_id(parent_id_command: str) -> int:
    if not parent_id_command:
        return 0
    return int(parent_id_command)


def check_commands(commands: List[str]) -> None:
    """takes in a list of commands, and raises an error if there are too many"""
     # currently only 2 commands at a time are supported
    if len(commands) > 2:
        raise ValueError('Too many commands in comment')
    # only one command can be a parent_id
    if len([command for command in commands if get_command_type(command) == 'parent_id']) > 1:
        raise ValueError('Too many parent ids in comment')
    # only one command can be a log_type
    if len([command for command in commands if get_command_type(command) == 'log_type']) > 1:
        raise ValueError('Too many log types in comment')
    # make sure there are no invalid commands
    if any([get_command_type(command) == None for command in commands]):
        raise ValueError('Invalid command in comment')
    

def parse_comment(comment: str) -> Comment:
    """strips the comment of any special commands"""
    commands, comment = strip_submission(comment)
    # verify the commands are valid
    check_commands(commands)
    # set variables from the commands
    parent_id = None
    log_type = None
    for command in commands:
        # if theres a number, it's a parent id
        if get_command_type(command) == 'parent_id':
            parent_id = get_parent_id(command)
        elif get_command_type(command) == 'log_type':
            log_type = command
    # state command is for submissions that are only parent id's
    state_command = parent_id and not comment and not log_type

    return Comment(comment, log_type, parent_id, state_command)
