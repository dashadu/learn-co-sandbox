"""
Validators Module
=================

This module provides comprehensive data validation utilities for common use cases
including email, phone numbers, URLs, credit cards, and custom validation rules.

Classes:
--------
    Validator: Main validation class with built-in validators
    ValidationRule: Custom validation rule builder
    DataProcessor: Data processing and transformation utilities
    ValidationError: Custom exception for validation failures

Examples:
    Basic validation:
    >>> validator = Validator()
    >>> validator.validate_email("user@example.com")
    True
    
    Custom rules:
    >>> rule = ValidationRule().min_length(5).max_length(20).alphanumeric()
    >>> rule.validate("hello123")
    True
"""

import re
from typing import Any, Callable, Dict, List, Optional, Union, Pattern
from datetime import datetime, date
from enum import Enum


class ValidationError(Exception):
    """
    Custom exception for validation failures.
    
    Attributes:
        field (str): Field name that failed validation
        value (Any): The invalid value
        message (str): Error message
        errors (List): List of all validation errors
    """
    
    def __init__(self, message: str, field: Optional[str] = None,
                 value: Any = None, errors: Optional[List] = None):
        """
        Initialize ValidationError.
        
        Args:
            message: Error message
            field: Field name
            value: Invalid value
            errors: List of validation errors
        """
        super().__init__(message)
        self.field = field
        self.value = value
        self.errors = errors or []


class ValidationRule:
    """
    Fluent interface for building custom validation rules.
    
    Allows chaining multiple validation criteria to create complex rules.
    
    Examples:
        String validation:
        >>> rule = ValidationRule().required().min_length(3).max_length(50)
        >>> rule.validate("hello")
        True
        
        Number validation:
        >>> rule = ValidationRule().numeric().min_value(0).max_value(100)
        >>> rule.validate(42)
        True
        
        Pattern matching:
        >>> rule = ValidationRule().pattern(r'^[A-Z]{3}-\\d{3}$')
        >>> rule.validate("ABC-123")
        True
    """
    
    def __init__(self):
        """Initialize ValidationRule with empty criteria list."""
        self.criteria: List[Callable[[Any], bool]] = []
        self.error_messages: List[str] = []
    
    def required(self) -> 'ValidationRule':
        """
        Mark field as required (not None or empty).
        
        Returns:
            Self for chaining
        
        Examples:
            >>> rule = ValidationRule().required()
            >>> rule.validate("")
            False
            >>> rule.validate("value")
            True
        """
        def check(value):
            if value is None:
                return False
            if isinstance(value, str) and not value.strip():
                return False
            if isinstance(value, (list, dict, tuple)) and len(value) == 0:
                return False
            return True
        
        self.criteria.append(check)
        self.error_messages.append("Field is required")
        return self
    
    def min_length(self, length: int) -> 'ValidationRule':
        """
        Set minimum length requirement.
        
        Args:
            length: Minimum length
        
        Returns:
            Self for chaining
        
        Examples:
            >>> rule = ValidationRule().min_length(5)
            >>> rule.validate("test")
            False
            >>> rule.validate("hello")
            True
        """
        def check(value):
            if hasattr(value, '__len__'):
                return len(value) >= length
            return False
        
        self.criteria.append(check)
        self.error_messages.append(f"Minimum length is {length}")
        return self
    
    def max_length(self, length: int) -> 'ValidationRule':
        """
        Set maximum length requirement.
        
        Args:
            length: Maximum length
        
        Returns:
            Self for chaining
        """
        def check(value):
            if hasattr(value, '__len__'):
                return len(value) <= length
            return True
        
        self.criteria.append(check)
        self.error_messages.append(f"Maximum length is {length}")
        return self
    
    def min_value(self, min_val: Union[int, float]) -> 'ValidationRule':
        """
        Set minimum value requirement.
        
        Args:
            min_val: Minimum value
        
        Returns:
            Self for chaining
        """
        def check(value):
            try:
                return float(value) >= min_val
            except (TypeError, ValueError):
                return False
        
        self.criteria.append(check)
        self.error_messages.append(f"Minimum value is {min_val}")
        return self
    
    def max_value(self, max_val: Union[int, float]) -> 'ValidationRule':
        """
        Set maximum value requirement.
        
        Args:
            max_val: Maximum value
        
        Returns:
            Self for chaining
        """
        def check(value):
            try:
                return float(value) <= max_val
            except (TypeError, ValueError):
                return False
        
        self.criteria.append(check)
        self.error_messages.append(f"Maximum value is {max_val}")
        return self
    
    def pattern(self, regex: Union[str, Pattern]) -> 'ValidationRule':
        """
        Add regex pattern requirement.
        
        Args:
            regex: Regular expression pattern
        
        Returns:
            Self for chaining
        
        Examples:
            >>> rule = ValidationRule().pattern(r'^\\d{3}-\\d{4}$')
            >>> rule.validate("123-4567")
            True
        """
        if isinstance(regex, str):
            regex = re.compile(regex)
        
        def check(value):
            if not isinstance(value, str):
                return False
            return regex.match(value) is not None
        
        self.criteria.append(check)
        self.error_messages.append(f"Must match pattern: {regex.pattern}")
        return self
    
    def alphanumeric(self) -> 'ValidationRule':
        """
        Require alphanumeric characters only.
        
        Returns:
            Self for chaining
        """
        def check(value):
            if not isinstance(value, str):
                return False
            return value.isalnum()
        
        self.criteria.append(check)
        self.error_messages.append("Must contain only alphanumeric characters")
        return self
    
    def numeric(self) -> 'ValidationRule':
        """
        Require numeric value.
        
        Returns:
            Self for chaining
        """
        def check(value):
            try:
                float(value)
                return True
            except (TypeError, ValueError):
                return False
        
        self.criteria.append(check)
        self.error_messages.append("Must be numeric")
        return self
    
    def custom(self, func: Callable[[Any], bool], message: str = "Custom validation failed") -> 'ValidationRule':
        """
        Add custom validation function.
        
        Args:
            func: Validation function returning bool
            message: Error message
        
        Returns:
            Self for chaining
        
        Examples:
            >>> rule = ValidationRule().custom(lambda x: x % 2 == 0, "Must be even")
            >>> rule.validate(4)
            True
            >>> rule.validate(3)
            False
        """
        self.criteria.append(func)
        self.error_messages.append(message)
        return self
    
    def validate(self, value: Any) -> bool:
        """
        Validate value against all criteria.
        
        Args:
            value: Value to validate
        
        Returns:
            True if all criteria pass
        """
        for criterion in self.criteria:
            if not criterion(value):
                return False
        return True
    
    def get_errors(self, value: Any) -> List[str]:
        """
        Get list of validation errors for value.
        
        Args:
            value: Value to validate
        
        Returns:
            List of error messages
        """
        errors = []
        for criterion, message in zip(self.criteria, self.error_messages):
            if not criterion(value):
                errors.append(message)
        return errors


class Validator:
    """
    Main validation class with built-in validators.
    
    Provides common validation methods for emails, URLs, phone numbers,
    credit cards, and more.
    
    Examples:
        >>> validator = Validator()
        >>> validator.validate_email("user@example.com")
        True
        >>> validator.validate_url("https://example.com")
        True
        >>> validator.validate_phone("+1-555-123-4567")
        True
    """
    
    # Regex patterns for validation
    EMAIL_PATTERN = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )
    
    URL_PATTERN = re.compile(
        r'^https?://'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$', re.IGNORECASE
    )
    
    PHONE_PATTERN = re.compile(
        r'^[\+]?[(]?[0-9]{1,3}[)]?[-\s\.]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{1,4}[-\s\.]?[0-9]{1,9}$'
    )
    
    IPV4_PATTERN = re.compile(
        r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}'
        r'(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
    )
    
    IPV6_PATTERN = re.compile(
        r'^(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|'
        r'([0-9a-fA-F]{1,4}:){1,7}:|'
        r'([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|'
        r'([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|'
        r'([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|'
        r'([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|'
        r'([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|'
        r'[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|'
        r':((:[0-9a-fA-F]{1,4}){1,7}|:))$'
    )
    
    def validate_email(self, email: str) -> bool:
        """
        Validate email address.
        
        Args:
            email: Email address to validate
        
        Returns:
            True if valid email
        
        Examples:
            >>> validator = Validator()
            >>> validator.validate_email("user@example.com")
            True
            >>> validator.validate_email("invalid.email")
            False
        """
        if not email or not isinstance(email, str):
            return False
        return self.EMAIL_PATTERN.match(email) is not None
    
    def validate_url(self, url: str) -> bool:
        """
        Validate URL.
        
        Args:
            url: URL to validate
        
        Returns:
            True if valid URL
        
        Examples:
            >>> validator = Validator()
            >>> validator.validate_url("https://example.com")
            True
            >>> validator.validate_url("not-a-url")
            False
        """
        if not url or not isinstance(url, str):
            return False
        return self.URL_PATTERN.match(url) is not None
    
    def validate_phone(self, phone: str) -> bool:
        """
        Validate phone number.
        
        Args:
            phone: Phone number to validate
        
        Returns:
            True if valid phone number
        
        Examples:
            >>> validator = Validator()
            >>> validator.validate_phone("+1-555-123-4567")
            True
            >>> validator.validate_phone("555-123-4567")
            True
        """
        if not phone or not isinstance(phone, str):
            return False
        # Remove common separators for validation
        cleaned = re.sub(r'[\s\-\(\)]', '', phone)
        if len(cleaned) < 7 or len(cleaned) > 15:
            return False
        return self.PHONE_PATTERN.match(phone) is not None
    
    def validate_credit_card(self, card_number: str) -> bool:
        """
        Validate credit card number using Luhn algorithm.
        
        Args:
            card_number: Credit card number
        
        Returns:
            True if valid credit card number
        
        Examples:
            >>> validator = Validator()
            >>> validator.validate_credit_card("4532015112830366")  # Test Visa
            True
            >>> validator.validate_credit_card("1234567890123456")
            False
        """
        if not card_number or not isinstance(card_number, str):
            return False
        
        # Remove spaces and hyphens
        card_number = re.sub(r'[\s\-]', '', card_number)
        
        # Check if all digits
        if not card_number.isdigit():
            return False
        
        # Check length (most cards are 13-19 digits)
        if len(card_number) < 13 or len(card_number) > 19:
            return False
        
        # Luhn algorithm
        def luhn_check(card_num):
            digits = [int(d) for d in card_num]
            checksum = 0
            
            # Reverse the digits
            digits = digits[::-1]
            
            for i, digit in enumerate(digits):
                if i % 2 == 1:
                    digit *= 2
                    if digit > 9:
                        digit -= 9
                checksum += digit
            
            return checksum % 10 == 0
        
        return luhn_check(card_number)
    
    def validate_ipv4(self, ip: str) -> bool:
        """
        Validate IPv4 address.
        
        Args:
            ip: IPv4 address
        
        Returns:
            True if valid IPv4
        
        Examples:
            >>> validator = Validator()
            >>> validator.validate_ipv4("192.168.1.1")
            True
            >>> validator.validate_ipv4("256.1.1.1")
            False
        """
        if not ip or not isinstance(ip, str):
            return False
        return self.IPV4_PATTERN.match(ip) is not None
    
    def validate_ipv6(self, ip: str) -> bool:
        """
        Validate IPv6 address.
        
        Args:
            ip: IPv6 address
        
        Returns:
            True if valid IPv6
        
        Examples:
            >>> validator = Validator()
            >>> validator.validate_ipv6("2001:0db8:85a3:0000:0000:8a2e:0370:7334")
            True
        """
        if not ip or not isinstance(ip, str):
            return False
        return self.IPV6_PATTERN.match(ip) is not None
    
    def validate_date(self, date_str: str, format: str = "%Y-%m-%d") -> bool:
        """
        Validate date string.
        
        Args:
            date_str: Date string
            format: Expected date format
        
        Returns:
            True if valid date
        
        Examples:
            >>> validator = Validator()
            >>> validator.validate_date("2024-03-15")
            True
            >>> validator.validate_date("2024-13-01")
            False
        """
        try:
            datetime.strptime(date_str, format)
            return True
        except (ValueError, TypeError):
            return False
    
    def validate_uuid(self, uuid_str: str, version: Optional[int] = None) -> bool:
        """
        Validate UUID string.
        
        Args:
            uuid_str: UUID string
            version: UUID version (1-5) or None for any
        
        Returns:
            True if valid UUID
        
        Examples:
            >>> validator = Validator()
            >>> validator.validate_uuid("550e8400-e29b-41d4-a716-446655440000")
            True
        """
        uuid_pattern = re.compile(
            r'^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$',
            re.IGNORECASE
        )
        
        if not uuid_str or not isinstance(uuid_str, str):
            return False
        
        if not uuid_pattern.match(uuid_str):
            return False
        
        if version:
            # Check specific version
            version_char = uuid_str[14]
            return version_char == str(version)
        
        return True


class DataProcessor:
    """
    Data processing and transformation utilities.
    
    Provides methods for cleaning, normalizing, and transforming data
    before or after validation.
    
    Examples:
        >>> processor = DataProcessor()
        >>> processor.normalize_email("USER@EXAMPLE.COM  ")
        'user@example.com'
        >>> processor.sanitize_html("<script>alert('xss')</script>Hello")
        'Hello'
    """
    
    def normalize_email(self, email: str) -> str:
        """
        Normalize email address.
        
        Args:
            email: Email address
        
        Returns:
            Normalized email (lowercase, trimmed)
        
        Examples:
            >>> processor = DataProcessor()
            >>> processor.normalize_email("  USER@EXAMPLE.COM  ")
            'user@example.com'
        """
        if not email:
            return ""
        return email.strip().lower()
    
    def normalize_phone(self, phone: str, country_code: str = "+1") -> str:
        """
        Normalize phone number.
        
        Args:
            phone: Phone number
            country_code: Default country code
        
        Returns:
            Normalized phone number
        
        Examples:
            >>> processor = DataProcessor()
            >>> processor.normalize_phone("(555) 123-4567")
            '+15551234567'
        """
        if not phone:
            return ""
        
        # Remove all non-digit characters except +
        cleaned = re.sub(r'[^\d+]', '', phone)
        
        # Add country code if not present
        if not cleaned.startswith('+'):
            if not cleaned.startswith(country_code.lstrip('+')):
                cleaned = country_code + cleaned
        
        return cleaned
    
    def sanitize_html(self, html: str) -> str:
        """
        Remove HTML tags from string.
        
        Args:
            html: HTML string
        
        Returns:
            Text without HTML tags
        
        Examples:
            >>> processor = DataProcessor()
            >>> processor.sanitize_html("<p>Hello <b>World</b></p>")
            'Hello World'
        """
        if not html:
            return ""
        
        # Remove HTML tags
        clean = re.sub(r'<[^>]+>', '', html)
        # Normalize whitespace
        clean = ' '.join(clean.split())
        return clean
    
    def truncate(self, text: str, max_length: int, suffix: str = "...") -> str:
        """
        Truncate text to maximum length.
        
        Args:
            text: Text to truncate
            max_length: Maximum length
            suffix: Suffix to append if truncated
        
        Returns:
            Truncated text
        
        Examples:
            >>> processor = DataProcessor()
            >>> processor.truncate("This is a long text", 10)
            'This is...'
        """
        if not text or len(text) <= max_length:
            return text
        
        if max_length <= len(suffix):
            return text[:max_length]
        
        return text[:max_length - len(suffix)] + suffix
    
    def mask_sensitive(self, text: str, visible_chars: int = 4,
                      mask_char: str = "*") -> str:
        """
        Mask sensitive information.
        
        Args:
            text: Text to mask
            visible_chars: Number of visible characters at end
            mask_char: Character to use for masking
        
        Returns:
            Masked text
        
        Examples:
            >>> processor = DataProcessor()
            >>> processor.mask_sensitive("4532015112830366", 4)
            '************0366'
        """
        if not text or len(text) <= visible_chars:
            return text
        
        masked_length = len(text) - visible_chars
        return mask_char * masked_length + text[-visible_chars:]
    
    def parse_boolean(self, value: Any) -> bool:
        """
        Parse various boolean representations.
        
        Args:
            value: Value to parse
        
        Returns:
            Boolean value
        
        Examples:
            >>> processor = DataProcessor()
            >>> processor.parse_boolean("yes")
            True
            >>> processor.parse_boolean("0")
            False
        """
        if isinstance(value, bool):
            return value
        
        if isinstance(value, str):
            value = value.lower().strip()
            if value in ('true', 'yes', 'y', '1', 'on'):
                return True
            if value in ('false', 'no', 'n', '0', 'off'):
                return False
        
        return bool(value)