from app.models import TimeSpan

from datetime import datetime

def get_time_span(request_args: dict) -> TimeSpan|None:
    start_time = request_args.get('start_time')
    end_time = request_args.get('end_time')
    target_date = request_args.get('target_date')
    if start_time and end_time:
        start_time = datetime.fromtimestamp(int(start_time)/1000.0)
        end_time = datetime.fromtimestamp(int(end_time)/1000.0)
        return TimeSpan(start_time, end_time)
    elif target_date:
        # date will come in lik yyyy-mm-dd
        target_date = datetime.strptime(target_date, '%Y-%m-%d')
        start_time = datetime.combine(target_date, datetime.min.time())
        end_time = datetime.combine(target_date, datetime.max.time())
        return TimeSpan(start_time, end_time)


def get_duration_string(time_span: TimeSpan | int) -> str:
    if isinstance(time_span, TimeSpan):
        duration = time_span.duration
    else:
        duration = time_span
        
    return f'{duration // 3600}:{(duration % 3600) // 60}'