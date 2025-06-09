# Python Performance Optimization Guidelines

## Algorithm Complexity

### Time Complexity Analysis

- Always consider Big O notation when reviewing algorithms
- O(1) > O(log n) > O(n) > O(n log n) > O(n²) > O(2ⁿ)
- Review nested loops carefully for O(n²) or worse complexity

### Common Performance Issues

```python
# BAD: O(n²) algorithm for finding duplicates
def find_duplicates_slow(lst):
    duplicates = []
    for i in range(len(lst)):
        for j in range(i+1, len(lst)):
            if lst[i] == lst[j]:
                duplicates.append(lst[i])
    return duplicates

# GOOD: O(n) algorithm using set
def find_duplicates_fast(lst):
    seen = set()
    duplicates = set()
    for item in lst:
        if item in seen:
            duplicates.add(item)
        else:
            seen.add(item)
    return list(duplicates)
```

## Data Structures Selection

### Choose the Right Data Structure

- Use `set()` for membership testing (O(1) vs O(n) for lists)
- Use `collections.deque` for frequent insertions at both ends
- Use `collections.defaultdict` to avoid key existence checks
- Use `collections.Counter` for counting operations

### Performance Comparison Examples

```python
# BAD: Using list for membership testing
def check_membership_slow(items, targets):
    valid_items = []
    for item in items:
        if item in targets:  # O(n) for each check
            valid_items.append(item)
    return valid_items

# GOOD: Using set for membership testing
def check_membership_fast(items, targets):
    target_set = set(targets)  # Convert once
    return [item for item in items if item in target_set]  # O(1) for each check
```

## Memory Optimization

### Generator Expressions vs List Comprehensions

```python
# BAD: Creates entire list in memory
squares = [x**2 for x in range(1000000)]
total = sum(squares)

# GOOD: Generator expression - memory efficient
squares = (x**2 for x in range(1000000))
total = sum(squares)
```

### String Concatenation

```python
# BAD: String concatenation in loop (O(n²))
result = ""
for item in items:
    result += str(item) + ","

# GOOD: Join method (O(n))
result = ",".join(str(item) for item in items)
```

## Function and Method Optimization

### Avoid Repeated Calculations

```python
# BAD: Repeated expensive calculation
def process_items(items):
    processed = []
    for item in items:
        if expensive_calculation() > threshold:
            processed.append(item * expensive_calculation())
    return processed

# GOOD: Calculate once, reuse
def process_items(items):
    processed = []
    calc_result = expensive_calculation()
    if calc_result > threshold:
        for item in items:
            processed.append(item * calc_result)
    return processed
```

### Use Built-in Functions

```python
# BAD: Manual implementation
def find_max(numbers):
    max_val = numbers[0]
    for num in numbers[1:]:
        if num > max_val:
            max_val = num
    return max_val

# GOOD: Built-in function (optimized in C)
def find_max(numbers):
    return max(numbers)
```

## I/O Operations

### Batch Operations

```python
# BAD: Multiple database queries
def get_user_data(user_ids):
    users = []
    for user_id in user_ids:
        user = db.query(f"SELECT * FROM users WHERE id = {user_id}")
        users.append(user)
    return users

# GOOD: Single batch query
def get_user_data(user_ids):
    placeholders = ",".join(["?" for _ in user_ids])
    query = f"SELECT * FROM users WHERE id IN ({placeholders})"
    return db.query(query, user_ids)
```

### File I/O Optimization

```python
# BAD: Reading file line by line
def process_large_file(filename):
    results = []
    with open(filename, 'r') as f:
        for line in f:
            results.append(process_line(line))
    return results

# GOOD: Reading in chunks
def process_large_file(filename):
    results = []
    with open(filename, 'r') as f:
        while True:
            chunk = f.readlines(8192)  # Read in chunks
            if not chunk:
                break
            for line in chunk:
                results.append(process_line(line))
    return results
```

## Caching and Memoization

### Use functools.lru_cache for Expensive Functions

```python
from functools import lru_cache

# Expensive recursive function
@lru_cache(maxsize=128)
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
```

### Custom Caching for Database Queries

```python
class DatabaseCache:
    def __init__(self, max_size=1000):
        self.cache = {}
        self.max_size = max_size

    def get_user(self, user_id):
        if user_id in self.cache:
            return self.cache[user_id]

        user = db.query(f"SELECT * FROM users WHERE id = {user_id}")
        if len(self.cache) >= self.max_size:
            # Remove oldest entry
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]

        self.cache[user_id] = user
        return user
```

## Profiling and Measurement

### Use cProfile for Performance Analysis

```python
import cProfile
import pstats

def profile_function():
    profiler = cProfile.Profile()
    profiler.enable()

    # Your code here
    expensive_function()

    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(10)  # Top 10 functions
```

### Memory Profiling with memory_profiler

```python
from memory_profiler import profile

@profile
def memory_intensive_function():
    # Monitor memory usage line by line
    large_list = [i for i in range(1000000)]
    return sum(large_list)
```

## Async Programming for I/O Bound Tasks

### Use asyncio for Concurrent I/O

```python
import asyncio
import aiohttp

# BAD: Sequential HTTP requests
def fetch_urls_sync(urls):
    results = []
    for url in urls:
        response = requests.get(url)
        results.append(response.text)
    return results

# GOOD: Concurrent HTTP requests
async def fetch_urls_async(urls):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_url(session, url) for url in urls]
        return await asyncio.gather(*tasks)

async def fetch_url(session, url):
    async with session.get(url) as response:
        return await response.text()
```

## Database Query Optimization

### Use Indexes and Query Optimization

```python
# BAD: N+1 query problem
def get_posts_with_authors():
    posts = Post.query.all()
    for post in posts:
        post.author = User.query.get(post.user_id)  # N additional queries
    return posts

# GOOD: Join or eager loading
def get_posts_with_authors():
    return Post.query.join(User).all()  # Single query with join
```

### Pagination for Large Datasets

```python
# BAD: Loading all records
def get_all_users():
    return User.query.all()  # Could be millions of records

# GOOD: Pagination
def get_users_paginated(page=1, per_page=50):
    return User.query.paginate(page=page, per_page=per_page)
```

## Code Review Checklist for Performance

1. **Algorithm Complexity**: Check for nested loops and inefficient algorithms
2. **Data Structure Usage**: Verify appropriate data structures are used
3. **Memory Management**: Look for memory leaks and excessive memory usage
4. **I/O Operations**: Check for batching and async patterns where appropriate
5. **Database Queries**: Review for N+1 problems and missing indexes
6. **Caching**: Identify opportunities for caching expensive operations
7. **Profiling**: Ensure performance-critical code has been profiled
