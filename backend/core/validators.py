"""
Input validation utilities.
Comprehensive validators for common fields and custom validations.
"""
import logging
import re
from typing import List

logger = logging.getLogger(__name__)


class ValidatorError(Exception):
    """Custom validation error."""


class InputValidator:
    """Validate and sanitize user input."""
    
    # Regex patterns
    EMAIL_PATTERN = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )
    URL_PATTERN = re.compile(
        r'^https?://[^\s/$.?#].[^\s]*$',
        re.IGNORECASE
    )
    PHONE_PATTERN = re.compile(r'^[\d\s\-\+\(\)]{7,20}$')
    
    # Unsafe characters for XSS
    XSS_PATTERNS = [
        re.compile(r'<script', re.IGNORECASE),
        re.compile(r'javascript:', re.IGNORECASE),
        re.compile(r'onerror=', re.IGNORECASE),
        re.compile(r'onclick=', re.IGNORECASE),
        re.compile(r'onload=', re.IGNORECASE),
    ]
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Validate email format.
        
        Args:
            email: Email string
        
        Returns:
            True if valid
        
        Raises:
            ValidatorError: If invalid
        """
        if not email or not isinstance(email, str):
            raise ValidatorError("Email must be a non-empty string")
        
        email = email.strip().lower()
        
        # Length check
        if len(email) > 254:
            raise ValidatorError("Email too long (max 254 characters)")
        
        # Format check
        if not InputValidator.EMAIL_PATTERN.match(email):
            raise ValidatorError("Invalid email format")
        
        # Prevent disposable emails (optional)
        # Can add check against disposable email domains
        
        return True
    
    @staticmethod
    def validate_password(password: str) -> bool:
        """
        Validate password strength.
        
        Requirements:
        - Minimum 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        - At least one special character
        
        Args:
            password: Password string
        
        Returns:
            True if valid
        
        Raises:
            ValidatorError: If invalid
        """
        if not password or not isinstance(password, str):
            raise ValidatorError("Password must be a non-empty string")
        
        errors = []
        
        if len(password) < 8:
            errors.append("Password must be at least 8 characters")
        
        if not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        
        if not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        
        if not re.search(r'\d', password):
            errors.append("Password must contain at least one digit")
        
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>?/]', password):
            errors.append("Password must contain at least one special character")
        
        if errors:
            raise ValidatorError(" | ".join(errors))
        
        return True
    
    @staticmethod
    def validate_full_name(name: str) -> bool:
        """
        Validate full name.
        
        Requirements:
        - 2-255 characters
        - Only letters, spaces, hyphens, apostrophes
        
        Args:
            name: Full name
        
        Returns:
            True if valid
        
        Raises:
            ValidatorError: If invalid
        """
        if not name or not isinstance(name, str):
            raise ValidatorError("Full name must be a non-empty string")
        
        name = name.strip()
        
        if len(name) < 2:
            raise ValidatorError("Full name must be at least 2 characters")
        
        if len(name) > 255:
            raise ValidatorError("Full name must be 255 characters or less")
        
        if not re.match(r"^[\w\s\-'.]+$", name, re.UNICODE):
            raise ValidatorError(
                "Full name can only contain letters, spaces, hyphens, and apostrophes"
            )
        
        return True
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """
        Validate URL format.
        
        Args:
            url: URL string
        
        Returns:
            True if valid
        
        Raises:
            ValidatorError: If invalid
        """
        if not url or not isinstance(url, str):
            raise ValidatorError("URL must be a non-empty string")
        
        if len(url) > 2048:
            raise ValidatorError("URL too long (max 2048 characters)")
        
        if not InputValidator.URL_PATTERN.match(url):
            raise ValidatorError("Invalid URL format")
        
        return True
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """
        Validate phone number format.
        
        Args:
            phone: Phone number string
        
        Returns:
            True if valid
        
        Raises:
            ValidatorError: If invalid
        """
        if not phone or not isinstance(phone, str):
            raise ValidatorError("Phone number must be a non-empty string")
        
        phone = phone.strip()
        
        if not InputValidator.PHONE_PATTERN.match(phone):
            raise ValidatorError(
                "Invalid phone number format (use digits, spaces, hyphens, +)"
            )
        
        return True
    
    @staticmethod
    def sanitize_string(text: str, max_length: int = 1000) -> str:
        """
        Sanitize string to prevent XSS and injection.
        
        Args:
            text: String to sanitize
            max_length: Maximum allowed length
        
        Returns:
            Sanitized string
        
        Raises:
            ValidatorError: If string contains malicious content
        """
        if not isinstance(text, str):
            return ""
        
        text = text.strip()
        
        # Check length
        if len(text) > max_length:
            raise ValidatorError(f"Text exceeds maximum length of {max_length}")
        
        # Check for XSS patterns
        for pattern in InputValidator.XSS_PATTERNS:
            if pattern.search(text):
                raise ValidatorError("Text contains invalid characters or patterns")
        
        # HTML escape special characters
        html_escape_table = {
            "&": "&amp;",
            '"': "&quot;",
            "'": "&#x27;",
            ">": "&gt;",
            "<": "&lt;",
        }
        
        text = "".join(html_escape_table.get(c, c) for c in text)
        
        return text
    
    @staticmethod
    def validate_uuid(uuid_str: str) -> bool:
        """
        Validate UUID format.
        
        Args:
            uuid_str: UUID string
        
        Returns:
            True if valid
        
        Raises:
            ValidatorError: If invalid
        """
        import uuid
        
        if not uuid_str or not isinstance(uuid_str, str):
            raise ValidatorError("UUID must be a non-empty string")
        
        try:
            uuid.UUID(uuid_str)
            return True
        except ValueError:
            raise ValidatorError("Invalid UUID format")
    
    @staticmethod
    def validate_enum(value: str, allowed_values: List[str]) -> bool:
        """
        Validate value is in allowed list.
        
        Args:
            value: Value to check
            allowed_values: List of allowed values
        
        Returns:
            True if valid
        
        Raises:
            ValidatorError: If not in allowed values
        """
        if value not in allowed_values:
            raise ValidatorError(
                f"Invalid value. Must be one of: {', '.join(allowed_values)}"
            )
        return True
    
    @staticmethod
    def validate_range(value: int, min_val: int, max_val: int) -> bool:
        """
        Validate number is within range.
        
        Args:
            value: Number to validate
            min_val: Minimum value (inclusive)
            max_val: Maximum value (inclusive)
        
        Returns:
            True if valid
        
        Raises:
            ValidatorError: If out of range
        """
        if not isinstance(value, int):
            raise ValidatorError("Value must be an integer")
        
        if not (min_val <= value <= max_val):
            raise ValidatorError(
                f"Value must be between {min_val} and {max_val}"
            )
        
        return True


# Singleton instance
_validator = None


def get_validator() -> InputValidator:
    """Get input validator singleton."""
    global _validator
    if _validator is None:
        _validator = InputValidator()
    return _validator