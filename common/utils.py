"""
Common utility functions used across services
"""

import os
import hashlib
from datetime import datetime
from functools import wraps
import signal
from typing import Any


class TimeoutError(Exception):
    """Custom timeout exception"""
    pass


def timeout_handler(signum, frame):
    """Signal handler for timeout"""
    raise TimeoutError("Operation timed out")


def with_timeout(seconds: int):
    """
    Decorator to add timeout to function

    Args:
        seconds: Timeout in seconds

    Example:
        @with_timeout(5)
        def slow_function():
            time.sleep(10)  # Will raise TimeoutError after 5 seconds
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Only works on Unix-like systems
            if os.name != 'nt':  # Not Windows
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(seconds)

                try:
                    result = func(*args, **kwargs)
                finally:
                    signal.alarm(0)  # Cancel alarm

                return result
            else:
                # On Windows, just execute without timeout
                return func(*args, **kwargs)

        return wrapper
    return decorator


def generate_id(prefix: str, *args) -> str:
    """
    Generate unique ID using hash

    Args:
        prefix: Prefix for the ID
        *args: Values to hash

    Returns:
        Unique ID string
    """
    data = ':'.join(str(arg) for arg in args)
    hash_value = hashlib.sha256(data.encode()).hexdigest()[:12]
    return f"{prefix}_{hash_value}"


def current_timestamp() -> str:
    """
    Get current timestamp in ISO format

    Returns:
        ISO formatted timestamp string
    """
    return datetime.now().isoformat()


def parse_date(date_string: str) -> datetime:
    """
    Parse date string in various formats

    Args:
        date_string: Date string

    Returns:
        datetime object
    """
    formats = [
        '%Y-%m-%d',
        '%d/%m/%Y',
        '%m/%d/%Y',
        '%Y-%m-%d %H:%M:%S',
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_string, fmt)
        except ValueError:
            continue

    raise ValueError(f"Unable to parse date: {date_string}")


def format_date(date_obj: datetime, format: str = '%Y-%m-%d') -> str:
    """
    Format datetime object to string

    Args:
        date_obj: datetime object
        format: Output format

    Returns:
        Formatted date string
    """
    return date_obj.strftime(format)


def validate_required_fields(data: dict, required_fields: list) -> tuple[bool, str]:
    """
    Validate that required fields are present in data

    Args:
        data: Dictionary to validate
        required_fields: List of required field names

    Returns:
        Tuple of (is_valid, error_message)
    """
    missing_fields = [field for field in required_fields if field not in data or not data[field]]

    if missing_fields:
        return False, f"Missing required fields: {', '.join(missing_fields)}"

    return True, ""


def safe_get(dictionary: dict, key: str, default: Any = None) -> Any:
    """
    Safely get value from dictionary

    Args:
        dictionary: Dictionary to get value from
        key: Key to look up
        default: Default value if key not found

    Returns:
        Value or default
    """
    return dictionary.get(key, default)


# Service timeout configurations
SERVICE_TIMEOUTS = {
    'student-service': 3,      # 3 seconds
    'course-service': 3,       # 3 seconds
    'bubble-sheet': 5,         # 5 seconds
    'pdf-processing': 120,     # 2 minutes
    'attendance': 5,           # 5 seconds
    'reporting': 30,           # 30 seconds
    'auth': 3,                 # 3 seconds
}


def get_service_timeout(service_name: str) -> int:
    """
    Get configured timeout for a service

    Args:
        service_name: Name of the service

    Returns:
        Timeout in seconds
    """
    return SERVICE_TIMEOUTS.get(service_name, 10)  # Default 10 seconds
