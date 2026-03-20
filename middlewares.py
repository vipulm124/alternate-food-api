"""
This module defines all custom middlewares for the application.
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from response import Response
from supabase_handler import validate_token

EXCLUDED_PATHS = [ "/docs",
    "/redocs",
    "/openapi.json",'/login' ,'/test']

class CustomAuthMiddleware(BaseHTTPMiddleware):
    """
    Custom middleware to hanlde authorization.
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> JSONResponse:
        """
        Validate the token in the request header and handle exceptions.
        If the token is not expired, proceed with the request.
        If not, try to get a new token.
        """

        url_path = request.url.path
        if any(url_path.startswith(p) for p in EXCLUDED_PATHS):
            return await call_next(request)
        auth_header = request.headers.get("Authorization")
        
        if not auth_header or not auth_header.startswith("Bearer "):
            return Response.error(
                status_code=status.HTTP_401_UNAUTHORIZED, message="Token missing."
            )
        
        access_token = auth_header.split(" ")[1]
        is_valid_token = await validate_token(access_token)
        if is_valid_token:
            response = await call_next(request)
            return response
        
        return Response.error(
                status_code=status.HTTP_401_UNAUTHORIZED, message="Token missing."
            )
