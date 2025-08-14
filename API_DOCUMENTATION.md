# MyProject API Documentation

## Table of Contents
1. [Overview](#overview)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [API Reference](#api-reference)
   - [Utility Functions](#utility-functions)
   - [Data Structures](#data-structures)
   - [API Client](#api-client)
   - [Validators](#validators)
5. [Usage Examples](#usage-examples)
6. [Command Line Interface](#command-line-interface)
7. [Best Practices](#best-practices)

## Overview

MyProject is a comprehensive Python library providing utilities for:
- Mathematical calculations
- Data validation
- HTTP API interactions
- Data structures (Cache, Queue, Stack)
- Data processing and transformation

## Installation

```bash
# Clone the repository
git clone https://github.com/yourorg/myproject.git
cd myproject

# Install dependencies (if any)
pip install -r requirements.txt

# Run tests
python -m pytest tests/
```

## Quick Start

```python
from src import Calculator, Validator, APIClient, Cache, Queue, Stack

# Calculator
calc = Calculator()
result = calc.add(10, 5)  # 15

# Validator
validator = Validator()
is_valid = validator.validate_email("user@example.com")  # True

# Cache
cache = Cache(capacity=100)
cache.put("key", "value")
value = cache.get("key")  # "value"

# Queue
queue = Queue()
queue.enqueue("item")
item = queue.dequeue()  # "item"
```

## API Reference

### Utility Functions

#### Calculator Class

A comprehensive calculator providing mathematical operations with history tracking.

##### Constructor
```python
Calculator(precision: int = 2)
```
- **precision**: Number of decimal places for results (0-10)

##### Methods

###### add(a, b)
Add two numbers.

```python
calc = Calculator()
result = calc.add(10, 5)  # Returns: 15
```

###### subtract(a, b)
Subtract b from a.

```python
result = calc.subtract(10, 3)  # Returns: 7
```

###### multiply(a, b)
Multiply two numbers.

```python
result = calc.multiply(4, 5)  # Returns: 20
```

###### divide(a, b)
Divide a by b.

```python
result = calc.divide(10, 2)  # Returns: 5.0
# Raises ZeroDivisionError if b is 0
```

###### power(base, exponent)
Calculate base raised to exponent.

```python
result = calc.power(2, 3)  # Returns: 8
```

###### percentage(value, total)
Calculate percentage of value relative to total.

```python
result = calc.percentage(25, 100)  # Returns: 25.0
```

###### get_history()
Get calculation history with timestamps.

```python
history = calc.get_history()
# Returns: ['[2024-03-15 10:30:00] 10 + 5 = 15', ...]
```

#### Utility Functions

##### format_date(date, format_type)
Format datetime objects to various string representations.

```python
from datetime import datetime
from src import format_date

dt = datetime(2024, 3, 15, 14, 30, 0)
iso_date = format_date(dt, "iso")      # "2024-03-15"
us_date = format_date(dt, "us")        # "03/15/2024"
eu_date = format_date(dt, "eu")        # "15/03/2024"
full_date = format_date(dt, "full")    # "2024-03-15 14:30:00"
timestamp = format_date(dt, "timestamp") # "1710511800"
```

##### parse_json(json_string, default=None)
Safely parse JSON with error handling.

```python
from src import parse_json

data = parse_json('{"name": "John", "age": 30}')
# Returns: {'name': 'John', 'age': 30}

invalid = parse_json('invalid json', default={})
# Returns: {}
```

##### generate_uuid(prefix="", use_short=False)
Generate unique identifiers.

```python
from src import generate_uuid

# Full UUID
uuid = generate_uuid()  # "550e8400-e29b-41d4-a716-446655440000"

# With prefix
user_id = generate_uuid(prefix="user_")  # "user_550e8400-..."

# Short UUID (8 characters)
short_id = generate_uuid(use_short=True)  # "550e8400"
```

##### sanitize_string(text, allowed_chars=None, max_length=None)
Clean and validate string inputs.

```python
from src.utils import sanitize_string

clean = sanitize_string("Hello@World!", allowed_chars=r'[a-zA-Z\s]')
# Returns: "HelloWorld"

truncated = sanitize_string("Very long text", max_length=10)
# Returns: "Very long "
```

##### retry_operation(max_attempts=3, delay=1.0, exceptions=(Exception,))
Decorator for retrying failed operations.

```python
from src.utils import retry_operation

@retry_operation(max_attempts=3, delay=0.5)
def unstable_api_call():
    # Your code that might fail
    response = make_request()
    return response
```

### Data Structures

#### Cache Class

LRU (Least Recently Used) cache implementation with O(1) operations.

##### Constructor
```python
Cache(capacity: int = 128, ttl: Optional[float] = None)
```
- **capacity**: Maximum number of items
- **ttl**: Time-to-live in seconds (optional)

##### Methods

```python
from src import Cache

# Create cache
cache = Cache(capacity=100, ttl=60.0)  # 60 second TTL

# Add items
cache.put("key1", "value1")
cache.put("key2", {"data": "complex"})

# Retrieve items
value = cache.get("key1")  # "value1"
missing = cache.get("nonexistent", default="default")  # "default"

# Remove items
cache.remove("key1")  # Returns: True

# Check existence
if "key2" in cache:
    print("Key exists")

# Get statistics
stats = cache.get_stats()
# {'hits': 10, 'misses': 2, 'evictions': 1}

# Clear cache
cache.clear()
```

#### Queue Class

Thread-safe FIFO queue implementation.

##### Constructor
```python
Queue(maxsize: int = 0, thread_safe: bool = True)
```
- **maxsize**: Maximum size (0 for unlimited)
- **thread_safe**: Enable thread safety

##### Methods

```python
from src import Queue

# Create queue
queue = Queue(maxsize=100)

# Single operations
queue.enqueue("first")
queue.enqueue("second")
item = queue.dequeue()  # "first"
front = queue.peek()    # "second" (without removing)

# Batch operations
queue.enqueue_many([1, 2, 3, 4])
items = queue.dequeue_many(2)  # [1, 2]

# Check state
is_empty = queue.is_empty()  # False
is_full = queue.is_full()    # False
size = queue.size()          # 2

# Clear queue
queue.clear()
```

#### Stack Class

LIFO stack implementation.

##### Constructor
```python
Stack(maxsize: int = 0)
```
- **maxsize**: Maximum size (0 for unlimited)

##### Methods

```python
from src import Stack

# Create stack
stack = Stack(maxsize=50)

# Single operations
stack.push("bottom")
stack.push("middle")
stack.push("top")
item = stack.pop()   # "top"
top = stack.peek()   # "middle" (without removing)

# Batch operations
stack.push_many([1, 2, 3])
items = stack.pop_many(2)  # [3, 2]

# Get as list
all_items = stack.to_list()  # [bottom, middle, 1]

# Check state
is_empty = stack.is_empty()  # False
size = stack.size()          # 3
```

### API Client

#### APIClient Class

Comprehensive HTTP client with retries, caching, and rate limiting.

##### Constructor
```python
APIClient(
    base_url: str,
    timeout: float = 30.0,
    max_retries: int = 3,
    auth_type: str = "none",
    auth_token: Optional[str] = None,
    auth_username: Optional[str] = None,
    auth_password: Optional[str] = None,
    rate_limit: Optional[int] = None,
    rate_limit_period: float = 60,
    enable_cache: bool = False
)
```

##### Examples

```python
from src import APIClient

# Basic client
client = APIClient(base_url="https://api.example.com")

# With Bearer authentication
client = APIClient(
    base_url="https://api.example.com",
    auth_type="bearer",
    auth_token="your-token-here"
)

# With rate limiting (10 requests per minute)
client = APIClient(
    base_url="https://api.example.com",
    rate_limit=10,
    rate_limit_period=60
)

# GET request
response = client.get("/users", params={"page": 1})
if response.is_success():
    users = response.json()

# POST request
response = client.post("/users", json_data={
    "name": "John Doe",
    "email": "john@example.com"
})

# PUT request
response = client.put("/users/123", json_data={
    "name": "Jane Doe"
})

# DELETE request
response = client.delete("/users/123")

# Custom headers
client.set_header("X-Custom-Header", "value")

# Response handling
response = client.get("/data")
print(f"Status: {response.status_code}")
print(f"Headers: {response.headers}")
print(f"Body: {response.text()}")
if response.is_success():
    data = response.json()
else:
    response.raise_for_status()  # Raises exception
```

### Validators

#### Validator Class

Built-in validators for common data types.

##### Methods

```python
from src import Validator

validator = Validator()

# Email validation
is_valid = validator.validate_email("user@example.com")  # True
is_valid = validator.validate_email("invalid.email")     # False

# URL validation
is_valid = validator.validate_url("https://example.com")  # True
is_valid = validator.validate_url("not-a-url")           # False

# Phone validation
is_valid = validator.validate_phone("+1-555-123-4567")  # True
is_valid = validator.validate_phone("555-123-4567")     # True

# Credit card validation (Luhn algorithm)
is_valid = validator.validate_credit_card("4532015112830366")  # True

# IP address validation
is_valid = validator.validate_ipv4("192.168.1.1")  # True
is_valid = validator.validate_ipv6("2001:0db8:85a3::8a2e:0370:7334")  # True

# Date validation
is_valid = validator.validate_date("2024-03-15")  # True
is_valid = validator.validate_date("2024-13-01")  # False

# UUID validation
is_valid = validator.validate_uuid("550e8400-e29b-41d4-a716-446655440000")  # True
```

#### ValidationRule Class

Build custom validation rules with fluent interface.

```python
from src.validators import ValidationRule

# Username validation
username_rule = (ValidationRule()
    .required()
    .min_length(3)
    .max_length(20)
    .alphanumeric())

is_valid = username_rule.validate("john123")  # True
errors = username_rule.get_errors("ab")  # ["Minimum length is 3"]

# Age validation
age_rule = (ValidationRule()
    .required()
    .numeric()
    .min_value(18)
    .max_value(120))

is_valid = age_rule.validate(25)  # True

# Custom validation
even_number_rule = (ValidationRule()
    .numeric()
    .custom(lambda x: x % 2 == 0, "Must be even number"))

is_valid = even_number_rule.validate(4)  # True
is_valid = even_number_rule.validate(3)  # False
```

#### DataProcessor Class

Data transformation and normalization utilities.

```python
from src import DataProcessor

processor = DataProcessor()

# Email normalization
email = processor.normalize_email("  USER@EXAMPLE.COM  ")
# Returns: "user@example.com"

# Phone normalization
phone = processor.normalize_phone("(555) 123-4567")
# Returns: "+15551234567"

# HTML sanitization
text = processor.sanitize_html("<p>Hello <b>World</b></p>")
# Returns: "Hello World"

# Text truncation
truncated = processor.truncate("This is a very long text", max_length=10)
# Returns: "This is..."

# Sensitive data masking
masked = processor.mask_sensitive("4532015112830366", visible_chars=4)
# Returns: "************0366"

# Boolean parsing
value = processor.parse_boolean("yes")   # True
value = processor.parse_boolean("false") # False
value = processor.parse_boolean("1")     # True
```

## Usage Examples

### Example 1: Building a User Registration System

```python
from src import Validator, DataProcessor, APIClient
from src.validators import ValidationRule

# Setup
validator = Validator()
processor = DataProcessor()
api_client = APIClient(base_url="https://api.myapp.com")

# Define validation rules
password_rule = (ValidationRule()
    .required()
    .min_length(8)
    .pattern(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)'))

def register_user(email: str, password: str, phone: str):
    # Normalize inputs
    email = processor.normalize_email(email)
    phone = processor.normalize_phone(phone)
    
    # Validate inputs
    if not validator.validate_email(email):
        return {"error": "Invalid email address"}
    
    if not password_rule.validate(password):
        errors = password_rule.get_errors(password)
        return {"error": f"Invalid password: {errors}"}
    
    if not validator.validate_phone(phone):
        return {"error": "Invalid phone number"}
    
    # Register via API
    response = api_client.post("/users/register", json_data={
        "email": email,
        "password": password,
        "phone": phone
    })
    
    if response.is_success():
        return response.json()
    else:
        return {"error": response.text()}

# Usage
result = register_user(
    email="USER@EXAMPLE.COM  ",
    password="SecurePass123",
    phone="(555) 123-4567"
)
```

### Example 2: Caching API Responses

```python
from src import Cache, APIClient
import time

# Setup cache with 5 minute TTL
cache = Cache(capacity=100, ttl=300)
api_client = APIClient(base_url="https://api.example.com")

def get_user_data(user_id: int):
    # Check cache first
    cache_key = f"user:{user_id}"
    cached_data = cache.get(cache_key)
    
    if cached_data:
        print(f"Cache hit for user {user_id}")
        return cached_data
    
    # Fetch from API
    print(f"Fetching user {user_id} from API")
    response = api_client.get(f"/users/{user_id}")
    
    if response.is_success():
        user_data = response.json()
        # Cache the result
        cache.put(cache_key, user_data)
        return user_data
    
    return None

# First call - fetches from API
user = get_user_data(123)  # "Fetching user 123 from API"

# Second call - returns from cache
user = get_user_data(123)  # "Cache hit for user 123"
```

### Example 3: Task Queue Processing

```python
from src import Queue
import threading
import time

# Create task queue
task_queue = Queue(thread_safe=True)

def worker(worker_id: int):
    """Worker thread to process tasks"""
    while True:
        try:
            task = task_queue.dequeue()
            print(f"Worker {worker_id} processing: {task}")
            time.sleep(1)  # Simulate work
        except IndexError:
            # Queue is empty
            time.sleep(0.1)

# Start worker threads
workers = []
for i in range(3):
    t = threading.Thread(target=worker, args=(i,))
    t.daemon = True
    t.start()
    workers.append(t)

# Add tasks
tasks = ["task1", "task2", "task3", "task4", "task5"]
task_queue.enqueue_many(tasks)

# Wait for completion
while not task_queue.is_empty():
    time.sleep(0.5)
```

### Example 4: Data Validation Pipeline

```python
from src import Validator, DataProcessor
from src.validators import ValidationRule, ValidationError

class UserDataValidator:
    def __init__(self):
        self.validator = Validator()
        self.processor = DataProcessor()
        
        # Define validation rules
        self.rules = {
            'username': ValidationRule()
                .required()
                .min_length(3)
                .max_length(20)
                .pattern(r'^[a-zA-Z0-9_]+$'),
            
            'age': ValidationRule()
                .required()
                .numeric()
                .min_value(13)
                .max_value(120),
            
            'bio': ValidationRule()
                .max_length(500)
        }
    
    def validate_user_data(self, data: dict) -> dict:
        """Validate and process user data"""
        errors = {}
        processed = {}
        
        # Validate username
        if 'username' in data:
            if self.rules['username'].validate(data['username']):
                processed['username'] = data['username'].lower()
            else:
                errors['username'] = self.rules['username'].get_errors(data['username'])
        
        # Validate age
        if 'age' in data:
            if self.rules['age'].validate(data['age']):
                processed['age'] = int(data['age'])
            else:
                errors['age'] = self.rules['age'].get_errors(data['age'])
        
        # Validate and process email
        if 'email' in data:
            email = self.processor.normalize_email(data['email'])
            if self.validator.validate_email(email):
                processed['email'] = email
            else:
                errors['email'] = ["Invalid email address"]
        
        # Process bio
        if 'bio' in data:
            bio = self.processor.sanitize_html(data['bio'])
            bio = self.processor.truncate(bio, max_length=500)
            if self.rules['bio'].validate(bio):
                processed['bio'] = bio
            else:
                errors['bio'] = self.rules['bio'].get_errors(bio)
        
        if errors:
            raise ValidationError("Validation failed", errors=errors)
        
        return processed

# Usage
validator = UserDataValidator()

try:
    user_data = validator.validate_user_data({
        'username': 'john_doe',
        'age': '25',
        'email': '  JOHN@EXAMPLE.COM  ',
        'bio': '<p>Hello, I am <b>John</b>!</p>'
    })
    print(user_data)
    # {'username': 'john_doe', 'age': 25, 'email': 'john@example.com', 'bio': 'Hello, I am John!'}
except ValidationError as e:
    print(f"Validation errors: {e.errors}")
```

## Command Line Interface

The library includes a comprehensive CLI for testing and demonstration.

### Calculator Operations
```bash
# Basic arithmetic
python main.py calculate --operation add --a 10 --b 5
# Result: 15

python main.py calculate --operation divide --a 100 --b 4
# Result: 25.0

python main.py calculate --operation power --a 2 --b 8
# Result: 256
```

### Data Validation
```bash
# Validate email
python main.py validate --type email --value user@example.com
# Validation result for email: ✓ Valid

# Validate URL
python main.py validate --type url --value https://example.com
# Validation result for url: ✓ Valid

# Validate phone
python main.py validate --type phone --value "+1-555-123-4567"
# Validation result for phone: ✓ Valid
```

### Data Processing
```bash
# Normalize email
python main.py process --operation normalize_email --data "USER@EXAMPLE.COM  "
# Original: USER@EXAMPLE.COM  
# Processed: user@example.com

# Mask sensitive data
python main.py process --operation mask_sensitive --data "4532015112830366" --visible-chars 4
# Original: 4532015112830366
# Processed: ************0366

# Truncate text
python main.py process --operation truncate --data "This is a very long text that needs truncation" --max-length 20
# Original: This is a very long text that needs truncation
# Processed: This is a very lo...
```

### Demonstrations
```bash
# Run data structures demo
python main.py demo --type structures

# Run validation demo
python main.py demo --type validation

# Run all demos
python main.py demo --type all
```

### Utility Functions
```bash
# Generate UUID
python main.py utils --function uuid
# Generated UUID: 550e8400-e29b-41d4-a716-446655440000

# Generate short UUID
python main.py utils --function uuid --short
# Generated UUID: 550e8400

# Show date formats
python main.py utils --function date
# ISO: 2024-03-15
# US: 03/15/2024
# EU: 15/03/2024
# FULL: 2024-03-15 14:30:00

# Parse JSON
python main.py utils --function json --data '{"name":"John","age":30}'
# Parsed JSON: {
#   "name": "John",
#   "age": 30
# }
```

## Best Practices

### 1. Error Handling

Always handle potential errors when using the library:

```python
from src import Calculator, ValidationError

calc = Calculator()

try:
    result = calc.divide(10, 0)
except ZeroDivisionError as e:
    print(f"Error: {e}")

# For validation
try:
    # validation code
    pass
except ValidationError as e:
    print(f"Validation failed: {e.errors}")
```

### 2. Resource Management

Use context managers or cleanup methods:

```python
from src import Cache, APIClient

# Clear cache when done
cache = Cache()
# ... use cache ...
cache.clear()

# Clear API client cache
client = APIClient(base_url="...", enable_cache=True)
# ... make requests ...
client.clear_cache()
```

### 3. Thread Safety

Use thread-safe options when needed:

```python
from src import Queue

# For multi-threaded applications
queue = Queue(thread_safe=True)

# For single-threaded applications (better performance)
queue = Queue(thread_safe=False)
```

### 4. Performance Optimization

```python
# Use caching for expensive operations
cache = Cache(capacity=1000, ttl=300)  # 5 minute TTL

# Batch operations when possible
queue.enqueue_many([item1, item2, item3])  # Better than individual enqueues

# Set appropriate precision for calculations
calc = Calculator(precision=2)  # Don't use unnecessary precision
```

### 5. Input Validation

Always validate and sanitize user inputs:

```python
from src import Validator, DataProcessor

validator = Validator()
processor = DataProcessor()

def process_user_input(email: str, html_content: str):
    # Normalize and validate email
    email = processor.normalize_email(email)
    if not validator.validate_email(email):
        raise ValueError("Invalid email")
    
    # Sanitize HTML content
    safe_content = processor.sanitize_html(html_content)
    
    return email, safe_content
```

## Testing

Run unit tests:

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_calculator.py

# Run with coverage
python -m pytest --cov=src tests/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For issues, questions, or contributions, please visit:
- GitHub: https://github.com/yourorg/myproject
- Documentation: https://myproject.readthedocs.io
- Email: support@myproject.com