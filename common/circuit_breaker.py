"""
Circuit Breaker Pattern Implementation
Prevents cascading failures in microservices communication
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Callable, Any


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"          # Normal operation
    OPEN = "open"              # Failing - reject requests
    HALF_OPEN = "half_open"    # Testing if service recovered


class CircuitBreaker:
    """
    Circuit breaker to protect against cascading failures

    States:
    - CLOSED: Normal operation, requests pass through
    - OPEN: Too many failures, requests fail immediately
    - HALF_OPEN: Testing if service recovered

    Example:
        breaker = CircuitBreaker(failure_threshold=5, timeout=60)
        result = breaker.call(some_function, arg1, arg2)
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: int = 60,
        success_threshold: int = 2
    ):
        """
        Initialize circuit breaker

        Args:
            failure_threshold: Number of failures before opening circuit
            timeout: Seconds to wait before trying again (OPEN -> HALF_OPEN)
            success_threshold: Successes needed in HALF_OPEN to close circuit
        """
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.success_threshold = success_threshold

        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection

        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            Function result

        Raises:
            Exception: If circuit is OPEN or function fails
        """
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                print(f"🔶 Circuit breaker: HALF_OPEN - Testing service")
            else:
                raise Exception(
                    f"Circuit breaker is OPEN - service unavailable "
                    f"(retry in {self._time_until_retry()}s)"
                )

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result

        except Exception as e:
            self._on_failure()
            raise e

    def _on_success(self):
        """Handle successful call"""
        self.failure_count = 0

        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            print(f"🔶 Circuit breaker: HALF_OPEN success ({self.success_count}/{self.success_threshold})")

            if self.success_count >= self.success_threshold:
                self.state = CircuitState.CLOSED
                self.success_count = 0
                print(f"✅ Circuit breaker: CLOSED - Service recovered")

    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()

        if self.state == CircuitState.HALF_OPEN:
            # Fail immediately back to OPEN if testing fails
            self.state = CircuitState.OPEN
            self.success_count = 0
            print(f"❌ Circuit breaker: OPEN - Service still failing")

        elif self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            print(f"❌ Circuit breaker: OPEN - Too many failures ({self.failure_count})")

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to try again"""
        if not self.last_failure_time:
            return False
        return (datetime.now() - self.last_failure_time) > timedelta(seconds=self.timeout)

    def _time_until_retry(self) -> int:
        """Calculate seconds until retry is allowed"""
        if not self.last_failure_time:
            return 0
        elapsed = (datetime.now() - self.last_failure_time).total_seconds()
        return max(0, int(self.timeout - elapsed))

    def reset(self):
        """Manually reset circuit breaker"""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        print("✅ Circuit breaker manually reset")

    def get_state(self) -> dict:
        """Get current circuit breaker state"""
        return {
            'state': self.state.value,
            'failure_count': self.failure_count,
            'success_count': self.success_count,
            'last_failure_time': self.last_failure_time.isoformat() if self.last_failure_time else None
        }
