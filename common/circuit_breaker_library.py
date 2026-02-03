"""
Circuit Breaker using pybreaker library.

Comparison with manual implementation (circuit_breaker.py):
- Manual: Full control over state transitions, logging, and behavior. More code to maintain.
- Library: Quick setup, reliable, well-tested. Less control over internal details.

Both implement the same 3 states: CLOSED -> OPEN -> HALF_OPEN -> CLOSED
"""

import pybreaker


class LibraryCircuitBreaker:
    """
    Circuit Breaker using pybreaker library.
    Same concept as the manual implementation, but using a proven library.
    """

    def __init__(self, name="unknown", failure_threshold=3, timeout=15):
        # Create a listener to log state changes
        self.listener = CircuitBreakerLogger(name)

        self.breaker = pybreaker.CircuitBreaker(
            fail_max=failure_threshold,
            reset_timeout=timeout,
            listeners=[self.listener],
            name=name
        )
        self.name = name
        print(f"[LIB-CB:{name}] Library Circuit Breaker initialized (pybreaker) - threshold={failure_threshold}, timeout={timeout}s")

    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        try:
            return self.breaker.call(func, *args, **kwargs)
        except pybreaker.CircuitBreakerError:
            print(f"[LIB-CB:{self.name}] Request REJECTED - circuit is OPEN")
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
        print(f"[LIB-CB:{self.name}] Manual reset -> CLOSED")


class CircuitBreakerLogger(pybreaker.CircuitBreakerListener):
    """Logs circuit breaker state changes"""

    def __init__(self, name):
        self.name = name

    def state_change(self, cb, old_state, new_state):
        print(f"[LIB-CB:{self.name}] State: {old_state.name.upper()} -> {new_state.name.upper()}")

    def failure(self, cb, exc):
        print(f"[LIB-CB:{self.name}] Failure recorded ({cb.fail_counter}/{cb.fail_max})")

    def success(self, cb):
        print(f"[LIB-CB:{self.name}] Success recorded")
