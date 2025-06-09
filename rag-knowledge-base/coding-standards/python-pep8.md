# Python PEP 8 Style Guide

## Code Layout

### Indentation

- Use 4 spaces per indentation level
- Never mix tabs and spaces
- Continuation lines should align wrapped elements either vertically or using a hanging indent

### Maximum Line Length

- Limit all lines to a maximum of 79 characters
- For flowing long blocks of text, limit to 72 characters

### Blank Lines

- Surround top-level function and class definitions with two blank lines
- Method definitions inside a class are surrounded by a single blank line
- Extra blank lines may be used sparingly to separate groups of related functions

## Import Guidelines

### Import Order

1. Standard library imports
2. Related third party imports
3. Local application/library specific imports

### Import Statements

- Imports should usually be on separate lines
- Imports are always put at the top of the file
- Absolute imports are recommended over relative imports

Example:

```python
import os
import sys

from third_party import lib

from . import local_module
```

## Naming Conventions

### Function and Variable Names

- Use lowercase with words separated by underscores: `function_name`, `variable_name`
- Be descriptive: `user_count` instead of `n`

### Class Names

- Use CapWords convention: `MyClass`, `HTTPServer`
- Exception names should end in "Error": `ValueError`, `ConnectionError`

### Constants

- Use all uppercase with underscores: `MAX_OVERFLOW`, `TOTAL_COUNT`

### Private Attributes

- Use single leading underscore for internal use: `_internal_var`
- Use double leading underscore for name mangling: `__private_var`

## Documentation Strings

### Function Docstrings

```python
def function(param1: str, param2: int) -> bool:
    """Brief description of function.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: Description of when this is raised
    """
    pass
```

### Class Docstrings

```python
class MyClass:
    """Brief description of class.

    Attributes:
        attribute1: Description of attribute1
        attribute2: Description of attribute2
    """
```

## Programming Recommendations

### Comparisons

- Use `is` and `is not` for comparing to None: `if value is None:`
- Use `isinstance()` instead of comparing types directly
- For sequences (strings, lists, tuples), use the fact that empty sequences are false

### Error Handling

- Be specific in exceptions you catch
- Don't use bare `except:` clauses
- Use `finally` clauses for cleanup code

### Function Annotations

- Use type hints for function parameters and return values
- Import from `typing` module for complex types

Example:

```python
from typing import List, Dict, Optional

def process_items(items: List[str]) -> Dict[str, int]:
    """Process a list of items and return counts."""
    return {item: len(item) for item in items}
```
