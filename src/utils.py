"""
Utility Functions Module
========================

This module provides a collection of utility functions and classes for common
operations including mathematical calculations, string manipulation, date formatting,
and data processing.

Classes:
--------
    Calculator: A class providing basic and advanced mathematical operations

Functions:
----------
    format_date: Format datetime objects to various string representations
    parse_json: Safely parse JSON strings with error handling
    generate_uuid: Generate unique identifiers
    sanitize_string: Clean and validate string inputs
    retry_operation: Decorator for retrying failed operations
"""

import json
import uuid
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Union, Callable
from functools import wraps
import time


class Calculator:
    """
    A calculator class providing mathematical operations.
    
    This class implements basic arithmetic operations as well as advanced
    mathematical functions with proper error handling and validation.
    
    Attributes:
        precision (int): Number of decimal places for results (default: 2)
        history (List[str]): History of performed calculations
    
    Examples:
        Basic arithmetic:
        >>> calc = Calculator()
        >>> calc.add(10, 5)
        15
        >>> calc.multiply(3, 4)
        12
        
        Advanced operations:
        >>> calc.power(2, 3)
        8
        >>> calc.percentage(50, 200)
        25.0
        
        With precision:
        >>> calc = Calculator(precision=4)
        >>> calc.divide(10, 3)
        3.3333
    """
    
    def __init__(self, precision: int = 2):
        """
        Initialize the Calculator.
        
        Args:
            precision (int): Number of decimal places for results.
                           Must be between 0 and 10.
        
        Raises:
            ValueError: If precision is not between 0 and 10.
        """
        if not 0 <= precision <= 10:
            raise ValueError("Precision must be between 0 and 10")
        self.precision = precision
        self.history: List[str] = []
    
    def add(self, a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
        """
        Add two numbers.
        
        Args:
            a: First number
            b: Second number
        
        Returns:
            Sum of a and b
        
        Examples:
            >>> calc = Calculator()
            >>> calc.add(5, 3)
            8
            >>> calc.add(2.5, 1.5)
            4.0
        """
        result = a + b
        self._log_operation(f"{a} + {b} = {result}")
        return result
    
    def subtract(self, a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
        """
        Subtract b from a.
        
        Args:
            a: Number to subtract from
            b: Number to subtract
        
        Returns:
            Difference of a and b
        
        Examples:
            >>> calc = Calculator()
            >>> calc.subtract(10, 3)
            7
        """
        result = a - b
        self._log_operation(f"{a} - {b} = {result}")
        return result
    
    def multiply(self, a: Union[int, float], b: Union[int, float]) -> Union[int, float]:
        """
        Multiply two numbers.
        
        Args:
            a: First number
            b: Second number
        
        Returns:
            Product of a and b
        
        Examples:
            >>> calc = Calculator()
            >>> calc.multiply(4, 5)
            20
        """
        result = a * b
        self._log_operation(f"{a} * {b} = {result}")
        return result
    
    def divide(self, a: Union[int, float], b: Union[int, float]) -> float:
        """
        Divide a by b.
        
        Args:
            a: Dividend
            b: Divisor
        
        Returns:
            Quotient of a divided by b
        
        Raises:
            ZeroDivisionError: If b is zero
        
        Examples:
            >>> calc = Calculator()
            >>> calc.divide(10, 2)
            5.0
            >>> calc.divide(7, 3)
            2.33
        """
        if b == 0:
            raise ZeroDivisionError("Cannot divide by zero")
        result = round(a / b, self.precision)
        self._log_operation(f"{a} / {b} = {result}")
        return result
    
    def power(self, base: Union[int, float], exponent: Union[int, float]) -> Union[int, float]:
        """
        Calculate base raised to the power of exponent.
        
        Args:
            base: The base number
            exponent: The exponent
        
        Returns:
            base^exponent
        
        Examples:
            >>> calc = Calculator()
            >>> calc.power(2, 3)
            8
            >>> calc.power(5, 2)
            25
        """
        result = base ** exponent
        self._log_operation(f"{base}^{exponent} = {result}")
        return result
    
    def percentage(self, value: Union[int, float], total: Union[int, float]) -> float:
        """
        Calculate percentage of value relative to total.
        
        Args:
            value: The value to calculate percentage for
            total: The total value
        
        Returns:
            Percentage as a float
        
        Raises:
            ValueError: If total is zero
        
        Examples:
            >>> calc = Calculator()
            >>> calc.percentage(25, 100)
            25.0
            >>> calc.percentage(30, 200)
            15.0
        """
        if total == 0:
            raise ValueError("Total cannot be zero")
        result = round((value / total) * 100, self.precision)
        self._log_operation(f"{value} is {result}% of {total}")
        return result
    
    def _log_operation(self, operation: str) -> None:
        """Log an operation to history."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.history.append(f"[{timestamp}] {operation}")
    
    def get_history(self) -> List[str]:
        """
        Get the calculation history.
        
        Returns:
            List of performed calculations with timestamps
        
        Examples:
            >>> calc = Calculator()
            >>> calc.add(5, 3)
            8
            >>> calc.multiply(2, 4)
            8
            >>> history = calc.get_history()
            >>> len(history)
            2
        """
        return self.history.copy()
    
    def clear_history(self) -> None:
        """Clear the calculation history."""
        self.history.clear()


def format_date(date: datetime, format_type: str = "iso") -> str:
    """
    Format a datetime object to various string representations.
    
    Args:
        date: The datetime object to format
        format_type: The format type. Options:
            - "iso": ISO 8601 format (YYYY-MM-DD)
            - "us": US format (MM/DD/YYYY)
            - "eu": European format (DD/MM/YYYY)
            - "full": Full format with time
            - "timestamp": Unix timestamp
    
    Returns:
        Formatted date string
    
    Raises:
        ValueError: If format_type is not recognized
    
    Examples:
        >>> from datetime import datetime
        >>> dt = datetime(2024, 3, 15, 14, 30, 0)
        >>> format_date(dt, "iso")
        '2024-03-15'
        >>> format_date(dt, "us")
        '03/15/2024'
        >>> format_date(dt, "eu")
        '15/03/2024'
        >>> format_date(dt, "full")
        '2024-03-15 14:30:00'
    """
    formats = {
        "iso": "%Y-%m-%d",
        "us": "%m/%d/%Y",
        "eu": "%d/%m/%Y",
        "full": "%Y-%m-%d %H:%M:%S",
        "timestamp": "timestamp"
    }
    
    if format_type not in formats:
        raise ValueError(f"Unknown format type: {format_type}")
    
    if format_type == "timestamp":
        return str(int(date.timestamp()))
    
    return date.strftime(formats[format_type])


def parse_json(json_string: str, default: Any = None) -> Any:
    """
    Safely parse a JSON string with error handling.
    
    Args:
        json_string: The JSON string to parse
        default: Default value to return if parsing fails
    
    Returns:
        Parsed JSON object or default value
    
    Examples:
        >>> parse_json('{"name": "John", "age": 30}')
        {'name': 'John', 'age': 30}
        >>> parse_json('[1, 2, 3]')
        [1, 2, 3]
        >>> parse_json('invalid json', default={})
        {}
        >>> parse_json('null')
        None
    """
    try:
        return json.loads(json_string)
    except (json.JSONDecodeError, TypeError):
        return default


def generate_uuid(prefix: str = "", use_short: bool = False) -> str:
    """
    Generate a unique identifier.
    
    Args:
        prefix: Optional prefix for the UUID
        use_short: If True, generates a shorter 8-character ID
    
    Returns:
        Generated UUID string
    
    Examples:
        >>> uid = generate_uuid()
        >>> len(uid)
        36
        >>> uid = generate_uuid(prefix="user_")
        >>> uid.startswith("user_")
        True
        >>> uid = generate_uuid(use_short=True)
        >>> len(uid)
        8
    """
    if use_short:
        uid = str(uuid.uuid4())[:8]
    else:
        uid = str(uuid.uuid4())
    
    return f"{prefix}{uid}" if prefix else uid


def sanitize_string(text: str, allowed_chars: Optional[str] = None,
                   max_length: Optional[int] = None) -> str:
    """
    Clean and validate string inputs.
    
    Args:
        text: The string to sanitize
        allowed_chars: Regex pattern of allowed characters (default: alphanumeric + space)
        max_length: Maximum allowed length
    
    Returns:
        Sanitized string
    
    Examples:
        >>> sanitize_string("Hello World!")
        'Hello World'
        >>> sanitize_string("user@123#test", allowed_chars=r'[a-zA-Z0-9]')
        'user123test'
        >>> sanitize_string("This is a very long string", max_length=10)
        'This is a '
    """
    if allowed_chars is None:
        allowed_chars = r'[a-zA-Z0-9\s]'
    
    # Remove characters not matching the pattern
    sanitized = ''.join(re.findall(allowed_chars, text))
    
    # Apply max length if specified
    if max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized


def retry_operation(max_attempts: int = 3, delay: float = 1.0,
                   exceptions: tuple = (Exception,)) -> Callable:
    """
    Decorator for retrying failed operations.
    
    Args:
        max_attempts: Maximum number of retry attempts
        delay: Delay between attempts in seconds
        exceptions: Tuple of exceptions to catch and retry
    
    Returns:
        Decorated function
    
    Examples:
        >>> @retry_operation(max_attempts=3, delay=0.5)
        ... def unstable_network_call():
        ...     # Simulated network call
        ...     import random
        ...     if random.random() < 0.7:
        ...         raise ConnectionError("Network error")
        ...     return "Success"
        
        >>> @retry_operation(exceptions=(ValueError, TypeError))
        ... def process_data(data):
        ...     if not data:
        ...         raise ValueError("Empty data")
        ...     return len(data)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        time.sleep(delay)
                    continue
            raise last_exception
        return wrapper
    return decorator