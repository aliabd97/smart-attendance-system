"""
Bulkhead Pattern Implementation
Isolates resources to prevent cascading failures
Part of Fault Tolerance Patterns
"""

import threading
import time
import queue
from typing import Callable, Any, Optional
from functools import wraps
from dataclasses import dataclass
from enum import Enum


class BulkheadState(Enum):
    """States of bulkhead resource pool"""
    AVAILABLE = "available"
    EXHAUSTED = "exhausted"
    RECOVERING = "recovering"


@dataclass
class BulkheadStats:
    """Statistics for bulkhead monitoring"""
    total_capacity: int
    available_capacity: int
    active_requests: int
    queued_requests: int
    total_accepted: int
    total_rejected: int
    state: BulkheadState


class BulkheadException(Exception):
    """Raised when bulkhead capacity is exceeded"""
    pass


class Bulkhead:
    """
    Bulkhead pattern implementation using semaphore
    Limits concurrent access to a resource pool

    Example:
        bulkhead = Bulkhead(max_concurrent=5, max_queue=10)

        @bulkhead.protect
        def process_request():
            # This will be limited to 5 concurrent executions
            pass
    """

    def __init__(
        self,
        max_concurrent: int = 10,
        max_queue: int = 20,
        timeout: int = 30,
        name: str = "default"
    ):
        """
        Initialize bulkhead

        Args:
            max_concurrent: Maximum concurrent executions allowed
            max_queue: Maximum requests that can wait in queue
            timeout: Maximum time to wait for resource (seconds)
            name: Name of this bulkhead for monitoring
        """
        self.max_concurrent = max_concurrent
        self.max_queue = max_queue
        self.timeout = timeout
        self.name = name

        # Semaphore to limit concurrent access
        self._semaphore = threading.Semaphore(max_concurrent)

        # Queue for waiting requests
        self._queue = queue.Queue(maxsize=max_queue)

        # Statistics
        self._lock = threading.Lock()
        self._active_count = 0
        self._total_accepted = 0
        self._total_rejected = 0

    def protect(self, func: Callable) -> Callable:
        """
        Decorator to protect a function with bulkhead

        Usage:
            @bulkhead.protect
            def my_function():
                pass
        """
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Try to acquire semaphore
            acquired = self._semaphore.acquire(blocking=True, timeout=self.timeout)

            if not acquired:
                # Could not acquire resource within timeout
                with self._lock:
                    self._total_rejected += 1
                raise BulkheadException(
                    f"Bulkhead '{self.name}': Could not acquire resource within {self.timeout}s"
                )

            try:
                # Resource acquired, increment active count
                with self._lock:
                    self._active_count += 1
                    self._total_accepted += 1

                # Execute function
                result = func(*args, **kwargs)
                return result

            finally:
                # Release resource
                with self._lock:
                    self._active_count -= 1
                self._semaphore.release()

        return wrapper

    def execute(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute a function with bulkhead protection (non-decorator version)

        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            Function result

        Raises:
            BulkheadException: If resource cannot be acquired
        """
        protected_func = self.protect(func)
        return protected_func(*args, **kwargs)

    def get_stats(self) -> BulkheadStats:
        """Get current bulkhead statistics"""
        with self._lock:
            available = self.max_concurrent - self._active_count

            # Determine state
            if available == 0:
                state = BulkheadState.EXHAUSTED
            elif available < self.max_concurrent * 0.2:  # Less than 20% available
                state = BulkheadState.RECOVERING
            else:
                state = BulkheadState.AVAILABLE

            return BulkheadStats(
                total_capacity=self.max_concurrent,
                available_capacity=available,
                active_requests=self._active_count,
                queued_requests=self._queue.qsize(),
                total_accepted=self._total_accepted,
                total_rejected=self._total_rejected,
                state=state
            )

    def reset_stats(self):
        """Reset statistics counters"""
        with self._lock:
            self._total_accepted = 0
            self._total_rejected = 0


class BulkheadManager:
    """
    Manages multiple bulkheads for different resource types
    Provides centralized bulkhead configuration and monitoring
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        """Singleton pattern to ensure single instance"""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._bulkheads = {}
            return cls._instance

    def create_bulkhead(
        self,
        name: str,
        max_concurrent: int = 10,
        max_queue: int = 20,
        timeout: int = 30
    ) -> Bulkhead:
        """
        Create or get a named bulkhead

        Args:
            name: Unique name for this bulkhead
            max_concurrent: Maximum concurrent executions
            max_queue: Maximum queue size
            timeout: Timeout in seconds

        Returns:
            Bulkhead instance
        """
        if name not in self._bulkheads:
            self._bulkheads[name] = Bulkhead(
                max_concurrent=max_concurrent,
                max_queue=max_queue,
                timeout=timeout,
                name=name
            )
        return self._bulkheads[name]

    def get_bulkhead(self, name: str) -> Optional[Bulkhead]:
        """Get bulkhead by name"""
        return self._bulkheads.get(name)

    def get_all_stats(self) -> dict:
        """Get statistics for all bulkheads"""
        return {
            name: bulkhead.get_stats()
            for name, bulkhead in self._bulkheads.items()
        }

    def list_bulkheads(self) -> list:
        """List all registered bulkheads"""
        return list(self._bulkheads.keys())


# Pre-configured bulkheads for common use cases
class ServiceBulkheads:
    """Pre-configured bulkheads for different service operations"""

    # Singleton instance
    _manager = BulkheadManager()

    # HTTP Request Bulkhead
    # Limits concurrent HTTP calls to external services
    HTTP_REQUESTS = _manager.create_bulkhead(
        name='http_requests',
        max_concurrent=20,
        max_queue=50,
        timeout=15
    )

    # Database Bulkhead
    # Limits concurrent database connections
    DATABASE = _manager.create_bulkhead(
        name='database',
        max_concurrent=10,
        max_queue=30,
        timeout=10
    )

    # File Processing Bulkhead
    # Limits concurrent file operations (Excel, PDF)
    FILE_PROCESSING = _manager.create_bulkhead(
        name='file_processing',
        max_concurrent=3,
        max_queue=10,
        timeout=120
    )

    # PDF/OMR Processing Bulkhead
    # Limits heavy OMR processing operations
    OMR_PROCESSING = _manager.create_bulkhead(
        name='omr_processing',
        max_concurrent=2,
        max_queue=5,
        timeout=180
    )

    # Report Generation Bulkhead
    # Limits concurrent report generation
    REPORT_GENERATION = _manager.create_bulkhead(
        name='report_generation',
        max_concurrent=5,
        max_queue=15,
        timeout=90
    )

    # RabbitMQ Bulkhead
    # Limits concurrent message publishing
    RABBITMQ = _manager.create_bulkhead(
        name='rabbitmq',
        max_concurrent=15,
        max_queue=40,
        timeout=10
    )


# Convenience decorators
def http_bulkhead(func: Callable) -> Callable:
    """Decorator to protect HTTP requests with bulkhead"""
    return ServiceBulkheads.HTTP_REQUESTS.protect(func)


def database_bulkhead(func: Callable) -> Callable:
    """Decorator to protect database operations with bulkhead"""
    return ServiceBulkheads.DATABASE.protect(func)


def file_processing_bulkhead(func: Callable) -> Callable:
    """Decorator to protect file processing with bulkhead"""
    return ServiceBulkheads.FILE_PROCESSING.protect(func)


def omr_bulkhead(func: Callable) -> Callable:
    """Decorator to protect OMR processing with bulkhead"""
    return ServiceBulkheads.OMR_PROCESSING.protect(func)


def report_bulkhead(func: Callable) -> Callable:
    """Decorator to protect report generation with bulkhead"""
    return ServiceBulkheads.REPORT_GENERATION.protect(func)


# Example usage
if __name__ == '__main__':
    import random

    # Example 1: Using pre-configured bulkhead
    @http_bulkhead
    def call_external_api(api_id: int):
        print(f"Calling API {api_id}...")
        time.sleep(random.uniform(0.5, 2.0))
        print(f"API {api_id} completed")
        return {"api_id": api_id, "status": "success"}

    # Example 2: Custom bulkhead
    custom_bulkhead = Bulkhead(max_concurrent=3, name="custom")

    @custom_bulkhead.protect
    def process_task(task_id: int):
        print(f"Processing task {task_id}...")
        time.sleep(1)
        print(f"Task {task_id} completed")

    # Test concurrent execution
    print("Testing HTTP Bulkhead (max 20 concurrent):")
    threads = []
    for i in range(25):
        thread = threading.Thread(target=call_external_api, args=(i,))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    # Print statistics
    print("\nHTTP Bulkhead Statistics:")
    stats = ServiceBulkheads.HTTP_REQUESTS.get_stats()
    print(f"Total Capacity: {stats.total_capacity}")
    print(f"Available: {stats.available_capacity}")
    print(f"Active Requests: {stats.active_requests}")
    print(f"Total Accepted: {stats.total_accepted}")
    print(f"Total Rejected: {stats.total_rejected}")
    print(f"State: {stats.state.value}")

    print("\nTesting Custom Bulkhead (max 3 concurrent):")
    threads = []
    for i in range(10):
        thread = threading.Thread(target=process_task, args=(i,))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    # Print custom bulkhead stats
    print("\nCustom Bulkhead Statistics:")
    stats = custom_bulkhead.get_stats()
    print(f"Total Capacity: {stats.total_capacity}")
    print(f"Total Accepted: {stats.total_accepted}")
    print(f"Total Rejected: {stats.total_rejected}")

    # List all bulkheads
    print("\nAll registered bulkheads:")
    manager = BulkheadManager()
    for name in manager.list_bulkheads():
        print(f"- {name}")
