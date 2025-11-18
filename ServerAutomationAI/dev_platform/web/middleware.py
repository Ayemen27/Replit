"""
Security Middleware: Rate Limiting & CSRF Protection
"""
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Dict, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple in-memory rate limiting middleware
    Uses sliding window per IP address
    """
    
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.window_seconds = 60
        self._requests: Dict[str, list] = {}
    
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health check
        if request.url.path == "/api/health":
            return await call_next(request)
        
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Clean old requests and check rate limit
        now = datetime.now()
        
        if client_ip not in self._requests:
            self._requests[client_ip] = []
        
        # Remove requests older than window
        cutoff = now - timedelta(seconds=self.window_seconds)
        self._requests[client_ip] = [
            req_time for req_time in self._requests[client_ip]
            if req_time > cutoff
        ]
        
        # Check if rate limit exceeded
        if len(self._requests[client_ip]) >= self.requests_per_minute:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            raise HTTPException(
                status_code=429,
                detail="Too many requests. Please try again later."
            )
        
        # Add current request
        self._requests[client_ip].append(now)
        
        # Continue with request
        response = await call_next(request)
        
        # Add rate limit headers
        remaining = max(0, self.requests_per_minute - len(self._requests[client_ip]))
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int((now + timedelta(seconds=self.window_seconds)).timestamp()))
        
        return response


class CSRFProtectionMiddleware(BaseHTTPMiddleware):
    """
    CSRF Protection using Double Submit Cookie pattern
    """
    
    def __init__(self, app, csrf_cookie_name: str = "csrf_token"):
        super().__init__(app)
        self.csrf_cookie_name = csrf_cookie_name
        self.csrf_header_name = "X-CSRF-Token"
        # Methods that require CSRF protection
        self.protected_methods = {"POST", "PUT", "PATCH", "DELETE"}
    
    async def dispatch(self, request: Request, call_next):
        # Skip CSRF check for safe methods and specific paths
        if request.method not in self.protected_methods:
            return await call_next(request)
        
        # Skip CSRF check for login endpoint (uses password authentication)
        if request.url.path == "/auth/login":
            return await call_next(request)
        
        # Skip for health check
        if request.url.path == "/api/health":
            return await call_next(request)
        
        # Get CSRF token from cookie and header
        csrf_cookie = request.cookies.get(self.csrf_cookie_name)
        csrf_header = request.headers.get(self.csrf_header_name)
        
        # Validate CSRF tokens match
        if not csrf_cookie or not csrf_header or csrf_cookie != csrf_header:
            logger.warning(f"CSRF validation failed for {request.url.path}")
            raise HTTPException(
                status_code=403,
                detail="CSRF validation failed"
            )
        
        response = await call_next(request)
        return response
