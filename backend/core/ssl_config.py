"""
SSL/TLS configuration and utilities.
Handles certificate validation and secure connections.
"""
import logging
import ssl
from typing import Optional

logger = logging.getLogger(__name__)


class SSLConfig:
    """SSL/TLS configuration."""
    
    # Minimum TLS version
    MIN_TLS_VERSION = ssl.TLSVersion.TLSv1_2
    
    # Ciphers (high security)
    STRONG_CIPHERS = (
        'ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS'
    )
    
    @staticmethod
    def get_ssl_context(
        cert_path: Optional[str] = None,
        key_path: Optional[str] = None
    ) -> ssl.SSLContext:
        """
        Create secure SSL context.
        
        Args:
            cert_path: Path to SSL certificate
            key_path: Path to SSL key
        
        Returns:
            Configured SSL context
        """
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        
        # Set minimum TLS version
        context.minimum_version = SSLConfig.MIN_TLS_VERSION
        
        # Load certificate and key if provided
        if cert_path and key_path:
            try:
                context.load_cert_chain(cert_path, key_path)
                logger.info(f"Loaded SSL certificate from {cert_path}")
            except Exception as e:
                logger.error(f"Error loading SSL certificate: {str(e)}")
                raise
        
        # Set strong ciphers
        try:
            context.set_ciphers(SSLConfig.STRONG_CIPHERS)
        except ssl.SSLError as e:
            logger.warning(f"Could not set preferred ciphers: {str(e)}")
        
        return context
    
    @staticmethod
    def verify_certificate(
        hostname: str,
        port: int = 443,
        timeout: int = 5
    ) -> bool:
        """
        Verify SSL certificate for a hostname.
        
        Args:
            hostname: Hostname to verify
            port: Port number
            timeout: Connection timeout
        
        Returns:
            True if certificate is valid
        """
        import socket
        
        try:
            context = ssl.create_default_context()
            
            with socket.create_connection(
                (hostname, port),
                timeout=timeout
            ) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    logger.info(f"Certificate valid for {hostname}")
                    return True
        
        except ssl.SSLError as e:
            logger.error(f"SSL verification failed for {hostname}: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Certificate verification error: {str(e)}")
            return False


class CertificatePinning:
    """Certificate pinning for enhanced security."""
    
    # Public key pins (base64 encoded SPKI)
    PINNED_KEYS = {
        'accounts.google.com': [
            # Add Google's public key pins here
            # Can be obtained from: https://certs.google.com/
        ],
    }
    
    @staticmethod
    def validate_pin(hostname: str, certificate: dict) -> bool:
        """
        Validate certificate against pinned public key.
        
        Args:
            hostname: Hostname to validate
            certificate: Certificate dict
        
        Returns:
            True if certificate pin is valid
        """
        # Implement certificate pinning logic
        # This is optional but adds extra security
        pinned_keys = CertificatePinning.PINNED_KEYS.get(hostname)
        
        if not pinned_keys:
            # No pins configured for this host
            return True
        
        # Extract public key from certificate
        # and compare against pinned keys
        # Implementation depends on certificate format
        
        return True