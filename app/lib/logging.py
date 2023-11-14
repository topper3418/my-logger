import logging
import time
from functools import wraps

import os


# Function to create or get a logger based on the function name
def get_function_logger(func_name, log_file):
    logger = logging.getLogger(func_name)
    logger.setLevel(logging.INFO)

    # Check if the logger already has handlers
    if not logger.handlers:
        fh = logging.FileHandler(log_file)
        fh.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    return logger

# Decorator function to log runtime
def log_runtime(log_file):
    log_path = os.path.join('logs', log_file)
    if not os.path.exists('logs'):
        os.makedirs('logs')
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_function_logger(func.__name__, log_path)
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            runtime_ms = (end_time - start_time) * 1000
            logger.info(f"Function {func.__name__} took {runtime_ms:.2f} ms to complete")
            return result
        return wrapper
    return decorator