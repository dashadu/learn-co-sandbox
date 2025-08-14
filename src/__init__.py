"""
MyProject - A Comprehensive Python Library
==========================================

A well-documented Python library demonstrating best practices for API design,
documentation, and usage examples.

Package Structure:
------------------
- utils: Utility functions for common operations
- data_structures: Custom data structures and algorithms
- api_client: HTTP API client for external services
- validators: Data validation utilities
- core: Core application logic

Quick Start:
-----------
    >>> from src import Calculator, DataProcessor, APIClient
    >>> calc = Calculator()
    >>> result = calc.add(5, 3)
    >>> print(result)
    8

Version: 1.0.0
Author: Development Team
License: MIT
"""

__version__ = "1.0.0"
__author__ = "Development Team"
__all__ = [
    "Calculator",
    "DataProcessor",
    "APIClient",
    "Validator",
    "Cache",
    "Queue",
    "Stack",
    "format_date",
    "parse_json",
    "generate_uuid"
]

# Import main components for easier access
from .utils import Calculator, format_date, parse_json, generate_uuid
from .data_structures import Cache, Queue, Stack
from .api_client import APIClient
from .validators import Validator, DataProcessor