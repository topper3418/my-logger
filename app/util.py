from app.models import TimeSpan

from datetime import datetime

def get_time_span(request_args: dict) -> TimeSpan|None:
    start_time = request_args.get('start_time')
    end_time = request_args.get('end_time')
    if start_time and end_time:
        start_time = datetime.fromtimestamp(int(start_time)/1000.0)
        end_time = datetime.fromtimestamp(int(end_time)/1000.0)
        return TimeSpan(start_time, end_time)