"""
Standard response formatting.
"""
from rest_framework.response import Response
from rest_framework import status


class APIResponse:
    """Standard API response wrapper."""
    
    @staticmethod
    def success(data=None, message="Success", status_code=status.HTTP_200_OK):
        """Return success response."""
        return Response({
            'success': True,
            'message': message,
            'data': data,
        }, status=status_code)
    
    @staticmethod
    def error(error_code, message, status_code=status.HTTP_400_BAD_REQUEST):
        """Return error response."""
        return Response({
            'success': False,
            'error': error_code,
            'message': message,
        }, status=status_code)
    
    @staticmethod
    def paginated(queryset, serializer_class, request, page_size=20):
        """Return paginated response."""
        from rest_framework.pagination import PageNumberPagination
        
        paginator = PageNumberPagination()
        paginator.page_size = page_size
        page = paginator.paginate_queryset(queryset, request)
        
        if page is not None:
            serializer = serializer_class(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        serializer = serializer_class(queryset, many=True)
        return Response(serializer.data)