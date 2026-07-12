"""
Timing-safe utilities to prevent timing attacks.
"""
import logging
import time
import random

logger = logging.getLogger(__name__)


class TimingSafeComparer:
    """Timing-safe string comparison."""
    
    @staticmethod
    def compare(a: str, b: str) -> bool:
        """
        Compare two strings in constant time.
        Prevents timing attacks that reveal information.
        
        Args:
            a: First string
            b: Second string
        
        Returns:
            True if strings are equal
        """
        import hmac
        return hmac.compare_digest(a, b)


class RandomDelay:
    """Add random delays to prevent timing attacks."""
    
    MIN_DELAY = 0.1  # 100ms
    MAX_DELAY = 0.5  # 500ms
    
    @staticmethod
    def add_delay(min_ms: int = 100, max_ms: int = 500) -> None:
        """
        Add random delay to operation.
        Prevents attackers from measuring response time.
        
        Args:
            min_ms: Minimum delay in milliseconds
            max_ms: Maximum delay in milliseconds
        """
        delay_seconds = random.uniform(min_ms / 1000, max_ms / 1000)
        time.sleep(delay_seconds)
    
    @staticmethod
    def add_delay_for_failed_auth(attempt_number: int = 1) -> None:
        """
        Add delay based on failed attempt number.
        Increases delay with each failed attempt.
        
        Args:
            attempt_number: Which attempt this is (1, 2, 3...)
        """
        # Exponential backoff: 100ms, 200ms, 400ms, 800ms, 1600ms
        delay_ms = min(100 * (2 ** (attempt_number - 1)), 1600)
        RandomDelay.add_delay(delay_ms, delay_ms + 100)