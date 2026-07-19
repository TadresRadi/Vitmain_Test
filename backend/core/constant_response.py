"""
Constant response utilities.
Return same response regardless of outcome to prevent enumeration.
"""
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class ConstantResponse:
    """Generate constant responses that don't reveal user existence."""
    
    # Generic success message
    SUCCESS_MESSAGE = "Operation completed successfully"
    
    # Generic error message (for both user not found and other errors)
    GENERIC_ERROR = "Operation failed. Please try again."
    
    # For password reset - same message whether user exists or not
    PASSWORD_RESET_MESSAGE = (  # nosec B105 - user-facing message, not a credential
        "If an account exists with this email, "
        "a password reset link has been sent to it."
    )
    
    # For email verification - same message whether user exists or not
    EMAIL_VERIFICATION_MESSAGE = (
        "If an account exists with this email, "
        "a verification link has been sent to it."
    )
    
    @staticmethod
    def password_reset_response() -> Dict[str, Any]:
        """
        Return constant response for password reset.
        Used whether user exists or not.
        
        Returns:
            Response dict
        """
        return {
            'message': ConstantResponse.PASSWORD_RESET_MESSAGE,
            'success': True,
        }
    
    @staticmethod
    def email_verification_response() -> Dict[str, Any]:
        """
        Return constant response for email verification.
        
        Returns:
            Response dict
        """
        return {
            'message': ConstantResponse.EMAIL_VERIFICATION_MESSAGE,
            'success': True,
        }
    
    @staticmethod
    def generic_error_response() -> Dict[str, Any]:
        """
        Return constant error response.
        Used for invalid credentials, user not found, etc.
        
        Returns:
            Response dict
        """
        return {
            'error': 'invalid_credentials',
            'message': ConstantResponse.GENERIC_ERROR,
            'success': False,
        }
    
    @staticmethod
    def registration_response(email: str = None) -> Dict[str, Any]:
        """
        Return constant response for registration.
        
        Args:
            email: Optional email (don't include if preventing enumeration)
        
        Returns:
            Response dict
        """
        return {
            'message': 'Registration completed. Please check your email.',
            'success': True,
        }