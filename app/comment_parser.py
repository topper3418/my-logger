from app.db_funcs import get_log_type


class CommentParser:
    """takes in a comment, and makes available the following properties:
    - comment_type (if specified)
    - parent_id (if specified)
    - comment (the comment itself, stripped of special commands)"""
    def __init__(self, comment: str):
        self.comment = comment
        self.log_type_id = None
        self.parent_id = False
        self.state_command = False
        self.parse_comment()
    
    def parse_comment(self):
        """strips the comment of any special commands"""
        comment = self.comment
        commands = []
        while '[' in comment and ']' in comment:
            # get the text between the brackets
            bracket_text = comment[comment.find('[')+1:comment.find(']')]
            commands.append(bracket_text)
            # remove the text between the brackets
            comment = comment.replace(f'[{bracket_text}]', '')
        self.comment = comment.strip()
        # verify the commands are valid
        if len(commands) > 2:
            raise ValueError('Too many commands in comment')
        for command in commands:
            # if theres a number, it's a parent id
            if command.isnumeric():
                if self.parent_id:
                    raise ValueError('Too many parent ids in comment')
                self.parent_id = int(command)
            # if it's empty, and theres no comment, it's a state command to "unfocus"
            elif not command and not self.comment:
                self.state_command = True
            # if its empty and there is a comment, it's an orphaned comment
            elif not command and self.comment:
                self.parent_id = None
            else:
                log_type = get_log_type(command)
                if log_type:
                    if self.log_type_id:
                        raise ValueError('Too many log types in comment')
                    self.log_type_id = log_type.id
                else:
                    raise ValueError(f'Invalid command in comment: {command}')
        if not self.state_command:
            self.state_command = not self.comment and\
                                 not self.log_type_id and\
                                 self.parent_id
