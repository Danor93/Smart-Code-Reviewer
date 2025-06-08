# Example: Code with performance issues

import time

def find_duplicates_slow(numbers):
    """Find duplicates in a list - INEFFICIENT O(n²) version"""
    duplicates = []
    
    # PERFORMANCE ISSUE: Nested loops create O(n²) complexity
    for i in range(len(numbers)):
        for j in range(i + 1, len(numbers)):
            if numbers[i] == numbers[j] and numbers[i] not in duplicates:
                duplicates.append(numbers[i])
    
    return duplicates

def calculate_fibonacci_slow(n):
    """Calculate Fibonacci number - INEFFICIENT recursive version"""
    
    # PERFORMANCE ISSUE: Exponential time complexity due to repeated calculations
    if n <= 1:
        return n
    
    # This recalculates the same values over and over
    return calculate_fibonacci_slow(n - 1) + calculate_fibonacci_slow(n - 2)

def search_in_list_slow(data, target):
    """Search for target in list - INEFFICIENT linear search"""
    
    # PERFORMANCE ISSUE: Linear search in potentially sorted data
    for i, item in enumerate(data):
        if item == target:
            return i
    
    return -1

def process_large_dataset_slow(data):
    """Process large dataset - MEMORY INEFFICIENT version"""
    
    # PERFORMANCE ISSUE: Loading all data into memory at once
    results = []
    
    # PERFORMANCE ISSUE: Creating new lists instead of generators
    squared_data = [x**2 for x in data]
    filtered_data = [x for x in squared_data if x > 100]
    final_data = [x * 2 for x in filtered_data]
    
    # PERFORMANCE ISSUE: Inefficient string concatenation
    result_string = ""
    for item in final_data:
        result_string += str(item) + ","
    
    return result_string

def read_file_slow(filename):
    """Read file - INEFFICIENT I/O version"""
    
    # PERFORMANCE ISSUE: Reading file character by character
    content = ""
    with open(filename, 'r') as f:
        while True:
            char = f.read(1)
            if not char:
                break
            content += char  # Inefficient string concatenation
    
    return content

def sort_dictionary_slow(data_dict):
    """Sort dictionary by values - INEFFICIENT version"""
    
    # PERFORMANCE ISSUE: Converting to list multiple times
    items = list(data_dict.items())
    
    # PERFORMANCE ISSUE: Bubble sort instead of built-in efficient sorting
    n = len(items)
    for i in range(n):
        for j in range(0, n - i - 1):
            if items[j][1] > items[j + 1][1]:
                items[j], items[j + 1] = items[j + 1], items[j]
    
    # PERFORMANCE ISSUE: Rebuilding dictionary inefficiently
    result = {}
    for key, value in items:
        result[key] = value
    
    return result

def calculate_statistics_slow(numbers):
    """Calculate basic statistics - INEFFICIENT multiple iterations"""
    
    # PERFORMANCE ISSUE: Multiple passes through the same data
    total = 0
    for num in numbers:
        total += num
    mean = total / len(numbers)
    
    # Another pass for variance
    variance_sum = 0
    for num in numbers:
        variance_sum += (num - mean) ** 2
    variance = variance_sum / len(numbers)
    
    # Another pass for median
    sorted_numbers = []
    for num in numbers:
        sorted_numbers.append(num)
    
    # PERFORMANCE ISSUE: Inefficient sorting implementation
    for i in range(len(sorted_numbers)):
        for j in range(i + 1, len(sorted_numbers)):
            if sorted_numbers[i] > sorted_numbers[j]:
                sorted_numbers[i], sorted_numbers[j] = sorted_numbers[j], sorted_numbers[i]
    
    median = sorted_numbers[len(sorted_numbers) // 2]
    
    return {
        'mean': mean,
        'variance': variance,
        'median': median
    }

def database_query_slow():
    """Database queries - INEFFICIENT multiple queries"""
    import sqlite3
    
    # PERFORMANCE ISSUE: Opening/closing connection multiple times
    for i in range(100):
        conn = sqlite3.connect('example.db')
        cursor = conn.cursor()
        
        # PERFORMANCE ISSUE: N+1 query problem
        cursor.execute("SELECT id FROM users LIMIT 1")
        user_id = cursor.fetchone()[0]
        
        # Separate query for each user detail
        cursor.execute(f"SELECT name FROM users WHERE id = {user_id}")
        name = cursor.fetchone()
        
        cursor.execute(f"SELECT email FROM users WHERE id = {user_id}")
        email = cursor.fetchone()
        
        conn.close()
        
        # PERFORMANCE ISSUE: Unnecessary sleep in loop
        time.sleep(0.01)

def string_processing_slow(text_list):
    """String processing - INEFFICIENT operations"""
    
    # PERFORMANCE ISSUE: Repeated string concatenation
    result = ""
    
    for text in text_list:
        # PERFORMANCE ISSUE: Multiple regex compilations
        import re
        pattern = re.compile(r'\d+')  # Compiling regex in loop
        
        # PERFORMANCE ISSUE: Inefficient string operations
        cleaned = ""
        for char in text:
            if char.isalnum():
                cleaned += char  # String concatenation in loop
        
        # PERFORMANCE ISSUE: Multiple string operations
        processed = cleaned.lower().strip().replace(' ', '_')
        result += processed + "\n"
    
    return result

# PERFORMANCE ISSUE: Global variable modifications in functions
global_counter = 0

def increment_counter_slow():
    """Increment global counter - INEFFICIENT global access"""
    global global_counter
    
    # PERFORMANCE ISSUE: Unnecessary global variable access
    for i in range(1000):
        global_counter += 1
        global_counter -= 1
        global_counter += 1

if __name__ == "__main__":
    # Test the inefficient functions
    print("Testing inefficient implementations...")
    
    # This will be very slow for large inputs
    large_list = list(range(1000)) * 2  # List with duplicates
    duplicates = find_duplicates_slow(large_list)
    print(f"Found {len(duplicates)} duplicates")
    
    # This will be extremely slow for n > 35
    fib_result = calculate_fibonacci_slow(30)
    print(f"Fibonacci(30) = {fib_result}")
    
    print("All inefficient operations completed!")
