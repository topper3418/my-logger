
class LogType:
    def __init__(self, name: str, render: bool = False):
        self.name = name
        self.render = render

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


default_log_types = [
    LogType('thought', render=True),
    LogType('question', render=True),
    LogType('task', render=True),
    LogType('error', render=False),
    LogType('complete', render=False),
    LogType('distraction', render=True),
    LogType('promote', render=False),
    LogType('import', render=False)
]


def get_log_type(name: str) -> LogType:
    for log_type in default_log_types:
        if log_type.name == name:
            return log_type
    raise ValueError(f'Log type {name} not found in default_log_types.')

