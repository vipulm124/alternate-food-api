"""
App wide response handler for standardizing API responses.
This module provides a consistent response format across all API endpoints.
"""

from typing import Dict, Optional

from config import Config
from fastapi.responses import JSONResponse


class Response(JSONResponse):
    """
    Custom response class that extends FastAPI's JSONResponse.
    Provides standardized response format for all API responses.
    """

    def __init__(self, content: Dict, status_code: int) -> None:
        """
        Initialize Response object with content and status code
        Args:
            content: Dictionary containing response data
            status_code: HTTP status code for the response
        """
        super().__init__(content, status_code)

    @staticmethod
    def success(
        *,
        message: str,
        status_code: int = 200,
        body: Optional[Dict] = None,
        cookies: Optional[Dict] = None
    ) -> "Response":
        """
        Create a success response with standardized format.
        Args:
            message: Success message to be included in response.
            status_code: HTTP status code (defaults to 200).
            body: Optional dictionary containing additional response data.
        Returns:
            Response object with success status and formatted content.
        """
        response = Response(
            status_code=status_code,
            content={
                "success": True,
                "message": message,
                "details": body if body else None,
            },
        )
        if cookies:
            for key, value in cookies.items():
                response.set_cookie(
                    key=key,
                    value=value,
                    httponly=True,
                    secure=(Config.ENV == "production"),
                    domain=(
                        Config.PROJECT_DOMAIN_SUFFIX
                        if (Config.ENV == "production")
                        else None
                    ),
                    samesite="lax" if config.ENV != "production" else "strict",
                    path="/",
                )
        return response

    @staticmethod
    def error(*, status_code: int, message: str) -> "Response":
        """
        Create a error response with standardized format.
        Args:
            status_code: HTTP status code.
            message: Error message to be included in response.
        Returns:
            Response object with error status and message.
        """
        return Response(
            status_code=status_code,
            content={
                "success": False,
                "message": message,
                "details": None,
            },
        )
