"""
Service Validator - Breaking Foreign Keys Pattern
Validates student and course IDs by calling their respective services
"""

from __future__ import annotations
import requests
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from common.circuit_breaker import CircuitBreaker
from common.utils import get_service_timeout


class ServiceValidator:
    """
    Validates entities across microservices
    Implements the Breaking Foreign Keys Pattern
    """

    def __init__(self):
        # Get service URLs from environment or use defaults
        self.student_service_url = os.getenv('STUDENT_SERVICE_URL', 'http://localhost:5001')
        self.course_service_url = os.getenv('COURSE_SERVICE_URL', 'http://localhost:5002')

        # Circuit breakers for each service
        self.student_breaker = CircuitBreaker(failure_threshold=5, timeout=60)
        self.course_breaker = CircuitBreaker(failure_threshold=5, timeout=60)

    def validate_student_exists(self, student_id: str) -> tuple[bool, str]:
        """
        Validate that student exists by calling Student Service

        Args:
            student_id: Student ID to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            def call_student_service():
                url = f"{self.student_service_url}/api/students/{student_id}"
                timeout = get_service_timeout('student-service')
                response = requests.get(url, timeout=timeout)
                return response

            # Use circuit breaker to call service
            response = self.student_breaker.call(call_student_service)

            if response.status_code == 200:
                return True, ""
            elif response.status_code == 404:
                return False, f"Student {student_id} does not exist"
            else:
                return False, f"Student service error: {response.status_code}"

        except Exception as e:
            error_msg = f"Failed to validate student {student_id}: {str(e)}"
            print(f"❌ {error_msg}")
            return False, error_msg

    def validate_course_exists(self, course_id: str) -> tuple[bool, str]:
        """
        Validate that course exists by calling Course Service

        Args:
            course_id: Course ID to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            def call_course_service():
                url = f"{self.course_service_url}/api/courses/{course_id}"
                timeout = get_service_timeout('course-service')
                response = requests.get(url, timeout=timeout)
                return response

            # Use circuit breaker to call service
            response = self.course_breaker.call(call_course_service)

            if response.status_code == 200:
                return True, ""
            elif response.status_code == 404:
                return False, f"Course {course_id} does not exist"
            else:
                return False, f"Course service error: {response.status_code}"

        except Exception as e:
            error_msg = f"Failed to validate course {course_id}: {str(e)}"
            print(f"❌ {error_msg}")
            return False, error_msg

    def validate_enrollment(self, student_id: str, course_id: str) -> tuple[bool, str]:
        """
        Validate that student is enrolled in course

        Args:
            student_id: Student ID
            course_id: Course ID

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            def call_course_service():
                url = f"{self.course_service_url}/api/courses/{course_id}/students"
                timeout = get_service_timeout('course-service')
                response = requests.get(url, timeout=timeout)
                return response

            response = self.course_breaker.call(call_course_service)

            if response.status_code == 200:
                data = response.json()
                enrolled_students = data.get('student_ids', [])

                if student_id in enrolled_students:
                    return True, ""
                else:
                    return False, f"Student {student_id} is not enrolled in course {course_id}"
            else:
                return False, f"Failed to check enrollment: {response.status_code}"

        except Exception as e:
            error_msg = f"Failed to validate enrollment: {str(e)}"
            print(f"❌ {error_msg}")
            # For attendance, we might want to be lenient here
            # Return True but log the warning
            print(f"⚠️ Warning: Could not validate enrollment, proceeding anyway")
            return True, ""

    def validate_before_recording(self, student_id: str, course_id: str,
                                  check_enrollment: bool = False) -> tuple[bool, str]:
        """
        Validate both student and course before recording attendance

        Args:
            student_id: Student ID
            course_id: Course ID
            check_enrollment: Whether to check if student is enrolled

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Validate student exists
        is_valid, error_msg = self.validate_student_exists(student_id)
        if not is_valid:
            return False, error_msg

        # Validate course exists
        is_valid, error_msg = self.validate_course_exists(course_id)
        if not is_valid:
            return False, error_msg

        # Optionally check enrollment
        if check_enrollment:
            is_valid, error_msg = self.validate_enrollment(student_id, course_id)
            if not is_valid:
                return False, error_msg

        return True, "Validation successful"

    def get_circuit_breaker_status(self) -> dict:
        """Get status of circuit breakers"""
        return {
            'student_service': self.student_breaker.get_state(),
            'course_service': self.course_breaker.get_state()
        }

    def reset_circuit_breakers(self):
        """Manually reset circuit breakers"""
        self.student_breaker.reset()
        self.course_breaker.reset()
        print("✅ Circuit breakers reset")
