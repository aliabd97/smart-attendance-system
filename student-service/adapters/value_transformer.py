"""
Value Transformer for Excel Adapter Pattern
Transforms legacy data values to modern format
"""

from datetime import datetime


class ValueTransformer:
    """
    Transforms Excel values to proper format for Student model
    Handles type conversions and value mappings
    """

    # Department code mappings
    DEPARTMENT_MAPPINGS = {
        'CS': 'Computer Science',
        'cs': 'Computer Science',
        'IT': 'Information Technology',
        'it': 'Information Technology',
        'SE': 'Software Engineering',
        'se': 'Software Engineering',
        'CE': 'Computer Engineering',
        'ce': 'Computer Engineering',
        'IS': 'Information Systems',
        'is': 'Information Systems',
        'AI': 'Artificial Intelligence',
        'ai': 'Artificial Intelligence',
        'DS': 'Data Science',
        'ds': 'Data Science',
    }

    # Status mappings
    STATUS_MAPPINGS = {
        'Active': True,
        'active': True,
        'ACTIVE': True,
        'yes': True,
        'Yes': True,
        'YES': True,
        'true': True,
        'True': True,
        'TRUE': True,
        '1': True,
        1: True,
        'Inactive': False,
        'inactive': False,
        'INACTIVE': False,
        'no': False,
        'No': False,
        'NO': False,
        'false': False,
        'False': False,
        'FALSE': False,
        '0': False,
        0: False,
    }

    @staticmethod
    def transform_department(value: str) -> str:
        """
        Transform department code to full name

        Args:
            value: Department code or name

        Returns:
            Full department name
        """
        if not value:
            return None

        # Check if it's a code
        if value in ValueTransformer.DEPARTMENT_MAPPINGS:
            return ValueTransformer.DEPARTMENT_MAPPINGS[value]

        # Return as-is if already full name
        return str(value).strip()

    @staticmethod
    def transform_level(value) -> int:
        """
        Transform level to integer

        Args:
            value: Level value (str or int)

        Returns:
            Integer level
        """
        if not value:
            return None

        try:
            level = int(value)
            # Validate level is in valid range (1-6 for typical university)
            if 1 <= level <= 6:
                return level
            else:
                print(f"Warning: Invalid level {level}, defaulting to None")
                return None
        except (ValueError, TypeError):
            print(f"Warning: Cannot convert '{value}' to integer level")
            return None

    @staticmethod
    def transform_status(value) -> bool:
        """
        Transform status to boolean

        Args:
            value: Status value (various formats)

        Returns:
            Boolean status
        """
        if value is None:
            return True  # Default to active

        # Check mappings
        if value in ValueTransformer.STATUS_MAPPINGS:
            return ValueTransformer.STATUS_MAPPINGS[value]

        # Default to True if unknown
        return True

    @staticmethod
    def transform_date(value) -> str:
        """
        Transform date to ISO format (YYYY-MM-DD)

        Args:
            value: Date string in various formats

        Returns:
            ISO formatted date string
        """
        if not value:
            return datetime.now().strftime('%Y-%m-%d')

        # If already a string, try to parse it
        if isinstance(value, str):
            formats = [
                '%d/%m/%Y',    # 01/12/2024
                '%m/%d/%Y',    # 12/01/2024
                '%Y-%m-%d',    # 2024-12-01 (already ISO)
                '%d-%m-%Y',    # 01-12-2024
                '%Y/%m/%d',    # 2024/12/01
            ]

            for fmt in formats:
                try:
                    date_obj = datetime.strptime(value, fmt)
                    return date_obj.strftime('%Y-%m-%d')
                except ValueError:
                    continue

            print(f"Warning: Cannot parse date '{value}', using current date")
            return datetime.now().strftime('%Y-%m-%d')

        # If datetime object
        if isinstance(value, datetime):
            return value.strftime('%Y-%m-%d')

        # Default to current date
        return datetime.now().strftime('%Y-%m-%d')

    @staticmethod
    def transform_phone(value) -> str:
        """
        Transform phone number to standard format

        Args:
            value: Phone number

        Returns:
            Cleaned phone number string
        """
        if not value:
            return None

        # Convert to string and remove common separators
        phone = str(value).strip()
        phone = phone.replace('-', '').replace(' ', '').replace('(', '').replace(')', '')

        return phone if phone else None

    @staticmethod
    def transform_email(value: str) -> str:
        """
        Transform email to lowercase

        Args:
            value: Email address

        Returns:
            Lowercase email
        """
        if not value:
            return None

        return str(value).strip().lower()

    @staticmethod
    def transform_row(row: dict) -> dict:
        """
        Transform entire row based on field types

        Args:
            row: Dictionary with field names and values

        Returns:
            Dictionary with transformed values
        """
        transformed = {}

        for field, value in row.items():
            if field == 'department':
                transformed[field] = ValueTransformer.transform_department(value)
            elif field == 'level':
                transformed[field] = ValueTransformer.transform_level(value)
            elif field == 'is_active':
                transformed[field] = ValueTransformer.transform_status(value)
            elif field == 'registration_date':
                transformed[field] = ValueTransformer.transform_date(value)
            elif field == 'phone':
                transformed[field] = ValueTransformer.transform_phone(value)
            elif field == 'email':
                transformed[field] = ValueTransformer.transform_email(value)
            else:
                # Keep as-is for id and name
                transformed[field] = str(value).strip() if value else None

        return transformed
