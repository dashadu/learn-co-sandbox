"""
API Client Module
=================

This module provides a robust HTTP API client with features including:
- Automatic retries with exponential backoff
- Request/response logging
- Authentication support (API key, Bearer token, Basic auth)
- Rate limiting
- Response caching
- Timeout handling

Classes:
--------
    APIClient: Main API client for HTTP requests
    APIResponse: Wrapper for HTTP responses
    RateLimiter: Rate limiting implementation

Examples:
    Basic usage:
    >>> client = APIClient(base_url="https://api.example.com")
    >>> response = client.get("/users")
    >>> response.json()
    
    With authentication:
    >>> client = APIClient(
    ...     base_url="https://api.example.com",
    ...     auth_type="bearer",
    ...     auth_token="your-token"
    ... )
"""

import time
import json
import hashlib
from typing import Any, Dict, List, Optional, Union, Tuple
from enum import Enum
from urllib.parse import urljoin, urlencode
from datetime import datetime, timedelta
import logging


class AuthType(Enum):
    """Authentication types supported by the API client."""
    NONE = "none"
    API_KEY = "api_key"
    BEARER = "bearer"
    BASIC = "basic"


class HTTPMethod(Enum):
    """HTTP methods."""
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


class APIResponse:
    """
    Wrapper for HTTP responses.
    
    Provides convenient methods for accessing response data and metadata.
    
    Attributes:
        status_code (int): HTTP status code
        headers (Dict): Response headers
        body (bytes): Raw response body
        elapsed_time (float): Request duration in seconds
        url (str): Request URL
        method (str): HTTP method used
    
    Examples:
        >>> response = APIResponse(200, {"Content-Type": "application/json"}, b'{"key": "value"}')
        >>> response.is_success()
        True
        >>> response.json()
        {'key': 'value'}
    """
    
    def __init__(self, status_code: int, headers: Dict[str, str], 
                 body: bytes, elapsed_time: float = 0, 
                 url: str = "", method: str = ""):
        """
        Initialize APIResponse.
        
        Args:
            status_code: HTTP status code
            headers: Response headers
            body: Response body as bytes
            elapsed_time: Request duration
            url: Request URL
            method: HTTP method
        """
        self.status_code = status_code
        self.headers = headers
        self.body = body
        self.elapsed_time = elapsed_time
        self.url = url
        self.method = method
    
    def json(self) -> Any:
        """
        Parse response body as JSON.
        
        Returns:
            Parsed JSON data
        
        Raises:
            ValueError: If response is not valid JSON
        
        Examples:
            >>> response = APIResponse(200, {}, b'{"name": "John"}')
            >>> response.json()
            {'name': 'John'}
        """
        try:
            return json.loads(self.body.decode('utf-8'))
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            raise ValueError(f"Response is not valid JSON: {e}")
    
    def text(self) -> str:
        """
        Get response body as text.
        
        Returns:
            Response body as string
        
        Examples:
            >>> response = APIResponse(200, {}, b'Hello World')
            >>> response.text()
            'Hello World'
        """
        return self.body.decode('utf-8', errors='replace')
    
    def is_success(self) -> bool:
        """
        Check if request was successful (2xx status code).
        
        Returns:
            True if status code is 2xx
        
        Examples:
            >>> APIResponse(200, {}, b'').is_success()
            True
            >>> APIResponse(404, {}, b'').is_success()
            False
        """
        return 200 <= self.status_code < 300
    
    def is_error(self) -> bool:
        """Check if request resulted in error (4xx or 5xx)."""
        return self.status_code >= 400
    
    def raise_for_status(self) -> None:
        """
        Raise exception if response indicates error.
        
        Raises:
            Exception: If status code indicates error
        
        Examples:
            >>> response = APIResponse(404, {}, b'Not Found')
            >>> response.raise_for_status()
            Traceback (most recent call last):
            ...
            Exception: HTTP 404: Not Found
        """
        if self.is_error():
            raise Exception(f"HTTP {self.status_code}: {self.text()}")


class RateLimiter:
    """
    Rate limiter for API requests.
    
    Implements token bucket algorithm for rate limiting.
    
    Attributes:
        max_requests (int): Maximum requests per period
        period (float): Time period in seconds
        tokens (float): Available tokens
        last_update (float): Last token update timestamp
    
    Examples:
        >>> limiter = RateLimiter(max_requests=10, period=60)  # 10 req/min
        >>> limiter.acquire()  # Returns immediately if tokens available
        >>> limiter.acquire()  # May wait if rate limit reached
    """
    
    def __init__(self, max_requests: int = 100, period: float = 60):
        """
        Initialize RateLimiter.
        
        Args:
            max_requests: Maximum requests per period
            period: Time period in seconds
        """
        self.max_requests = max_requests
        self.period = period
        self.tokens = max_requests
        self.last_update = time.time()
    
    def acquire(self, tokens: int = 1) -> None:
        """
        Acquire tokens, waiting if necessary.
        
        Args:
            tokens: Number of tokens to acquire
        
        Examples:
            >>> limiter = RateLimiter(max_requests=5, period=10)
            >>> for i in range(5):
            ...     limiter.acquire()  # No waiting
            >>> limiter.acquire()  # Will wait
        """
        while tokens > self.tokens:
            self._refill()
            if tokens > self.tokens:
                time.sleep(0.1)
        
        self.tokens -= tokens
    
    def _refill(self) -> None:
        """Refill tokens based on elapsed time."""
        now = time.time()
        elapsed = now - self.last_update
        self.tokens = min(
            self.max_requests,
            self.tokens + (elapsed * self.max_requests / self.period)
        )
        self.last_update = now


class APIClient:
    """
    HTTP API Client with advanced features.
    
    A comprehensive API client supporting authentication, rate limiting,
    caching, retries, and logging.
    
    Attributes:
        base_url (str): Base URL for API endpoints
        timeout (float): Request timeout in seconds
        max_retries (int): Maximum retry attempts
        rate_limiter (RateLimiter): Rate limiting instance
        cache (Dict): Response cache
        session_headers (Dict): Default headers for all requests
    
    Examples:
        Basic client:
        >>> client = APIClient("https://api.example.com")
        >>> response = client.get("/users")
        >>> users = response.json()
        
        With authentication:
        >>> client = APIClient(
        ...     base_url="https://api.example.com",
        ...     auth_type="bearer",
        ...     auth_token="secret-token"
        ... )
        
        With rate limiting:
        >>> client = APIClient(
        ...     base_url="https://api.example.com",
        ...     rate_limit=10,  # 10 requests per minute
        ...     rate_limit_period=60
        ... )
        
        Custom headers:
        >>> client = APIClient("https://api.example.com")
        >>> client.set_header("X-Custom-Header", "value")
    """
    
    def __init__(self, base_url: str, timeout: float = 30.0,
                 max_retries: int = 3, auth_type: str = "none",
                 auth_token: Optional[str] = None,
                 auth_username: Optional[str] = None,
                 auth_password: Optional[str] = None,
                 rate_limit: Optional[int] = None,
                 rate_limit_period: float = 60,
                 enable_cache: bool = False):
        """
        Initialize APIClient.
        
        Args:
            base_url: Base URL for API
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
            auth_type: Authentication type (none, api_key, bearer, basic)
            auth_token: Authentication token (for api_key or bearer)
            auth_username: Username for basic auth
            auth_password: Password for basic auth
            rate_limit: Maximum requests per period
            rate_limit_period: Rate limit period in seconds
            enable_cache: Enable response caching
        
        Raises:
            ValueError: If invalid auth configuration
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        self.session_headers: Dict[str, str] = {
            "User-Agent": "APIClient/1.0",
            "Accept": "application/json"
        }
        
        # Setup authentication
        self._setup_auth(auth_type, auth_token, auth_username, auth_password)
        
        # Setup rate limiting
        self.rate_limiter = None
        if rate_limit:
            self.rate_limiter = RateLimiter(rate_limit, rate_limit_period)
        
        # Setup cache
        self.enable_cache = enable_cache
        self.cache: Dict[str, Tuple[APIResponse, float]] = {}
        self.cache_ttl = 300  # 5 minutes default
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
    
    def _setup_auth(self, auth_type: str, auth_token: Optional[str],
                   auth_username: Optional[str], auth_password: Optional[str]) -> None:
        """Setup authentication headers."""
        if auth_type == "bearer" and auth_token:
            self.session_headers["Authorization"] = f"Bearer {auth_token}"
        elif auth_type == "api_key" and auth_token:
            self.session_headers["X-API-Key"] = auth_token
        elif auth_type == "basic" and auth_username and auth_password:
            import base64
            credentials = base64.b64encode(
                f"{auth_username}:{auth_password}".encode()
            ).decode()
            self.session_headers["Authorization"] = f"Basic {credentials}"
        elif auth_type != "none":
            raise ValueError(f"Invalid auth configuration for type: {auth_type}")
    
    def set_header(self, key: str, value: str) -> None:
        """
        Set a default header for all requests.
        
        Args:
            key: Header name
            value: Header value
        
        Examples:
            >>> client = APIClient("https://api.example.com")
            >>> client.set_header("X-Custom-Header", "value")
        """
        self.session_headers[key] = value
    
    def get(self, endpoint: str, params: Optional[Dict] = None,
            headers: Optional[Dict] = None, use_cache: bool = True) -> APIResponse:
        """
        Perform GET request.
        
        Args:
            endpoint: API endpoint (relative to base_url)
            params: Query parameters
            headers: Additional headers
            use_cache: Use cached response if available
        
        Returns:
            APIResponse object
        
        Examples:
            >>> client = APIClient("https://api.example.com")
            >>> response = client.get("/users", params={"page": 1})
            >>> response.json()
            [{'id': 1, 'name': 'John'}, ...]
        """
        return self._request(HTTPMethod.GET, endpoint, params=params,
                           headers=headers, use_cache=use_cache)
    
    def post(self, endpoint: str, data: Optional[Union[Dict, str]] = None,
             json_data: Optional[Dict] = None, headers: Optional[Dict] = None) -> APIResponse:
        """
        Perform POST request.
        
        Args:
            endpoint: API endpoint
            data: Form data or raw string
            json_data: JSON data (will be serialized)
            headers: Additional headers
        
        Returns:
            APIResponse object
        
        Examples:
            >>> client = APIClient("https://api.example.com")
            >>> response = client.post("/users", json_data={"name": "John"})
            >>> response.status_code
            201
        """
        return self._request(HTTPMethod.POST, endpoint, data=data,
                           json_data=json_data, headers=headers)
    
    def put(self, endpoint: str, data: Optional[Union[Dict, str]] = None,
            json_data: Optional[Dict] = None, headers: Optional[Dict] = None) -> APIResponse:
        """
        Perform PUT request.
        
        Args:
            endpoint: API endpoint
            data: Form data or raw string
            json_data: JSON data
            headers: Additional headers
        
        Returns:
            APIResponse object
        """
        return self._request(HTTPMethod.PUT, endpoint, data=data,
                           json_data=json_data, headers=headers)
    
    def delete(self, endpoint: str, headers: Optional[Dict] = None) -> APIResponse:
        """
        Perform DELETE request.
        
        Args:
            endpoint: API endpoint
            headers: Additional headers
        
        Returns:
            APIResponse object
        
        Examples:
            >>> client = APIClient("https://api.example.com")
            >>> response = client.delete("/users/123")
            >>> response.status_code
            204
        """
        return self._request(HTTPMethod.DELETE, endpoint, headers=headers)
    
    def patch(self, endpoint: str, data: Optional[Union[Dict, str]] = None,
             json_data: Optional[Dict] = None, headers: Optional[Dict] = None) -> APIResponse:
        """
        Perform PATCH request.
        
        Args:
            endpoint: API endpoint
            data: Form data or raw string
            json_data: JSON data
            headers: Additional headers
        
        Returns:
            APIResponse object
        """
        return self._request(HTTPMethod.PATCH, endpoint, data=data,
                           json_data=json_data, headers=headers)
    
    def _request(self, method: HTTPMethod, endpoint: str,
                params: Optional[Dict] = None,
                data: Optional[Union[Dict, str]] = None,
                json_data: Optional[Dict] = None,
                headers: Optional[Dict] = None,
                use_cache: bool = False) -> APIResponse:
        """Internal method to perform HTTP request with retries."""
        # Build URL
        url = urljoin(self.base_url, endpoint)
        if params:
            url += "?" + urlencode(params)
        
        # Check cache
        cache_key = self._get_cache_key(method, url, data, json_data)
        if use_cache and self.enable_cache and method == HTTPMethod.GET:
            cached = self._get_cached_response(cache_key)
            if cached:
                return cached
        
        # Apply rate limiting
        if self.rate_limiter:
            self.rate_limiter.acquire()
        
        # Merge headers
        request_headers = {**self.session_headers}
        if headers:
            request_headers.update(headers)
        
        # Prepare body
        body = None
        if json_data:
            body = json.dumps(json_data).encode()
            request_headers["Content-Type"] = "application/json"
        elif data:
            if isinstance(data, dict):
                body = urlencode(data).encode()
                request_headers["Content-Type"] = "application/x-www-form-urlencoded"
            else:
                body = data.encode() if isinstance(data, str) else data
        
        # Perform request with retries
        last_exception = None
        for attempt in range(self.max_retries):
            try:
                start_time = time.time()
                
                # Simulate HTTP request (in real implementation, use requests or urllib)
                # This is a mock implementation for demonstration
                response = self._mock_http_request(
                    method.value, url, request_headers, body
                )
                
                elapsed = time.time() - start_time
                
                api_response = APIResponse(
                    status_code=response["status_code"],
                    headers=response["headers"],
                    body=response["body"],
                    elapsed_time=elapsed,
                    url=url,
                    method=method.value
                )
                
                # Cache successful GET responses
                if (use_cache and self.enable_cache and 
                    method == HTTPMethod.GET and api_response.is_success()):
                    self._cache_response(cache_key, api_response)
                
                # Log request
                self.logger.info(f"{method.value} {url} - {response['status_code']} ({elapsed:.2f}s)")
                
                return api_response
                
            except Exception as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    # Exponential backoff
                    wait_time = 2 ** attempt
                    self.logger.warning(f"Request failed, retrying in {wait_time}s: {e}")
                    time.sleep(wait_time)
                continue
        
        raise Exception(f"Request failed after {self.max_retries} attempts: {last_exception}")
    
    def _mock_http_request(self, method: str, url: str, 
                          headers: Dict, body: Optional[bytes]) -> Dict:
        """Mock HTTP request for demonstration."""
        # This is a mock implementation
        # In real implementation, use requests library or urllib
        return {
            "status_code": 200,
            "headers": {"Content-Type": "application/json"},
            "body": b'{"message": "Mock response"}'
        }
    
    def _get_cache_key(self, method: HTTPMethod, url: str,
                      data: Any, json_data: Any) -> str:
        """Generate cache key for request."""
        key_parts = [method.value, url]
        if data:
            key_parts.append(str(data))
        if json_data:
            key_parts.append(json.dumps(json_data, sort_keys=True))
        
        key_string = "|".join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _get_cached_response(self, cache_key: str) -> Optional[APIResponse]:
        """Get cached response if valid."""
        if cache_key in self.cache:
            response, timestamp = self.cache[cache_key]
            if time.time() - timestamp < self.cache_ttl:
                self.logger.debug(f"Cache hit for key: {cache_key}")
                return response
            else:
                del self.cache[cache_key]
        return None
    
    def _cache_response(self, cache_key: str, response: APIResponse) -> None:
        """Cache response."""
        self.cache[cache_key] = (response, time.time())
        self.logger.debug(f"Cached response for key: {cache_key}")
    
    def clear_cache(self) -> None:
        """Clear all cached responses."""
        self.cache.clear()
        self.logger.info("Cache cleared")