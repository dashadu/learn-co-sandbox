# MyProject - Usage Examples and Tutorials

This document provides comprehensive examples and tutorials for using the MyProject library.

## Table of Contents
1. [Getting Started](#getting-started)
2. [Calculator Examples](#calculator-examples)
3. [Data Validation Examples](#data-validation-examples)
4. [Data Structures Examples](#data-structures-examples)
5. [API Client Examples](#api-client-examples)
6. [Data Processing Examples](#data-processing-examples)
7. [Complete Applications](#complete-applications)
8. [Advanced Patterns](#advanced-patterns)

## Getting Started

### Basic Setup

```python
# Import the library
from src import (
    Calculator, Validator, DataProcessor,
    APIClient, Cache, Queue, Stack,
    format_date, parse_json, generate_uuid
)

# Initialize components
calc = Calculator()
validator = Validator()
processor = DataProcessor()
```

### Running from Command Line

```bash
# Get help
python main.py --help

# Run a simple calculation
python main.py calculate --operation add --a 10 --b 5

# Validate an email
python main.py validate --type email --value user@example.com
```

## Calculator Examples

### Basic Arithmetic Operations

```python
from src import Calculator

# Create calculator with 2 decimal precision
calc = Calculator(precision=2)

# Addition
result = calc.add(10.5, 20.3)
print(f"10.5 + 20.3 = {result}")  # 30.8

# Subtraction
result = calc.subtract(50, 15.75)
print(f"50 - 15.75 = {result}")  # 34.25

# Multiplication
result = calc.multiply(7.5, 4)
print(f"7.5 × 4 = {result}")  # 30.0

# Division with precision
result = calc.divide(10, 3)
print(f"10 ÷ 3 = {result}")  # 3.33

# Power
result = calc.power(2, 8)
print(f"2^8 = {result}")  # 256

# Percentage
result = calc.percentage(75, 200)
print(f"75 is {result}% of 200")  # 37.5
```

### Working with History

```python
from src import Calculator
from datetime import datetime

calc = Calculator()

# Perform several calculations
calc.add(100, 50)
calc.multiply(10, 5)
calc.divide(100, 4)

# Get calculation history
history = calc.get_history()
for entry in history:
    print(entry)
# Output:
# [2024-03-15 10:30:00] 100 + 50 = 150
# [2024-03-15 10:30:01] 10 * 5 = 50
# [2024-03-15 10:30:02] 100 / 4 = 25.0

# Clear history
calc.clear_history()
```

### Error Handling in Calculations

```python
from src import Calculator

calc = Calculator()

# Handle division by zero
try:
    result = calc.divide(10, 0)
except ZeroDivisionError as e:
    print(f"Error: {e}")  # Error: Cannot divide by zero

# Handle invalid percentage calculation
try:
    result = calc.percentage(50, 0)
except ValueError as e:
    print(f"Error: {e}")  # Error: Total cannot be zero
```

## Data Validation Examples

### Email Validation

```python
from src import Validator, DataProcessor

validator = Validator()
processor = DataProcessor()

# Test various email formats
emails = [
    "user@example.com",
    "john.doe+tag@company.co.uk",
    "invalid.email",
    "no@domain",
    "  USER@EXAMPLE.COM  "
]

for email in emails:
    # Normalize first
    normalized = processor.normalize_email(email)
    is_valid = validator.validate_email(normalized)
    print(f"{email:30} -> {normalized:25} : {'✓' if is_valid else '✗'}")
```

### Phone Number Validation

```python
from src import Validator, DataProcessor

validator = Validator()
processor = DataProcessor()

phones = [
    "+1-555-123-4567",
    "(555) 123-4567",
    "555.123.4567",
    "+44 20 7123 4567",
    "invalid phone"
]

for phone in phones:
    is_valid = validator.validate_phone(phone)
    normalized = processor.normalize_phone(phone) if is_valid else "N/A"
    print(f"{phone:20} -> {normalized:15} : {'✓' if is_valid else '✗'}")
```

### Credit Card Validation

```python
from src import Validator, DataProcessor

validator = Validator()
processor = DataProcessor()

# Test credit card numbers (these are test numbers, not real)
cards = [
    "4532015112830366",  # Valid test Visa
    "5425233430109903",  # Valid test Mastercard
    "1234567890123456",  # Invalid
    "4532-0151-1283-0366",  # With dashes
]

for card in cards:
    # Remove formatting
    clean_card = card.replace("-", "").replace(" ", "")
    is_valid = validator.validate_credit_card(clean_card)
    
    # Mask for display
    if is_valid:
        masked = processor.mask_sensitive(clean_card, visible_chars=4)
        print(f"{card:25} -> {masked:20} : ✓")
    else:
        print(f"{card:25} -> {'Invalid':20} : ✗")
```

### Custom Validation Rules

```python
from src.validators import ValidationRule, ValidationError

# Password validation rule
password_rule = (ValidationRule()
    .required()
    .min_length(8)
    .max_length(128)
    .pattern(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])')
    .custom(lambda p: 'password' not in p.lower(), "Cannot contain 'password'"))

# Test passwords
passwords = [
    "weak",
    "NoNumbers!",
    "nouppercas3!",
    "ValidPass123!",
    "Password123!",  # Contains 'password'
]

for pwd in passwords:
    if password_rule.validate(pwd):
        print(f"{pwd:20} : ✓ Valid")
    else:
        errors = password_rule.get_errors(pwd)
        print(f"{pwd:20} : ✗ {errors}")
```

### Form Validation Example

```python
from src import Validator, DataProcessor
from src.validators import ValidationRule, ValidationError

class FormValidator:
    def __init__(self):
        self.validator = Validator()
        self.processor = DataProcessor()
        
        # Define field rules
        self.rules = {
            'name': ValidationRule()
                .required()
                .min_length(2)
                .max_length(50)
                .pattern(r'^[a-zA-Z\s]+$'),
            
            'age': ValidationRule()
                .required()
                .numeric()
                .min_value(13)
                .max_value(120),
            
            'website': ValidationRule()
                .custom(lambda v: v == "" or self.validator.validate_url(v), 
                       "Invalid URL"),
            
            'bio': ValidationRule()
                .max_length(500)
        }
    
    def validate_form(self, data):
        errors = {}
        cleaned = {}
        
        for field, rule in self.rules.items():
            if field in data:
                value = data[field]
                
                # Special processing for certain fields
                if field == 'name':
                    value = value.strip().title()
                elif field == 'bio':
                    value = self.processor.sanitize_html(value)
                    value = self.processor.truncate(value, max_length=500)
                
                # Validate
                if rule.validate(value):
                    cleaned[field] = value
                else:
                    errors[field] = rule.get_errors(value)
        
        if errors:
            raise ValidationError("Form validation failed", errors=errors)
        
        return cleaned

# Usage
validator = FormValidator()

form_data = {
    'name': 'john doe',
    'age': '25',
    'website': 'https://johndoe.com',
    'bio': '<p>Software developer with <b>5 years</b> experience</p>'
}

try:
    clean_data = validator.validate_form(form_data)
    print("Form is valid!")
    print(clean_data)
except ValidationError as e:
    print(f"Validation errors: {e.errors}")
```

## Data Structures Examples

### Cache Usage Examples

```python
from src import Cache
import time

# Basic cache usage
cache = Cache(capacity=3)

# Store data
cache.put("user:1", {"name": "Alice", "age": 30})
cache.put("user:2", {"name": "Bob", "age": 25})
cache.put("user:3", {"name": "Charlie", "age": 35})

# Retrieve data
user = cache.get("user:1")
print(user)  # {'name': 'Alice', 'age': 30}

# LRU eviction - adding a 4th item evicts least recently used
cache.put("user:4", {"name": "David", "age": 28})
print(cache.get("user:2"))  # None (evicted)

# Cache with TTL
ttl_cache = Cache(capacity=100, ttl=2.0)  # 2 second TTL
ttl_cache.put("temp_data", "expires soon")
print(ttl_cache.get("temp_data"))  # "expires soon"
time.sleep(3)
print(ttl_cache.get("temp_data"))  # None (expired)

# Cache statistics
print(cache.get_stats())
# {'hits': 2, 'misses': 1, 'evictions': 1}
```

### Queue Usage Examples

```python
from src import Queue

# Basic queue operations
queue = Queue()

# Enqueue items
queue.enqueue("Task 1")
queue.enqueue("Task 2")
queue.enqueue("Task 3")

# Process items
while not queue.is_empty():
    task = queue.dequeue()
    print(f"Processing: {task}")

# Bounded queue
bounded_queue = Queue(maxsize=3)
bounded_queue.enqueue("A")
bounded_queue.enqueue("B")
bounded_queue.enqueue("C")

try:
    bounded_queue.enqueue("D")  # Queue is full
except OverflowError as e:
    print(f"Error: {e}")

# Batch operations
batch_queue = Queue()
batch_queue.enqueue_many(["Item1", "Item2", "Item3", "Item4", "Item5"])
batch = batch_queue.dequeue_many(3)
print(f"Batch processed: {batch}")  # ['Item1', 'Item2', 'Item3']
```

### Stack Usage Examples

```python
from src import Stack

# Basic stack operations
stack = Stack()

# Push items
stack.push("First")
stack.push("Second")
stack.push("Third")

# Pop items (LIFO order)
print(stack.pop())  # "Third"
print(stack.pop())  # "Second"

# Peek without removing
print(stack.peek())  # "First"
print(stack.size())  # 1 (still there)

# Stack for undo/redo functionality
class UndoRedoManager:
    def __init__(self, max_history=50):
        self.undo_stack = Stack(maxsize=max_history)
        self.redo_stack = Stack(maxsize=max_history)
    
    def do_action(self, action):
        self.undo_stack.push(action)
        self.redo_stack.clear()  # Clear redo stack on new action
        print(f"Did: {action}")
    
    def undo(self):
        if not self.undo_stack.is_empty():
            action = self.undo_stack.pop()
            self.redo_stack.push(action)
            print(f"Undid: {action}")
            return action
        return None
    
    def redo(self):
        if not self.redo_stack.is_empty():
            action = self.redo_stack.pop()
            self.undo_stack.push(action)
            print(f"Redid: {action}")
            return action
        return None

# Usage
manager = UndoRedoManager()
manager.do_action("Type 'Hello'")
manager.do_action("Type ' World'")
manager.undo()  # Undid: Type ' World'
manager.redo()  # Redid: Type ' World'
```

## API Client Examples

### Basic API Requests

```python
from src import APIClient

# Create client
client = APIClient(base_url="https://jsonplaceholder.typicode.com")

# GET request
response = client.get("/posts/1")
if response.is_success():
    post = response.json()
    print(f"Title: {post.get('title')}")

# POST request
new_post = {
    "title": "My Post",
    "body": "This is the content",
    "userId": 1
}
response = client.post("/posts", json_data=new_post)
if response.is_success():
    created = response.json()
    print(f"Created post with ID: {created.get('id')}")

# Error handling
response = client.get("/posts/99999")
if response.is_error():
    print(f"Error {response.status_code}: {response.text()}")
```

### API Client with Authentication

```python
from src import APIClient

# Bearer token authentication
bearer_client = APIClient(
    base_url="https://api.github.com",
    auth_type="bearer",
    auth_token="your_github_token"
)

# API key authentication
api_key_client = APIClient(
    base_url="https://api.example.com",
    auth_type="api_key",
    auth_token="your_api_key"
)

# Basic authentication
basic_client = APIClient(
    base_url="https://api.example.com",
    auth_type="basic",
    auth_username="user",
    auth_password="pass"
)

# Custom headers
client = APIClient(base_url="https://api.example.com")
client.set_header("X-Custom-Header", "CustomValue")
client.set_header("X-API-Version", "2.0")
```

### Rate-Limited API Client

```python
from src import APIClient
import time

# Client with rate limiting (10 requests per minute)
client = APIClient(
    base_url="https://api.example.com",
    rate_limit=10,
    rate_limit_period=60
)

# Make multiple requests - automatically rate limited
for i in range(15):
    start = time.time()
    response = client.get(f"/data/{i}")
    elapsed = time.time() - start
    print(f"Request {i+1}: {response.status_code} (took {elapsed:.2f}s)")
    # After 10 requests, subsequent requests will be delayed
```

### Cached API Requests

```python
from src import APIClient

# Enable caching
client = APIClient(
    base_url="https://api.example.com",
    enable_cache=True
)

# First request - hits the API
response1 = client.get("/expensive-data")
print("First request completed")

# Second request - returns from cache
response2 = client.get("/expensive-data")
print("Second request (cached) completed")

# Clear cache when needed
client.clear_cache()
```

## Data Processing Examples

### Text Processing

```python
from src import DataProcessor

processor = DataProcessor()

# HTML sanitization
html_content = """
<div>
    <h1>Welcome</h1>
    <p>This is <b>bold</b> and this is <script>alert('xss')</script> dangerous.</p>
    <a href="javascript:void(0)">Click me</a>
</div>
"""
clean_text = processor.sanitize_html(html_content)
print(clean_text)
# Output: Welcome This is bold and this is dangerous. Click me

# Text truncation with ellipsis
long_text = "This is a very long text that needs to be truncated for display purposes"
truncated = processor.truncate(long_text, max_length=30)
print(truncated)  # This is a very long text t...

# Custom truncation
truncated = processor.truncate(long_text, max_length=30, suffix=" [more]")
print(truncated)  # This is a very long te [more]
```

### Data Masking and Security

```python
from src import DataProcessor

processor = DataProcessor()

# Mask credit card
credit_card = "4532015112830366"
masked = processor.mask_sensitive(credit_card, visible_chars=4)
print(f"Card: {masked}")  # Card: ************0366

# Mask SSN
ssn = "123-45-6789"
masked = processor.mask_sensitive(ssn.replace("-", ""), visible_chars=4)
print(f"SSN: {masked}")  # SSN: *****6789

# Mask email partially
email = "johndoe@example.com"
parts = email.split("@")
masked_email = processor.mask_sensitive(parts[0], visible_chars=2) + "@" + parts[1]
print(f"Email: {masked_email}")  # Email: *****oe@example.com
```

### Boolean Parsing

```python
from src import DataProcessor

processor = DataProcessor()

# Parse various boolean representations
values = ["yes", "no", "true", "false", "1", "0", "on", "off", True, False, 1, 0]

for value in values:
    result = processor.parse_boolean(value)
    print(f"{str(value):10} -> {result}")
```

## Complete Applications

### User Registration System

```python
from src import Validator, DataProcessor, APIClient, Cache
from src.validators import ValidationRule, ValidationError
import hashlib

class UserRegistrationSystem:
    def __init__(self, api_base_url):
        self.validator = Validator()
        self.processor = DataProcessor()
        self.api_client = APIClient(base_url=api_base_url)
        self.cache = Cache(capacity=100, ttl=300)  # 5 min cache
        
        # Validation rules
        self.username_rule = (ValidationRule()
            .required()
            .min_length(3)
            .max_length(20)
            .pattern(r'^[a-zA-Z0-9_]+$'))
        
        self.password_rule = (ValidationRule()
            .required()
            .min_length(8)
            .pattern(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)'))
    
    def check_username_availability(self, username):
        # Check cache first
        cache_key = f"username:{username}"
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached
        
        # Check via API
        response = self.api_client.get(f"/users/check/{username}")
        available = response.json().get("available", False) if response.is_success() else False
        
        # Cache result
        self.cache.put(cache_key, available)
        return available
    
    def register_user(self, username, email, password, phone):
        # Validate inputs
        if not self.username_rule.validate(username):
            raise ValidationError("Invalid username", 
                                errors=self.username_rule.get_errors(username))
        
        if not self.password_rule.validate(password):
            raise ValidationError("Invalid password",
                                errors=self.password_rule.get_errors(password))
        
        # Normalize data
        email = self.processor.normalize_email(email)
        if not self.validator.validate_email(email):
            raise ValidationError("Invalid email address")
        
        phone = self.processor.normalize_phone(phone)
        if not self.validator.validate_phone(phone):
            raise ValidationError("Invalid phone number")
        
        # Check username availability
        if not self.check_username_availability(username):
            raise ValidationError("Username already taken")
        
        # Hash password (simplified - use bcrypt in production)
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        # Register via API
        user_data = {
            "username": username,
            "email": email,
            "password_hash": password_hash,
            "phone": phone
        }
        
        response = self.api_client.post("/users/register", json_data=user_data)
        
        if response.is_success():
            return response.json()
        else:
            raise Exception(f"Registration failed: {response.text()}")

# Usage
system = UserRegistrationSystem("https://api.example.com")

try:
    user = system.register_user(
        username="johndoe",
        email="JOHN@EXAMPLE.COM  ",
        password="SecurePass123",
        phone="(555) 123-4567"
    )
    print(f"User registered successfully: {user}")
except ValidationError as e:
    print(f"Validation error: {e}")
except Exception as e:
    print(f"Error: {e}")
```

### Task Processing System

```python
from src import Queue, Stack, Cache
import threading
import time
from enum import Enum

class TaskStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class TaskProcessor:
    def __init__(self, num_workers=3):
        self.task_queue = Queue(thread_safe=True)
        self.completed_tasks = Stack(maxsize=100)
        self.task_cache = Cache(capacity=50)
        self.num_workers = num_workers
        self.workers = []
        self.running = False
    
    def add_task(self, task_id, task_data):
        """Add a task to the queue"""
        task = {
            "id": task_id,
            "data": task_data,
            "status": TaskStatus.PENDING,
            "timestamp": time.time()
        }
        self.task_queue.enqueue(task)
        self.task_cache.put(task_id, task)
        print(f"Task {task_id} added to queue")
    
    def process_task(self, task):
        """Process a single task"""
        task["status"] = TaskStatus.PROCESSING
        self.task_cache.put(task["id"], task)
        
        try:
            # Simulate task processing
            print(f"Processing task {task['id']}: {task['data']}")
            time.sleep(2)  # Simulate work
            
            # Mark as completed
            task["status"] = TaskStatus.COMPLETED
            task["completed_at"] = time.time()
            self.completed_tasks.push(task)
            self.task_cache.put(task["id"], task)
            print(f"Task {task['id']} completed")
            
        except Exception as e:
            task["status"] = TaskStatus.FAILED
            task["error"] = str(e)
            self.task_cache.put(task["id"], task)
            print(f"Task {task['id']} failed: {e}")
    
    def worker(self, worker_id):
        """Worker thread"""
        print(f"Worker {worker_id} started")
        while self.running:
            try:
                task = self.task_queue.dequeue()
                self.process_task(task)
            except IndexError:
                # Queue is empty
                time.sleep(0.5)
        print(f"Worker {worker_id} stopped")
    
    def start(self):
        """Start processing"""
        self.running = True
        for i in range(self.num_workers):
            worker_thread = threading.Thread(target=self.worker, args=(i,))
            worker_thread.daemon = True
            worker_thread.start()
            self.workers.append(worker_thread)
        print(f"Started {self.num_workers} workers")
    
    def stop(self):
        """Stop processing"""
        self.running = False
        for worker in self.workers:
            worker.join(timeout=5)
        print("All workers stopped")
    
    def get_task_status(self, task_id):
        """Get status of a task"""
        task = self.task_cache.get(task_id)
        if task:
            return task["status"]
        return None
    
    def get_stats(self):
        """Get processing statistics"""
        return {
            "queued": self.task_queue.size(),
            "completed": self.completed_tasks.size(),
            "cache_stats": self.task_cache.get_stats()
        }

# Usage
processor = TaskProcessor(num_workers=2)
processor.start()

# Add tasks
for i in range(5):
    processor.add_task(f"task_{i}", f"Process data {i}")

# Monitor progress
while processor.task_queue.size() > 0:
    stats = processor.get_stats()
    print(f"Stats: {stats}")
    time.sleep(1)

# Check specific task
status = processor.get_task_status("task_0")
print(f"Task 0 status: {status}")

# Stop processor
processor.stop()
```

## Advanced Patterns

### Decorator Pattern with Validation

```python
from src.validators import ValidationRule
from functools import wraps

def validate_inputs(**validators):
    """Decorator to validate function inputs"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get function argument names
            import inspect
            sig = inspect.signature(func)
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()
            
            # Validate each argument
            for param_name, validator in validators.items():
                if param_name in bound.arguments:
                    value = bound.arguments[param_name]
                    if not validator.validate(value):
                        errors = validator.get_errors(value)
                        raise ValueError(f"Invalid {param_name}: {errors}")
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Usage
email_rule = ValidationRule().required().pattern(r'^[\w\.-]+@[\w\.-]+\.\w+$')
age_rule = ValidationRule().numeric().min_value(0).max_value(150)

@validate_inputs(email=email_rule, age=age_rule)
def create_user(name, email, age):
    return {
        "name": name,
        "email": email,
        "age": age
    }

# Valid call
user = create_user("John", "john@example.com", 25)
print(user)

# Invalid call (will raise ValueError)
try:
    user = create_user("John", "invalid-email", 200)
except ValueError as e:
    print(f"Error: {e}")
```

### Caching Decorator

```python
from src import Cache
from functools import wraps
import hashlib
import json

def cached(ttl=300):
    """Decorator to cache function results"""
    cache = Cache(capacity=100, ttl=ttl)
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            key_data = {
                "func": func.__name__,
                "args": args,
                "kwargs": kwargs
            }
            cache_key = hashlib.md5(
                json.dumps(key_data, sort_keys=True, default=str).encode()
            ).hexdigest()
            
            # Check cache
            result = cache.get(cache_key)
            if result is not None:
                print(f"Cache hit for {func.__name__}")
                return result
            
            # Call function and cache result
            result = func(*args, **kwargs)
            cache.put(cache_key, result)
            return result
        
        wrapper.clear_cache = cache.clear
        return wrapper
    return decorator

# Usage
@cached(ttl=60)  # Cache for 60 seconds
def expensive_calculation(x, y):
    print(f"Calculating {x} * {y}...")
    time.sleep(2)  # Simulate expensive operation
    return x * y

# First call - calculates
result = expensive_calculation(10, 20)  # Takes 2 seconds

# Second call - from cache
result = expensive_calculation(10, 20)  # Instant

# Clear cache if needed
expensive_calculation.clear_cache()
```

### Pipeline Pattern

```python
from src import DataProcessor, Validator
from src.validators import ValidationRule

class DataPipeline:
    def __init__(self):
        self.steps = []
        self.processor = DataProcessor()
        self.validator = Validator()
    
    def add_step(self, func, name=None):
        """Add a processing step to the pipeline"""
        self.steps.append({
            "func": func,
            "name": name or func.__name__
        })
        return self
    
    def process(self, data):
        """Process data through the pipeline"""
        result = data
        for step in self.steps:
            print(f"Executing: {step['name']}")
            result = step["func"](result)
        return result

# Define pipeline steps
def normalize_email_step(data):
    processor = DataProcessor()
    if "email" in data:
        data["email"] = processor.normalize_email(data["email"])
    return data

def validate_email_step(data):
    validator = Validator()
    if "email" in data:
        if not validator.validate_email(data["email"]):
            raise ValueError(f"Invalid email: {data['email']}")
    return data

def sanitize_html_step(data):
    processor = DataProcessor()
    for key in ["bio", "description", "content"]:
        if key in data:
            data[key] = processor.sanitize_html(data[key])
    return data

def truncate_fields_step(data):
    processor = DataProcessor()
    limits = {"bio": 200, "description": 100, "title": 50}
    for field, limit in limits.items():
        if field in data:
            data[field] = processor.truncate(data[field], max_length=limit)
    return data

# Create and use pipeline
pipeline = DataPipeline()
pipeline.add_step(normalize_email_step, "Normalize Email")
pipeline.add_step(validate_email_step, "Validate Email")
pipeline.add_step(sanitize_html_step, "Sanitize HTML")
pipeline.add_step(truncate_fields_step, "Truncate Fields")

# Process data
input_data = {
    "email": "  USER@EXAMPLE.COM  ",
    "bio": "<p>This is a <b>very long</b> biography " * 20 + "</p>",
    "title": "This is a very long title that needs to be truncated"
}

try:
    output_data = pipeline.process(input_data)
    print("\nProcessed data:")
    for key, value in output_data.items():
        print(f"{key}: {value[:50]}..." if len(str(value)) > 50 else f"{key}: {value}")
except ValueError as e:
    print(f"Pipeline error: {e}")
```

## Testing Examples

### Unit Testing

```python
import unittest
from src import Calculator, Validator, Cache

class TestCalculator(unittest.TestCase):
    def setUp(self):
        self.calc = Calculator(precision=2)
    
    def test_addition(self):
        self.assertEqual(self.calc.add(2, 3), 5)
        self.assertEqual(self.calc.add(-1, 1), 0)
        self.assertEqual(self.calc.add(0.1, 0.2), 0.3)
    
    def test_division(self):
        self.assertEqual(self.calc.divide(10, 2), 5.0)
        self.assertEqual(self.calc.divide(7, 3), 2.33)
        
        with self.assertRaises(ZeroDivisionError):
            self.calc.divide(10, 0)
    
    def test_history(self):
        self.calc.add(1, 2)
        self.calc.multiply(3, 4)
        history = self.calc.get_history()
        self.assertEqual(len(history), 2)

class TestValidator(unittest.TestCase):
    def setUp(self):
        self.validator = Validator()
    
    def test_email_validation(self):
        self.assertTrue(self.validator.validate_email("user@example.com"))
        self.assertTrue(self.validator.validate_email("user.name+tag@example.co.uk"))
        self.assertFalse(self.validator.validate_email("invalid.email"))
        self.assertFalse(self.validator.validate_email("@example.com"))
    
    def test_url_validation(self):
        self.assertTrue(self.validator.validate_url("https://example.com"))
        self.assertTrue(self.validator.validate_url("http://localhost:8080"))
        self.assertFalse(self.validator.validate_url("not a url"))
        self.assertFalse(self.validator.validate_url("ftp://example.com"))

class TestCache(unittest.TestCase):
    def test_lru_eviction(self):
        cache = Cache(capacity=2)
        cache.put("a", 1)
        cache.put("b", 2)
        cache.put("c", 3)  # Should evict "a"
        
        self.assertIsNone(cache.get("a"))
        self.assertEqual(cache.get("b"), 2)
        self.assertEqual(cache.get("c"), 3)
    
    def test_ttl(self):
        import time
        cache = Cache(capacity=10, ttl=0.1)  # 100ms TTL
        cache.put("key", "value")
        
        self.assertEqual(cache.get("key"), "value")
        time.sleep(0.2)
        self.assertIsNone(cache.get("key"))

if __name__ == "__main__":
    unittest.main()
```

## Performance Tips

### 1. Use Batch Operations

```python
from src import Queue

# Inefficient
queue = Queue()
for item in range(1000):
    queue.enqueue(item)  # 1000 individual operations

# Efficient
queue = Queue()
items = list(range(1000))
queue.enqueue_many(items)  # Single batch operation
```

### 2. Cache Expensive Operations

```python
from src import Cache

cache = Cache(capacity=1000, ttl=3600)  # 1 hour cache

def get_user_data(user_id):
    # Check cache first
    cached = cache.get(f"user:{user_id}")
    if cached:
        return cached
    
    # Expensive operation
    data = fetch_from_database(user_id)
    
    # Cache result
    cache.put(f"user:{user_id}", data)
    return data
```

### 3. Use Appropriate Data Structures

```python
# For FIFO processing
queue = Queue()  # O(1) enqueue/dequeue

# For LIFO processing
stack = Stack()  # O(1) push/pop

# For fast lookups with automatic eviction
cache = Cache()  # O(1) get/put with LRU eviction
```

## Troubleshooting

### Common Issues and Solutions

1. **Import Errors**
   ```python
   # Make sure the src package is in your Python path
   import sys
   sys.path.append('/path/to/project')
   from src import Calculator
   ```

2. **Thread Safety Issues**
   ```python
   # Use thread-safe queue for multi-threaded apps
   queue = Queue(thread_safe=True)
   
   # For single-threaded apps, disable for better performance
   queue = Queue(thread_safe=False)
   ```

3. **Memory Issues with Cache**
   ```python
   # Set appropriate capacity
   cache = Cache(capacity=100)  # Limit cache size
   
   # Clear cache periodically
   cache.clear()
   
   # Use TTL to auto-expire entries
   cache = Cache(capacity=1000, ttl=300)  # 5 min TTL
   ```

4. **API Rate Limiting**
   ```python
   # Configure rate limiting
   client = APIClient(
       base_url="https://api.example.com",
       rate_limit=10,  # 10 requests
       rate_limit_period=60  # per minute
   )
   ```

## Conclusion

This comprehensive guide covers all major features and use cases of the MyProject library. For more information:

- Read the [API Documentation](API_DOCUMENTATION.md)
- Check the source code in the `src/` directory
- Run the examples using the CLI: `python main.py demo --type all`

Happy coding!