#!/usr/bin/env python3
"""
Main Application Module
=======================

This is the main entry point for the application, demonstrating usage of all
modules and providing a command-line interface for common operations.

Usage:
    python main.py --help
    python main.py calculate --operation add --a 10 --b 5
    python main.py validate --type email --value user@example.com
    python main.py api --method get --url https://api.example.com/data

Author: Development Team
Version: 1.0.0
"""

import argparse
import sys
import json
from typing import Any, Dict, List, Optional

# Import all modules from src package
from src import (
    Calculator,
    DataProcessor,
    APIClient,
    Validator,
    Cache,
    Queue,
    Stack,
    format_date,
    parse_json,
    generate_uuid
)
from src.validators import ValidationRule
from datetime import datetime


class Application:
    """
    Main application class orchestrating all functionality.
    
    This class provides a unified interface to all library features and
    serves as an example of how to integrate the various modules.
    
    Attributes:
        calculator (Calculator): Math operations handler
        validator (Validator): Data validation handler
        processor (DataProcessor): Data processing utilities
        cache (Cache): Application cache
        api_client (APIClient): HTTP client for API calls
    
    Examples:
        >>> app = Application()
        >>> app.run_calculation("add", 5, 3)
        8
        >>> app.validate_input("email", "user@example.com")
        True
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the application.
        
        Args:
            config: Optional configuration dictionary
        """
        config = config or {}
        
        # Initialize components
        self.calculator = Calculator(precision=config.get('precision', 2))
        self.validator = Validator()
        self.processor = DataProcessor()
        self.cache = Cache(capacity=config.get('cache_size', 100))
        
        # Initialize API client if base_url provided
        api_config = config.get('api', {})
        if api_config.get('base_url'):
            self.api_client = APIClient(
                base_url=api_config['base_url'],
                timeout=api_config.get('timeout', 30),
                max_retries=api_config.get('max_retries', 3)
            )
        else:
            self.api_client = None
        
        # Initialize data structures
        self.queue = Queue(maxsize=config.get('queue_size', 0))
        self.stack = Stack(maxsize=config.get('stack_size', 0))
    
    def run_calculation(self, operation: str, a: float, b: float) -> float:
        """
        Perform a calculation.
        
        Args:
            operation: Operation name (add, subtract, multiply, divide, power)
            a: First operand
            b: Second operand
        
        Returns:
            Calculation result
        
        Raises:
            ValueError: If operation is not supported
        
        Examples:
            >>> app = Application()
            >>> app.run_calculation("add", 10, 5)
            15
            >>> app.run_calculation("divide", 10, 2)
            5.0
        """
        operations = {
            'add': self.calculator.add,
            'subtract': self.calculator.subtract,
            'multiply': self.calculator.multiply,
            'divide': self.calculator.divide,
            'power': self.calculator.power
        }
        
        if operation not in operations:
            raise ValueError(f"Unsupported operation: {operation}")
        
        # Check cache first
        cache_key = f"calc:{operation}:{a}:{b}"
        cached_result = self.cache.get(cache_key)
        if cached_result is not None:
            print(f"Cache hit for {operation}({a}, {b})")
            return cached_result
        
        # Perform calculation
        result = operations[operation](a, b)
        
        # Cache result
        self.cache.put(cache_key, result)
        
        return result
    
    def validate_input(self, validation_type: str, value: str) -> bool:
        """
        Validate input data.
        
        Args:
            validation_type: Type of validation (email, url, phone, etc.)
            value: Value to validate
        
        Returns:
            True if valid
        
        Examples:
            >>> app = Application()
            >>> app.validate_input("email", "user@example.com")
            True
            >>> app.validate_input("url", "https://example.com")
            True
        """
        validators = {
            'email': self.validator.validate_email,
            'url': self.validator.validate_url,
            'phone': self.validator.validate_phone,
            'credit_card': self.validator.validate_credit_card,
            'ipv4': self.validator.validate_ipv4,
            'ipv6': self.validator.validate_ipv6,
            'uuid': self.validator.validate_uuid,
            'date': lambda v: self.validator.validate_date(v)
        }
        
        if validation_type not in validators:
            print(f"Unknown validation type: {validation_type}")
            return False
        
        return validators[validation_type](value)
    
    def process_data(self, operation: str, data: str, **kwargs) -> str:
        """
        Process data using DataProcessor.
        
        Args:
            operation: Processing operation
            data: Input data
            **kwargs: Additional arguments for the operation
        
        Returns:
            Processed data
        
        Examples:
            >>> app = Application()
            >>> app.process_data("normalize_email", "USER@EXAMPLE.COM  ")
            'user@example.com'
        """
        operations = {
            'normalize_email': self.processor.normalize_email,
            'normalize_phone': self.processor.normalize_phone,
            'sanitize_html': self.processor.sanitize_html,
            'truncate': lambda d: self.processor.truncate(d, **kwargs),
            'mask_sensitive': lambda d: self.processor.mask_sensitive(d, **kwargs)
        }
        
        if operation not in operations:
            raise ValueError(f"Unknown operation: {operation}")
        
        return operations[operation](data)
    
    def make_api_request(self, method: str, endpoint: str,
                        data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make an API request.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            data: Request data
        
        Returns:
            Response data
        
        Examples:
            >>> app = Application({"api": {"base_url": "https://api.example.com"}})
            >>> response = app.make_api_request("GET", "/users")
            >>> response['status']
            200
        """
        if not self.api_client:
            raise RuntimeError("API client not configured")
        
        method = method.upper()
        if method == "GET":
            response = self.api_client.get(endpoint)
        elif method == "POST":
            response = self.api_client.post(endpoint, json_data=data)
        elif method == "PUT":
            response = self.api_client.put(endpoint, json_data=data)
        elif method == "DELETE":
            response = self.api_client.delete(endpoint)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        return {
            'status': response.status_code,
            'data': response.json() if response.is_success() else None,
            'error': response.text() if response.is_error() else None
        }
    
    def demonstrate_data_structures(self) -> None:
        """
        Demonstrate usage of data structures.
        
        This method shows how to use Cache, Queue, and Stack.
        """
        print("\n=== Data Structures Demo ===\n")
        
        # Cache demo
        print("Cache Demo:")
        cache = Cache(capacity=3)
        cache.put("key1", "value1")
        cache.put("key2", "value2")
        cache.put("key3", "value3")
        print(f"Cache size: {cache.size()}")
        print(f"Get key1: {cache.get('key1')}")
        cache.put("key4", "value4")  # This evicts key2
        print(f"Get key2 (evicted): {cache.get('key2')}")
        print(f"Cache stats: {cache.get_stats()}\n")
        
        # Queue demo
        print("Queue Demo:")
        queue = Queue()
        queue.enqueue("first")
        queue.enqueue("second")
        queue.enqueue("third")
        print(f"Queue size: {queue.size()}")
        print(f"Dequeue: {queue.dequeue()}")
        print(f"Peek: {queue.peek()}")
        print(f"Queue size after dequeue: {queue.size()}\n")
        
        # Stack demo
        print("Stack Demo:")
        stack = Stack()
        stack.push("bottom")
        stack.push("middle")
        stack.push("top")
        print(f"Stack size: {stack.size()}")
        print(f"Pop: {stack.pop()}")
        print(f"Peek: {stack.peek()}")
        print(f"Stack size after pop: {stack.size()}")
    
    def demonstrate_validation_rules(self) -> None:
        """
        Demonstrate custom validation rules.
        """
        print("\n=== Validation Rules Demo ===\n")
        
        # Username validation
        username_rule = (ValidationRule()
                        .required()
                        .min_length(3)
                        .max_length(20)
                        .alphanumeric())
        
        test_usernames = ["ab", "validuser123", "user@123", "verylongusernamethatexceedslimit"]
        
        for username in test_usernames:
            is_valid = username_rule.validate(username)
            if not is_valid:
                errors = username_rule.get_errors(username)
                print(f"'{username}' - Invalid: {errors}")
            else:
                print(f"'{username}' - Valid")
        
        print()
        
        # Age validation
        age_rule = (ValidationRule()
                   .required()
                   .numeric()
                   .min_value(18)
                   .max_value(120))
        
        test_ages = [17, 25, 150, "not_a_number"]
        
        for age in test_ages:
            is_valid = age_rule.validate(age)
            print(f"Age {age}: {'Valid' if is_valid else 'Invalid'}")


def create_cli_parser() -> argparse.ArgumentParser:
    """
    Create command-line interface parser.
    
    Returns:
        Configured ArgumentParser
    """
    parser = argparse.ArgumentParser(
        description="MyProject CLI - Comprehensive Python Library Demo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Calculator operations
    python main.py calculate --operation add --a 10 --b 5
    python main.py calculate --operation divide --a 100 --b 4
    
    # Validation
    python main.py validate --type email --value user@example.com
    python main.py validate --type url --value https://example.com
    
    # Data processing
    python main.py process --operation normalize_email --data "USER@EXAMPLE.COM"
    python main.py process --operation mask_sensitive --data "4532015112830366"
    
    # Demos
    python main.py demo --type structures
    python main.py demo --type validation
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Calculate command
    calc_parser = subparsers.add_parser('calculate', help='Perform calculations')
    calc_parser.add_argument('--operation', required=True,
                            choices=['add', 'subtract', 'multiply', 'divide', 'power'],
                            help='Mathematical operation')
    calc_parser.add_argument('--a', type=float, required=True, help='First operand')
    calc_parser.add_argument('--b', type=float, required=True, help='Second operand')
    
    # Validate command
    val_parser = subparsers.add_parser('validate', help='Validate data')
    val_parser.add_argument('--type', required=True,
                           choices=['email', 'url', 'phone', 'credit_card',
                                   'ipv4', 'ipv6', 'uuid', 'date'],
                           help='Validation type')
    val_parser.add_argument('--value', required=True, help='Value to validate')
    
    # Process command
    proc_parser = subparsers.add_parser('process', help='Process data')
    proc_parser.add_argument('--operation', required=True,
                            choices=['normalize_email', 'normalize_phone',
                                    'sanitize_html', 'truncate', 'mask_sensitive'],
                            help='Processing operation')
    proc_parser.add_argument('--data', required=True, help='Data to process')
    proc_parser.add_argument('--max-length', type=int, help='Max length for truncate')
    proc_parser.add_argument('--visible-chars', type=int, help='Visible chars for mask')
    
    # Demo command
    demo_parser = subparsers.add_parser('demo', help='Run demonstrations')
    demo_parser.add_argument('--type', required=True,
                            choices=['structures', 'validation', 'all'],
                            help='Demo type')
    
    # Utils command
    utils_parser = subparsers.add_parser('utils', help='Utility functions')
    utils_parser.add_argument('--function', required=True,
                             choices=['uuid', 'date', 'json'],
                             help='Utility function')
    utils_parser.add_argument('--data', help='Input data')
    utils_parser.add_argument('--short', action='store_true',
                             help='Generate short UUID')
    
    return parser


def main():
    """
    Main entry point for the application.
    
    Parses command-line arguments and executes requested operations.
    """
    parser = create_cli_parser()
    args = parser.parse_args()
    
    # Initialize application
    app = Application()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'calculate':
            result = app.run_calculation(args.operation, args.a, args.b)
            print(f"Result: {result}")
            print(f"History: {app.calculator.get_history()[-1]}")
        
        elif args.command == 'validate':
            is_valid = app.validate_input(args.type, args.value)
            print(f"Validation result for {args.type}: {'✓ Valid' if is_valid else '✗ Invalid'}")
            if not is_valid:
                print(f"Value: {args.value}")
        
        elif args.command == 'process':
            kwargs = {}
            if args.max_length:
                kwargs['max_length'] = args.max_length
            if args.visible_chars:
                kwargs['visible_chars'] = args.visible_chars
            
            result = app.process_data(args.operation, args.data, **kwargs)
            print(f"Original: {args.data}")
            print(f"Processed: {result}")
        
        elif args.command == 'demo':
            if args.type == 'structures' or args.type == 'all':
                app.demonstrate_data_structures()
            if args.type == 'validation' or args.type == 'all':
                app.demonstrate_validation_rules()
        
        elif args.command == 'utils':
            if args.function == 'uuid':
                uuid = generate_uuid(use_short=args.short)
                print(f"Generated UUID: {uuid}")
            elif args.function == 'date':
                now = datetime.now()
                for fmt in ['iso', 'us', 'eu', 'full']:
                    print(f"{fmt.upper()}: {format_date(now, fmt)}")
            elif args.function == 'json':
                if args.data:
                    result = parse_json(args.data, default={})
                    print(f"Parsed JSON: {json.dumps(result, indent=2)}")
                else:
                    print("Please provide --data for JSON parsing")
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()