"""
Timeout Utilities
Provides timeout decorators and timeout management for service calls
Part of Fault Tolerance Patterns
"""

import signal
import functools
import time
from typing import Callable, Any, Optional
import threading


class TimeoutError(Exception):
    """Raised when a function execution exceeds the timeout"""
    pass


class TimeoutManager:
    """
    Manages timeout configurations for different types of operations
    Provides default timeouts and allows custom overrides
    """

    # Default timeout values (in seconds)
    DEFAULT_TIMEOUTS = {
        'http_request': 10,           # HTTP API calls
        'database_query': 5,           # Database operations
        'file_operation': 30,          # File I/O operations
        'external_service': 15,        # External service calls
        'rabbitmq_publish': 5,         # Message queue operations
        'rabbitmq_consume': 60,        # Message consumption
        'excel_processing': 120,       # Excel file processing
        'pdf_processing': 180,         # PDF/OMR processing
        'report_generation': 90,       # Report generation
    }

    @classmethod
    def get_timeout(cls, operation_type: str) -> int:
        """
        Get timeout for a specific operation type

        Args:
            operation_type: Type of operation (e.g., 'http_request')

        Returns:
            Timeout in seconds
        """
        return cls.DEFAULT_TIMEOUTS.get(operation_type, 30)  # Default 30s

    @classmethod
    def set_timeout(cls, operation_type: str, timeout: int):
        """
        Set custom timeout for an operation type

        Args:
            operation_type: Type of operation
            timeout: Timeout in seconds
        """
        cls.DEFAULT_TIMEOUTS[operation_type] = timeout


def timeout(seconds: Optional[int] = None, operation_type: Optional[str] = None):
    """
    Decorator to add timeout to a function

    Args:
        seconds: Timeout in seconds (overrides operation_type)
        operation_type: Type of operation (uses predefined timeout)

    Usage:
        @timeout(seconds=10)
        def my_function():
            pass

        @timeout(operation_type='http_request')
        def call_external_api():
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Determine timeout duration
            timeout_duration = seconds
            if timeout_duration is None and operation_type:
                timeout_duration = TimeoutManager.get_timeout(operation_type)
            if timeout_duration is None:
                timeout_duration = 30  # Default fallback

            # Create result container
            result = [None]
            exception = [None]

            def target():
                try:
                    result[0] = func(*args, **kwargs)
                except Exception as e:
                    exception[0] = e

            # Run function in thread with timeout
            thread = threading.Thread(target=target)
            thread.daemon = True
            thread.start()
            thread.join(timeout_duration)

            # Check if timeout occurred
            if thread.is_alive():
                raise TimeoutError(
                    f"Function '{func.__name__}' exceeded timeout of {timeout_duration}s"
                )

            # Check if exception occurred
            if exception[0]:
                raise exception[0]

            return result[0]

        return wrapper
    return decorator


def timeout_with_fallback(
    seconds: Optional[int] = None,
    operation_type: Optional[str] = None,
    fallback_value: Any = None
):
    """
    Decorator to add timeout with fallback value instead of raising exception

    Args:
        seconds: Timeout in seconds
        operation_type: Type of operation
        fallback_value: Value to return on timeout

    Usage:
        @timeout_with_fallback(seconds=5, fallback_value={'error': 'timeout'})
        def risky_operation():
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                # Use timeout decorator
                @timeout(seconds=seconds, operation_type=operation_type)
                def timed_func():
                    return func(*args, **kwargs)

                return timed_func()
            except TimeoutError:
                # Return fallback instead of raising
                return fallback_value

        return wrapper
    return decorator


def timeout_with_retry(
    seconds: Optional[int] = None,
    operation_type: Optional[str] = None,
    max_retries: int = 3,
    retry_delay: int = 1
):
    """
    Decorator to add timeout with automatic retry on timeout

    Args:
        seconds: Timeout in seconds
        operation_type: Type of operation
        max_retries: Maximum number of retry attempts
        retry_delay: Delay between retries in seconds

    Usage:
        @timeout_with_retry(seconds=5, max_retries=3)
        def unstable_operation():
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    # Use timeout decorator
                    @timeout(seconds=seconds, operation_type=operation_type)
                    def timed_func():
                        return func(*args, **kwargs)

                    return timed_func()

                except TimeoutError as e:
                    last_exception = e
                    if attempt < max_retries:
                        time.sleep(retry_delay)
                        continue
                    else:
                        raise TimeoutError(
                            f"Function '{func.__name__}' timed out after {max_retries + 1} attempts"
                        ) from last_exception

            return None

        return wrapper
    return decorator


class TimeoutContext:
    """
    Context manager for timeout operations

    Usage:
        with TimeoutContext(seconds=10):
            # Code that should timeout after 10 seconds
            slow_operation()
    """

    def __init__(self, seconds: int):
        self.seconds = seconds
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed = time.time() - self.start_time
        if elapsed > self.seconds:
            raise TimeoutError(f"Operation exceeded timeout of {self.seconds}s")
        return False

    def check_timeout(self):
        """Check if timeout has been exceeded"""
        if self.start_time:
            elapsed = time.time() - self.start_time
            if elapsed > self.seconds:
                raise TimeoutError(f"Operation exceeded timeout of {self.seconds}s")


# Service-specific timeout decorators for convenience
def http_timeout(seconds: Optional[int] = None):
    """Timeout decorator specifically for HTTP requests"""
    return timeout(seconds=seconds, operation_type='http_request')


def db_timeout(seconds: Optional[int] = None):
    """Timeout decorator specifically for database operations"""
    return timeout(seconds=seconds, operation_type='database_query')


def file_timeout(seconds: Optional[int] = None):
    """Timeout decorator specifically for file operations"""
    return timeout(seconds=seconds, operation_type='file_operation')


def external_service_timeout(seconds: Optional[int] = None):
    """Timeout decorator specifically for external service calls"""
    return timeout(seconds=seconds, operation_type='external_service')


# Example usage
if __name__ == '__main__':
    # Example 1: Basic timeout
    @timeout(seconds=5)
    def slow_function():
        import time
        time.sleep(10)
        return "Done"

    # Example 2: Timeout with operation type
    @timeout(operation_type='http_request')
    def call_api():
        import time
        time.sleep(2)
        return {"status": "success"}

    # Example 3: Timeout with fallback
    @timeout_with_fallback(seconds=3, fallback_value={'error': 'timeout'})
    def risky_function():
        import time
        time.sleep(5)
        return {"data": "important"}

    # Example 4: Timeout with retry
    @timeout_with_retry(seconds=2, max_retries=3, retry_delay=1)
    def unstable_function():
        import time
        time.sleep(1)
        return "Success"

    # Test examples
    try:
        print("Testing timeout_with_fallback:")
        result = risky_function()
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error: {e}")

    try:
        print("\nTesting timeout_with_retry:")
        result = unstable_function()
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error: {e}")

    try:
        print("\nTesting http_timeout:")
        result = call_api()
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error: {e}")
