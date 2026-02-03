"""
Circuit Breaker Pattern Implementation (State Pattern - Manual)
Prevents cascading failures in microservices communication

States:
- CLOSED: Normal operation, requests pass through
- OPEN: Too many failures, requests are rejected immediately
- HALF_OPEN: Testing if the failed service has recovered

This is a CLIENT-SIDE pattern: the calling service protects itself
from a failing downstream service.
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
    Circuit breaker to protect against cascading failures.

    Usage:
        breaker = CircuitBreaker(name="attendance-service", failure_threshold=3, timeout=15)
        result = breaker.call(some_http_function, arg1, arg2)
    """

    def __init__(
        self,
        name: str = "unknown",
        failure_threshold: int = 3,
        timeout: int = 15,
        success_threshold: int = 2
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.success_threshold = success_threshold

        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED

        print(f"[CB:{self.name}] Circuit Breaker initialized - State: CLOSED (threshold={failure_threshold}, timeout={timeout}s)")

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection.
        If the circuit is OPEN, the request is rejected immediately
        without calling the downstream service.
        """
        # Check if circuit is OPEN
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                old_state = self.state.value
                self.state = CircuitState.HALF_OPEN
                print(f"[CB:{self.name}] State: {old_state.upper()} -> HALF_OPEN (timeout expired, testing service...)")
            else:
                remaining = self._time_until_retry()
                print(f"[CB:{self.name}] Request REJECTED - circuit is OPEN (retry in {remaining}s)")
                raise Exception(
                    f"Circuit breaker [{self.name}] is OPEN - service unavailable (retry in {remaining}s)"
                )

        # Try to execute the function
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e

    def _on_success(self):
        """Handle successful call"""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            print(f"[CB:{self.name}] HALF_OPEN test success ({self.success_count}/{self.success_threshold})")

            if self.success_count >= self.success_threshold:
                old_state = self.state.value
                self.state = CircuitState.CLOSED
                self.success_count = 0
                self.failure_count = 0
                print(f"[CB:{self.name}] State: {old_state.upper()} -> CLOSED (service recovered!)")
        else:
            # Reset failure count on success in CLOSED state
            if self.failure_count > 0:
                print(f"[CB:{self.name}] Success - failure count reset to 0")
            self.failure_count = 0

    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()

        if self.state == CircuitState.HALF_OPEN:
            old_state = self.state.value
            self.state = CircuitState.OPEN
            self.success_count = 0
            print(f"[CB:{self.name}] State: {old_state.upper()} -> OPEN (test failed, service still down)")

        elif self.failure_count >= self.failure_threshold:
            old_state = self.state.value
            self.state = CircuitState.OPEN
            print(f"[CB:{self.name}] State: {old_state.upper()} -> OPEN (reason: {self.failure_count} consecutive failures)")
        else:
            print(f"[CB:{self.name}] Failure {self.failure_count}/{self.failure_threshold} - State: CLOSED")

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
        """Manually reset circuit breaker to CLOSED"""
        old_state = self.state.value
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        print(f"[CB:{self.name}] Manual reset: {old_state.upper()} -> CLOSED")

    def get_state(self) -> dict:
        """Get current circuit breaker state as dictionary"""
        return {
            'name': self.name,
            'state': self.state.value,
            'failure_count': self.failure_count,
            'failure_threshold': self.failure_threshold,
            'success_count': self.success_count,
            'timeout_seconds': self.timeout,
            'time_until_retry': self._time_until_retry() if self.state == CircuitState.OPEN else 0,
            'last_failure_time': self.last_failure_time.isoformat() if self.last_failure_time else None
        }
