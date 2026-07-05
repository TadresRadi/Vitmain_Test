"""
Core application module.
Contains shared utilities, base classes, and decorators.
"""
from .exceptions import (
    VitmainAPIException,
    AuthenticationError,
    AuthorizationError,
    ValidationError,
    NotFoundError,
    ConflictError,
    ExternalServiceError,
    RateLimitError,
)
from .services import BaseService, ServiceException
from .response import APIResponse
from .decorators import ratelimit
from .timing_safe import TimingSafeComparer, RandomDelay
from .constant_response import ConstantResponse


__all__ = [
    'VitmainAPIException',
    'AuthenticationError',
    'AuthorizationError',
    'ValidationError',
    'NotFoundError',
    'ConflictError',
    'ExternalServiceError',
    'RateLimitError',
    'BaseService',
    'ServiceException',
    'APIResponse',
    'ratelimit',
    'TimingSafeComparer',
    'RandomDelay',
    'ConstantResponse',
]