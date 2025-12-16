"""
Field Mapper for Excel Adapter Pattern
Maps legacy Excel field names to modern schema
"""


class FieldMapper:
    """
    Maps Excel column names to Student model fields
    Handles legacy naming conventions
    """

    # Mapping from Excel columns to Student model fields
    FIELD_MAPPINGS = {
        'Student_No': 'id',
        'student_no': 'id',
        'StudentNo': 'id',
        'ID': 'id',
        'Full_Name': 'name',
        'full_name': 'name',
        'FullName': 'name',
        'Name': 'name',
        'name': 'name',
        'Email_Address': 'email',
        'email_address': 'email',
        'Email': 'email',
        'email': 'email',
        'Dept': 'department',
        'dept': 'department',
        'Department': 'department',
        'department': 'department',
        'Year': 'level',
        'year': 'level',
        'Level': 'level',
        'level': 'level',
        'Mobile': 'phone',
        'mobile': 'phone',
        'Phone': 'phone',
        'phone': 'phone',
        'Status': 'is_active',
        'status': 'is_active',
        'Active': 'is_active',
        'active': 'is_active',
        'Reg_Date': 'registration_date',
        'reg_date': 'registration_date',
        'Registration_Date': 'registration_date',
        'registration_date': 'registration_date',
        'RegDate': 'registration_date',
    }

    @staticmethod
    def map_field(excel_field: str) -> str:
        """
        Map Excel field name to Student model field

        Args:
            excel_field: Excel column name

        Returns:
            Mapped field name or original if no mapping found
        """
        return FieldMapper.FIELD_MAPPINGS.get(excel_field, excel_field)

    @staticmethod
    def map_row(excel_row: dict) -> dict:
        """
        Map entire Excel row to Student model fields

        Args:
            excel_row: Dictionary with Excel column names

        Returns:
            Dictionary with mapped field names
        """
        mapped = {}
        for excel_field, value in excel_row.items():
            model_field = FieldMapper.map_field(excel_field)
            mapped[model_field] = value
        return mapped

    @staticmethod
    def get_supported_excel_fields() -> list:
        """Get list of supported Excel field names"""
        return list(FieldMapper.FIELD_MAPPINGS.keys())
