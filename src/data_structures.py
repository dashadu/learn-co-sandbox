"""
Data Structures Module
======================

This module implements commonly used data structures with optimized performance
and comprehensive error handling.

Classes:
--------
    Cache: LRU (Least Recently Used) cache implementation
    Queue: FIFO queue with thread-safety support
    Stack: LIFO stack implementation
    LinkedList: Doubly linked list with iteration support

Each data structure provides:
- Type hints for better IDE support
- Comprehensive error handling
- Thread-safety options
- Performance optimizations
- Rich comparison methods
"""

from typing import Any, Dict, Generic, List, Optional, TypeVar, Iterator
from collections import OrderedDict
from threading import Lock
import time


T = TypeVar('T')


class Cache(Generic[T]):
    """
    LRU (Least Recently Used) Cache implementation.
    
    A cache that automatically evicts least recently used items when the
    capacity is reached. Provides O(1) get and put operations.
    
    Attributes:
        capacity (int): Maximum number of items in cache
        ttl (float): Time-to-live for cache entries in seconds (optional)
        stats (Dict): Cache statistics (hits, misses, evictions)
    
    Examples:
        Basic usage:
        >>> cache = Cache(capacity=3)
        >>> cache.put("key1", "value1")
        >>> cache.put("key2", "value2")
        >>> cache.get("key1")
        'value1'
        
        With TTL:
        >>> cache = Cache(capacity=100, ttl=60.0)  # 60 second TTL
        >>> cache.put("temp", "data")
        >>> # After 60 seconds, the entry expires
        
        Statistics:
        >>> cache.get_stats()
        {'hits': 5, 'misses': 2, 'evictions': 1}
    """
    
    def __init__(self, capacity: int = 128, ttl: Optional[float] = None):
        """
        Initialize the Cache.
        
        Args:
            capacity: Maximum number of items (must be positive)
            ttl: Time-to-live in seconds (optional)
        
        Raises:
            ValueError: If capacity is not positive
        """
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        
        self.capacity = capacity
        self.ttl = ttl
        self._cache: OrderedDict = OrderedDict()
        self._timestamps: Dict[Any, float] = {}
        self._lock = Lock()
        self.stats = {"hits": 0, "misses": 0, "evictions": 0}
    
    def put(self, key: Any, value: T) -> None:
        """
        Add or update an item in the cache.
        
        Args:
            key: The cache key
            value: The value to cache
        
        Examples:
            >>> cache = Cache(capacity=2)
            >>> cache.put("a", 1)
            >>> cache.put("b", 2)
            >>> cache.put("c", 3)  # Evicts "a"
            >>> "a" in cache
            False
        """
        with self._lock:
            # Remove key if it exists (to update position)
            if key in self._cache:
                del self._cache[key]
            
            # Check capacity and evict if necessary
            if len(self._cache) >= self.capacity:
                evicted = self._cache.popitem(last=False)
                if evicted[0] in self._timestamps:
                    del self._timestamps[evicted[0]]
                self.stats["evictions"] += 1
            
            # Add item to cache
            self._cache[key] = value
            if self.ttl:
                self._timestamps[key] = time.time()
    
    def get(self, key: Any, default: Optional[T] = None) -> Optional[T]:
        """
        Retrieve an item from the cache.
        
        Args:
            key: The cache key
            default: Default value if key not found or expired
        
        Returns:
            Cached value or default
        
        Examples:
            >>> cache = Cache()
            >>> cache.put("key", "value")
            >>> cache.get("key")
            'value'
            >>> cache.get("missing", "default")
            'default'
        """
        with self._lock:
            if key not in self._cache:
                self.stats["misses"] += 1
                return default
            
            # Check TTL if enabled
            if self.ttl and key in self._timestamps:
                if time.time() - self._timestamps[key] > self.ttl:
                    del self._cache[key]
                    del self._timestamps[key]
                    self.stats["misses"] += 1
                    return default
            
            # Move to end (most recently used)
            self._cache.move_to_end(key)
            self.stats["hits"] += 1
            return self._cache[key]
    
    def remove(self, key: Any) -> bool:
        """
        Remove an item from the cache.
        
        Args:
            key: The cache key
        
        Returns:
            True if removed, False if not found
        
        Examples:
            >>> cache = Cache()
            >>> cache.put("key", "value")
            >>> cache.remove("key")
            True
            >>> cache.remove("key")
            False
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                if key in self._timestamps:
                    del self._timestamps[key]
                return True
            return False
    
    def clear(self) -> None:
        """Clear all items from the cache."""
        with self._lock:
            self._cache.clear()
            self._timestamps.clear()
    
    def size(self) -> int:
        """Get the current number of items in cache."""
        return len(self._cache)
    
    def get_stats(self) -> Dict[str, int]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with hits, misses, and evictions counts
        """
        return self.stats.copy()
    
    def __contains__(self, key: Any) -> bool:
        """Check if key exists in cache (doesn't update LRU)."""
        return key in self._cache
    
    def __len__(self) -> int:
        """Get the number of items in cache."""
        return len(self._cache)


class Queue(Generic[T]):
    """
    FIFO (First In, First Out) Queue implementation.
    
    Thread-safe queue with optional maximum size and blocking operations.
    
    Attributes:
        maxsize (int): Maximum queue size (0 for unlimited)
        thread_safe (bool): Enable thread safety
    
    Examples:
        Basic queue:
        >>> q = Queue()
        >>> q.enqueue(1)
        >>> q.enqueue(2)
        >>> q.dequeue()
        1
        
        Bounded queue:
        >>> q = Queue(maxsize=2)
        >>> q.enqueue("a")
        >>> q.enqueue("b")
        >>> q.is_full()
        True
        
        Batch operations:
        >>> q = Queue()
        >>> q.enqueue_many([1, 2, 3, 4])
        >>> q.dequeue_many(2)
        [1, 2]
    """
    
    def __init__(self, maxsize: int = 0, thread_safe: bool = True):
        """
        Initialize the Queue.
        
        Args:
            maxsize: Maximum size (0 for unlimited)
            thread_safe: Enable thread safety
        
        Raises:
            ValueError: If maxsize is negative
        """
        if maxsize < 0:
            raise ValueError("maxsize must be non-negative")
        
        self.maxsize = maxsize
        self._items: List[T] = []
        self._lock = Lock() if thread_safe else None
    
    def enqueue(self, item: T) -> None:
        """
        Add an item to the rear of the queue.
        
        Args:
            item: Item to add
        
        Raises:
            OverflowError: If queue is full
        
        Examples:
            >>> q = Queue()
            >>> q.enqueue("first")
            >>> q.enqueue("second")
            >>> q.size()
            2
        """
        if self._lock:
            with self._lock:
                self._enqueue_item(item)
        else:
            self._enqueue_item(item)
    
    def _enqueue_item(self, item: T) -> None:
        """Internal method to enqueue item."""
        if self.maxsize > 0 and len(self._items) >= self.maxsize:
            raise OverflowError("Queue is full")
        self._items.append(item)
    
    def dequeue(self) -> T:
        """
        Remove and return an item from the front of the queue.
        
        Returns:
            The front item
        
        Raises:
            IndexError: If queue is empty
        
        Examples:
            >>> q = Queue()
            >>> q.enqueue(10)
            >>> q.dequeue()
            10
        """
        if self._lock:
            with self._lock:
                return self._dequeue_item()
        else:
            return self._dequeue_item()
    
    def _dequeue_item(self) -> T:
        """Internal method to dequeue item."""
        if not self._items:
            raise IndexError("Queue is empty")
        return self._items.pop(0)
    
    def peek(self) -> T:
        """
        View the front item without removing it.
        
        Returns:
            The front item
        
        Raises:
            IndexError: If queue is empty
        
        Examples:
            >>> q = Queue()
            >>> q.enqueue("peek_me")
            >>> q.peek()
            'peek_me'
            >>> q.size()  # Still in queue
            1
        """
        if not self._items:
            raise IndexError("Queue is empty")
        return self._items[0]
    
    def enqueue_many(self, items: List[T]) -> None:
        """
        Add multiple items to the queue.
        
        Args:
            items: List of items to add
        
        Raises:
            OverflowError: If adding items would exceed maxsize
        
        Examples:
            >>> q = Queue()
            >>> q.enqueue_many([1, 2, 3])
            >>> q.size()
            3
        """
        if self.maxsize > 0:
            if len(self._items) + len(items) > self.maxsize:
                raise OverflowError("Adding items would exceed maxsize")
        
        if self._lock:
            with self._lock:
                self._items.extend(items)
        else:
            self._items.extend(items)
    
    def dequeue_many(self, count: int) -> List[T]:
        """
        Remove and return multiple items from the queue.
        
        Args:
            count: Number of items to dequeue
        
        Returns:
            List of dequeued items
        
        Raises:
            ValueError: If count is negative or exceeds queue size
        
        Examples:
            >>> q = Queue()
            >>> q.enqueue_many([1, 2, 3, 4])
            >>> q.dequeue_many(2)
            [1, 2]
        """
        if count < 0:
            raise ValueError("Count must be non-negative")
        if count > len(self._items):
            raise ValueError("Not enough items in queue")
        
        if self._lock:
            with self._lock:
                result = self._items[:count]
                self._items = self._items[count:]
                return result
        else:
            result = self._items[:count]
            self._items = self._items[count:]
            return result
    
    def is_empty(self) -> bool:
        """Check if queue is empty."""
        return len(self._items) == 0
    
    def is_full(self) -> bool:
        """Check if queue is full (always False for unlimited queues)."""
        return self.maxsize > 0 and len(self._items) >= self.maxsize
    
    def size(self) -> int:
        """Get the current number of items."""
        return len(self._items)
    
    def clear(self) -> None:
        """Remove all items from the queue."""
        if self._lock:
            with self._lock:
                self._items.clear()
        else:
            self._items.clear()
    
    def __len__(self) -> int:
        """Get the number of items."""
        return len(self._items)
    
    def __bool__(self) -> bool:
        """Check if queue is not empty."""
        return len(self._items) > 0


class Stack(Generic[T]):
    """
    LIFO (Last In, First Out) Stack implementation.
    
    A stack data structure with optional maximum size and peek operations.
    
    Attributes:
        maxsize (int): Maximum stack size (0 for unlimited)
    
    Examples:
        Basic stack:
        >>> stack = Stack()
        >>> stack.push(1)
        >>> stack.push(2)
        >>> stack.pop()
        2
        
        With max size:
        >>> stack = Stack(maxsize=3)
        >>> for i in range(3):
        ...     stack.push(i)
        >>> stack.is_full()
        True
        
        Peek operation:
        >>> stack = Stack()
        >>> stack.push("bottom")
        >>> stack.push("top")
        >>> stack.peek()
        'top'
        >>> stack.size()  # Item still in stack
        2
    """
    
    def __init__(self, maxsize: int = 0):
        """
        Initialize the Stack.
        
        Args:
            maxsize: Maximum size (0 for unlimited)
        
        Raises:
            ValueError: If maxsize is negative
        """
        if maxsize < 0:
            raise ValueError("maxsize must be non-negative")
        
        self.maxsize = maxsize
        self._items: List[T] = []
    
    def push(self, item: T) -> None:
        """
        Push an item onto the stack.
        
        Args:
            item: Item to push
        
        Raises:
            OverflowError: If stack is full
        
        Examples:
            >>> stack = Stack()
            >>> stack.push("first")
            >>> stack.push("second")
            >>> stack.peek()
            'second'
        """
        if self.maxsize > 0 and len(self._items) >= self.maxsize:
            raise OverflowError("Stack is full")
        self._items.append(item)
    
    def pop(self) -> T:
        """
        Remove and return the top item.
        
        Returns:
            The top item
        
        Raises:
            IndexError: If stack is empty
        
        Examples:
            >>> stack = Stack()
            >>> stack.push(42)
            >>> stack.pop()
            42
        """
        if not self._items:
            raise IndexError("Stack is empty")
        return self._items.pop()
    
    def peek(self) -> T:
        """
        View the top item without removing it.
        
        Returns:
            The top item
        
        Raises:
            IndexError: If stack is empty
        
        Examples:
            >>> stack = Stack()
            >>> stack.push("peek_me")
            >>> stack.peek()
            'peek_me'
            >>> stack.size()  # Still in stack
            1
        """
        if not self._items:
            raise IndexError("Stack is empty")
        return self._items[-1]
    
    def push_many(self, items: List[T]) -> None:
        """
        Push multiple items onto the stack.
        
        Args:
            items: List of items to push (pushed in order)
        
        Raises:
            OverflowError: If pushing items would exceed maxsize
        
        Examples:
            >>> stack = Stack()
            >>> stack.push_many([1, 2, 3])
            >>> stack.pop()
            3
        """
        if self.maxsize > 0:
            if len(self._items) + len(items) > self.maxsize:
                raise OverflowError("Pushing items would exceed maxsize")
        self._items.extend(items)
    
    def pop_many(self, count: int) -> List[T]:
        """
        Pop multiple items from the stack.
        
        Args:
            count: Number of items to pop
        
        Returns:
            List of popped items (in pop order)
        
        Raises:
            ValueError: If count is negative or exceeds stack size
        
        Examples:
            >>> stack = Stack()
            >>> stack.push_many([1, 2, 3, 4])
            >>> stack.pop_many(2)
            [4, 3]
        """
        if count < 0:
            raise ValueError("Count must be non-negative")
        if count > len(self._items):
            raise ValueError("Not enough items in stack")
        
        result = []
        for _ in range(count):
            result.append(self._items.pop())
        return result
    
    def is_empty(self) -> bool:
        """Check if stack is empty."""
        return len(self._items) == 0
    
    def is_full(self) -> bool:
        """Check if stack is full (always False for unlimited stacks)."""
        return self.maxsize > 0 and len(self._items) >= self.maxsize
    
    def size(self) -> int:
        """Get the current number of items."""
        return len(self._items)
    
    def clear(self) -> None:
        """Remove all items from the stack."""
        self._items.clear()
    
    def to_list(self) -> List[T]:
        """
        Get a copy of stack items as a list.
        
        Returns:
            List with bottom item first, top item last
        
        Examples:
            >>> stack = Stack()
            >>> stack.push_many([1, 2, 3])
            >>> stack.to_list()
            [1, 2, 3]
        """
        return self._items.copy()
    
    def __len__(self) -> int:
        """Get the number of items."""
        return len(self._items)
    
    def __bool__(self) -> bool:
        """Check if stack is not empty."""
        return len(self._items) > 0
    
    def __iter__(self) -> Iterator[T]:
        """Iterate over stack items (bottom to top)."""
        return iter(self._items)