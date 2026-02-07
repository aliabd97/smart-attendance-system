"""
Circuit Breaker using pybreaker library.

Comparison with manual implementation (circuit_breaker.py):
- Manual: Full control over state transitions, logging, and behavior. More code to maintain.
- Library: Quick setup, reliable, well-tested. Less control over internal details.

Both implement the same 3 states: CLOSED -> OPEN -> HALF_OPEN -> CLOSED
"""

import pybreaker
from datetime import datetime


class LibraryCircuitBreaker:
    """
    Circuit Breaker using pybreaker library.
    Same concept as the manual implementation, but using a proven library.
    """

    def __init__(self, name="unknown", failure_threshold=3, timeout=15):
        self.name = name
        # Logs buffer for Dashboard (max 100 entries)
        self.logs = []

        # Create a listener to log state changes (pass self for logging)
        self.listener = CircuitBreakerLogger(name, self)

        self.breaker = pybreaker.CircuitBreaker(
            fail_max=failure_threshold,
            reset_timeout=timeout,
            listeners=[self.listener],
            name=name
        )

        self._log(f"Library Circuit Breaker initialized (pybreaker) - threshold={failure_threshold}, timeout={timeout}s", "info")

    def _log(self, message: str, log_type: str = "info"):
        """Log message to both console and buffer"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        state = self.get_state()['state'] if hasattr(self, 'breaker') else 'closed'
        full_message = f"[LIB-CB:{self.name}] {message}"

        # Print to console
        print(full_message)

        # Add to logs buffer
        self.logs.append({
            'timestamp': timestamp,
            'type': log_type,
            'message': f"[LIBRARY] {message}",
            'state': state
        })

        # Keep only last 100 logs
        if len(self.logs) > 100:
            self.logs = self.logs[-100:]

    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        try:
            return self.breaker.call(func, *args, **kwargs)
        except pybreaker.CircuitBreakerError:
            self._log("Request REJECTED - circuit is OPEN", "error")
            raise Exception(f"Library circuit breaker [{self.name}] is OPEN - service unavailable")

    def get_state(self):
        """Get current state"""
        state_map = {
            'closed': 'closed',
            'open': 'open',
            'half-open': 'half_open'
        }
        current = str(self.breaker.current_state)
        return {
            'name': self.name,
            'state': state_map.get(current, current),
            'fail_counter': self.breaker.fail_counter,
            'implementation': 'pybreaker library'
        }

    def reset(self):
        """Reset to closed state"""
        self.breaker.close()
        self._log("Manual reset -> CLOSED", "info")

    def get_logs(self) -> list:
        """Get accumulated logs"""
        return self.logs.copy()

    def clear_logs(self):
        """Clear logs buffer"""
        self.logs = []


class CircuitBreakerLogger(pybreaker.CircuitBreakerListener):
    """Logs circuit breaker state changes"""

    def __init__(self, name, parent):
        self.name = name
        self.parent = parent  # Reference to LibraryCircuitBreaker for logging

    def state_change(self, cb, old_state, new_state):
        log_type = "warning" if new_state.name.upper() == "OPEN" else "info"
        self.parent._log(f"State: {old_state.name.upper()} -> {new_state.name.upper()}", log_type)

    def failure(self, cb, exc):
        self.parent._log(f"Failure recorded ({cb.fail_counter}/{cb.fail_max})", "warning")

    def success(self, cb):
        self.parent._log("Success recorded", "success")
