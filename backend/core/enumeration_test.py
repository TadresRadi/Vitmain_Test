"""
Account enumeration testing utility.
Use ONLY in development to test that enumeration is prevented.
"""
import time
import logging

logger = logging.getLogger(__name__)


class EnumerationTester:
    """Test if application leaks user existence information."""
    
    @staticmethod
    def test_password_reset_timing(api_client, existing_email: str, non_existing_email: str):
        """
        Test if response times differ for existing vs non-existing users.
        
        Args:
            api_client: API test client
            existing_email: Email that exists in system
            non_existing_email: Email that doesn't exist
        
        Returns:
            Dict with timing results
        """
        results = {
            'existing_user': None,
            'non_existing_user': None,
            'timing_difference': None,
        }
        
        # Test existing user
        start = time.time()
        api_client.post('/api/auth/password/reset-request', {
            'email': existing_email
        })
        results['existing_user'] = time.time() - start
        
        # Test non-existing user
        start = time.time()
        api_client.post('/api/auth/password/reset-request', {
            'email': non_existing_email
        })
        results['non_existing_user'] = time.time() - start
        
        # Calculate difference
        results['timing_difference'] = abs(
            results['existing_user'] - results['non_existing_user']
        )
        
        logger.info(f"Enumeration Test Results: {results}")
        
        # If difference is small, enumeration is prevented
        if results['timing_difference'] < 0.2:  # Less than 200ms difference
            logger.info("✓ PASS: Timing difference too small to leak user existence")
            return True
        else:
            logger.warning("✗ FAIL: Timing difference reveals user existence")
            return False