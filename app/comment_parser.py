from app.db_funcs import get_log_type, get_log_types

from typing import Tuple, List
from dataclasses import dataclass

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
    if command in get_log_types():
        return 'log_type'

@dataclass
class Comment:
    comment: str
    log_type_id: int = None
    parent_id: int = None
    state_command: bool = False

    
def parse_comment(comment: str) -> Comment:
    """strips the comment of any special commands"""
    commands, comment = strip_submission(comment)
    # verify the commands are valid
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
    # set variables from the commands
    parent_id = None
    log_type_id = None
    for command in commands:
        # if theres a number, it's a parent id
        if get_command_type(command) == 'parent_id':
            parent_id = int(command)
        elif get_command_type(command) == 'log_type':
            log_type_id = get_log_type(command).id
    # state command is for submissions that are only parent id's
    state_command = parent_id and not (comment and log_type_id) 

    return Comment(comment, log_type_id, parent_id, state_command)
