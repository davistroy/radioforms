# Python General Coding Rules: Best Practices for AI-Assisted Development

## Core Philosophy

**The #1 Rule**: Explicit is better than implicit. Simple is better than complex.

### Python Fundamental Principles (PEP 20 - The Zen of Python)

1. **Beautiful is better than ugly**
2. **Explicit is better than implicit**
3. **Simple is better than complex**
4. **Complex is better than complicated**
5. **Flat is better than nested**
6. **Sparse is better than dense**
7. **Readability counts**
8. **Special cases aren't special enough to break the rules**
9. **Although practicality beats purity**
10. **Errors should never pass silently**
11. **Unless explicitly silenced**
12. **In the face of ambiguity, refuse the temptation to guess**
13. **There should be one-- and preferably only one --obvious way to do it**
14. **Now is better than never**
15. **Although never is often better than *right* now**
16. **If the implementation is hard to explain, it's a bad idea**
17. **If the implementation is easy to explain, it may be a good idea**

## 🔧 Essential Setup & Configuration

### Always Use Context7 MCP

**CRITICAL**: Before implementing ANY Python feature:
```python
# Always check latest documentation with context7
# Use: context7 /python/cpython for official Python docs
# Use: context7 /python/peps for Python Enhancement Proposals
```

### Project Initialization Checklist

1. **Use Virtual Environments**
```bash
# Create virtual environment
python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# ALWAYS use virtual environments - no exceptions
```

2. **Project Structure**
```
project-name/
├── src/
│   └── project_name/      # Use underscores in package names
│       ├── __init__.py
│       ├── main.py
│       ├── models/
│       │   └── __init__.py
│       ├── services/
│       │   └── __init__.py
│       └── utils/
│           └── __init__.py
├── tests/
│   ├── __init__.py
│   ├── unit/
│   │   └── __init__.py
│   └── integration/
│       └── __init__.py
├── docs/
├── requirements.txt        # Production dependencies
├── requirements-dev.txt    # Development dependencies
├── setup.py               # For installable packages
├── pyproject.toml         # Modern Python packaging
├── README.md
├── .gitignore
├── .env.example
└── venv/                  # Virtual environment (git-ignored)
```

3. **pyproject.toml Configuration**
```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "project-name"
version = "0.1.0"
description = "A brief description"
readme = "README.md"
requires-python = ">=3.10"
dependencies = [
    "requests>=2.28.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "black>=22.0",
    "mypy>=1.0",
    "ruff>=0.1.0",
    "pre-commit>=3.0",
]

[tool.black]
line-length = 88
target-version = ['py310']

[tool.ruff]
line-length = 88
select = ["E", "F", "I", "N", "UP", "S", "B", "A", "C4", "DTZ", "RUF"]
ignore = ["E501"]  # Line too long (handled by black)

[tool.mypy]
python_version = "3.10"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

## 🚨 Python Specific Anti-Patterns

### 1. Mutable Default Arguments
```python
# ❌ AVOID: Mutable default arguments
def append_to_list(item, target_list=[]):
    target_list.append(item)
    return target_list

# ✅ DO: Use None as default
def append_to_list(item, target_list=None):
    if target_list is None:
        target_list = []
    target_list.append(item)
    return target_list
```

### 2. Bare Except Clauses
```python
# ❌ AVOID: Catching all exceptions
try:
    risky_operation()
except:
    pass  # Silently ignores ALL errors

# ✅ DO: Catch specific exceptions
try:
    risky_operation()
except (ValueError, TypeError) as e:
    logger.error(f"Operation failed: {e}")
    raise  # Re-raise if you can't handle it
```

### 3. Using `is` for Value Comparison
```python
# ❌ AVOID: Using 'is' for values
if x is 5:
    print("x is 5")

# ✅ DO: Use '==' for value comparison
if x == 5:
    print("x equals 5")

# Use 'is' only for singletons
if x is None:
    print("x is None")
```

### 4. Not Using Context Managers
```python
# ❌ AVOID: Manual resource management
file = open('data.txt')
data = file.read()
file.close()  # Might not be called if exception occurs

# ✅ DO: Use context managers
with open('data.txt') as file:
    data = file.read()
# File is automatically closed
```

### 5. Class Variables vs Instance Variables
```python
# ❌ AVOID: Mutable class variables
class User:
    permissions = []  # Shared across all instances!

# ✅ DO: Initialize in __init__
class User:
    def __init__(self):
        self.permissions = []  # Unique to each instance
```

## 📋 Development Best Practices

### 1. Type Hints (PEP 484)
```python
from typing import List, Optional, Dict, Union, Tuple
from dataclasses import dataclass

# Use type hints for all functions
def process_data(
    items: List[str], 
    max_length: int = 100
) -> Dict[str, int]:
    """Process list of items and return frequency count."""
    result: Dict[str, int] = {}
    for item in items:
        if len(item) <= max_length:
            result[item] = result.get(item, 0) + 1
    return result

# Use dataclasses for data structures
@dataclass
class User:
    id: int
    name: str
    email: str
    is_active: bool = True
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
```

### 2. Error Handling
```python
# Custom exceptions
class AppError(Exception):
    """Base application exception"""
    pass

class ValidationError(AppError):
    """Raised when validation fails"""
    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(f"{field}: {message}")

class ConfigurationError(AppError):
    """Raised when configuration is invalid"""
    pass

# Using exceptions properly
def validate_email(email: str) -> str:
    """Validate and normalize email address."""
    if not email or '@' not in email:
        raise ValidationError('email', 'Invalid email format')
    
    # Normalize
    return email.lower().strip()

# Context-aware error handling
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)

@contextmanager
def error_handler(operation: str):
    """Context manager for consistent error handling."""
    try:
        yield
    except ValidationError:
        raise  # Re-raise validation errors
    except Exception as e:
        logger.exception(f"Error during {operation}")
        raise AppError(f"Failed to {operation}: {str(e)}") from e
```

### 3. Configuration Management
```python
# config.py
import os
from pathlib import Path
from typing import Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class DatabaseConfig:
    host: str
    port: int
    name: str
    user: str
    password: str
    
    @property
    def url(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"

@dataclass
class Config:
    debug: bool
    secret_key: str
    database: DatabaseConfig
    log_level: str
    
    @classmethod
    def from_env(cls) -> "Config":
        """Create config from environment variables."""
        # Required variables
        required = ['SECRET_KEY', 'DB_HOST', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']
        missing = [var for var in required if not os.getenv(var)]
        if missing:
            raise ConfigurationError(f"Missing required environment variables: {', '.join(missing)}")
        
        return cls(
            debug=os.getenv('DEBUG', 'false').lower() == 'true',
            secret_key=os.getenv('SECRET_KEY'),
            database=DatabaseConfig(
                host=os.getenv('DB_HOST'),
                port=int(os.getenv('DB_PORT', 5432)),
                name=os.getenv('DB_NAME'),
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASSWORD'),
            ),
            log_level=os.getenv('LOG_LEVEL', 'INFO'),
        )

# Usage
config = Config.from_env()
```

### 4. Logging Best Practices
```python
import logging
import sys
from pathlib import Path

def setup_logging(level: str = "INFO", log_file: Optional[Path] = None):
    """Configure logging for the application."""
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(console_handler)
    
    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Adjust third-party loggers
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('asyncio').setLevel(logging.WARNING)

# Per-module logger
logger = logging.getLogger(__name__)

# Usage
def process_request(request_id: str):
    logger.info(f"Processing request {request_id}")
    try:
        # ... process ...
        logger.debug(f"Request {request_id} processed successfully")
    except Exception as e:
        logger.exception(f"Failed to process request {request_id}")
        raise
```

## 🧪 Testing Guidelines

### 1. Use pytest
```python
# test_user_service.py
import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from src.services.user_service import UserService
from src.models.user import User
from src.exceptions import ValidationError

class TestUserService:
    """Test cases for UserService."""
    
    @pytest.fixture
    def user_service(self):
        """Create UserService instance with mocked dependencies."""
        db_mock = Mock()
        email_service_mock = Mock()
        return UserService(db=db_mock, email_service=email_service_mock)
    
    @pytest.fixture
    def sample_user(self):
        """Create sample user for testing."""
        return User(
            id=1,
            name="Test User",
            email="test@example.com",
            created_at=datetime.now()
        )
    
    def test_create_user_success(self, user_service, sample_user):
        """Test successful user creation."""
        # Arrange
        user_service.db.save.return_value = sample_user
        
        # Act
        result = user_service.create_user(
            name="Test User",
            email="test@example.com"
        )
        
        # Assert
        assert result.id == 1
        assert result.email == "test@example.com"
        user_service.email_service.send_welcome_email.assert_called_once_with(
            "test@example.com"
        )
    
    def test_create_user_invalid_email(self, user_service):
        """Test user creation with invalid email."""
        with pytest.raises(ValidationError) as exc_info:
            user_service.create_user(
                name="Test User",
                email="invalid-email"
            )
        
        assert exc_info.value.field == "email"
        assert "Invalid email format" in str(exc_info.value)
    
    @pytest.mark.parametrize("email,expected", [
        ("test@example.com", True),
        ("invalid-email", False),
        ("", False),
        (None, False),
    ])
    def test_is_valid_email(self, user_service, email, expected):
        """Test email validation with various inputs."""
        assert user_service.is_valid_email(email) == expected
```

### 2. Test Organization
```python
# conftest.py - Shared fixtures
import pytest
from pathlib import Path
from typing import Generator

@pytest.fixture
def temp_data_dir(tmp_path: Path) -> Path:
    """Create temporary data directory for tests."""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    return data_dir

@pytest.fixture
def mock_database() -> Generator[Mock, None, None]:
    """Provide mock database connection."""
    with patch('src.database.get_connection') as mock:
        yield mock

# Use fixtures in tests
def test_file_processor(temp_data_dir, mock_database):
    """Test file processing with temporary directory."""
    test_file = temp_data_dir / "test.csv"
    test_file.write_text("header1,header2\nvalue1,value2")
    
    processor = FileProcessor(data_dir=temp_data_dir, db=mock_database)
    result = processor.process_file("test.csv")
    
    assert result.rows_processed == 1
    mock_database.insert.assert_called_once()
```

## 📦 Dependency Management

### 1. Requirements Files
```bash
# requirements.txt - Production only
requests>=2.28.0,<3.0.0
sqlalchemy>=2.0.0,<3.0.0
pydantic>=2.0.0,<3.0.0

# requirements-dev.txt - Development
-r requirements.txt
pytest>=7.0.0
pytest-cov>=4.0.0
black>=22.0.0
mypy>=1.0.0
ruff>=0.1.0
pre-commit>=3.0.0
```

### 2. Dependency Rules
```python
# Before adding ANY package:
# 1. Check if Python stdlib has it
# 2. Check package health: https://pypi.org/project/{package}/
# 3. Look at last update date
# 4. Check security: pip audit
# 5. Consider alternatives

# Prefer standard library
from pathlib import Path  # Instead of os.path
from dataclasses import dataclass  # Instead of attrs
from functools import lru_cache  # Instead of caching libraries
from unittest.mock import Mock  # Instead of mock package
import tomllib  # Python 3.11+ instead of toml package
```

## 🏗️ Code Organization Patterns

### 1. Module Organization
```python
# user_service.py - Single responsibility modules
"""User service for handling user operations.

This module provides functionality for creating, updating,
and managing users in the system.
"""

from typing import List, Optional
from datetime import datetime
import logging

from .models import User
from .exceptions import ValidationError, NotFoundError
from .database import get_db_connection

logger = logging.getLogger(__name__)

__all__ = ['UserService', 'get_user_service']  # Explicit exports


class UserService:
    """Service for managing users."""
    
    def __init__(self, db_connection=None):
        self._db = db_connection or get_db_connection()
    
    def get_user(self, user_id: int) -> User:
        """Get user by ID.
        
        Args:
            user_id: The user's ID
            
        Returns:
            User object
            
        Raises:
            NotFoundError: If user doesn't exist
        """
        user = self._db.query(User).filter_by(id=user_id).first()
        if not user:
            raise NotFoundError(f"User {user_id} not found")
        return user


# Module-level function for common access pattern
_service_instance = None

def get_user_service() -> UserService:
    """Get singleton UserService instance."""
    global _service_instance
    if _service_instance is None:
        _service_instance = UserService()
    return _service_instance
```

### 2. Class Design
```python
# Follow SOLID principles
from abc import ABC, abstractmethod
from typing import Protocol

# Interface segregation
class Readable(Protocol):
    """Protocol for readable sources."""
    def read(self) -> str:
        ...

class Writable(Protocol):
    """Protocol for writable destinations."""
    def write(self, data: str) -> None:
        ...

# Single responsibility
class FileReader:
    """Handles reading from files."""
    
    def __init__(self, filepath: Path):
        self.filepath = filepath
    
    def read(self) -> str:
        """Read entire file content."""
        with open(self.filepath, 'r') as f:
            return f.read()

# Open/closed principle
class DataProcessor(ABC):
    """Abstract base for data processors."""
    
    @abstractmethod
    def process(self, data: str) -> str:
        """Process data and return result."""
        pass

class UppercaseProcessor(DataProcessor):
    """Convert data to uppercase."""
    
    def process(self, data: str) -> str:
        return data.upper()

class PrefixProcessor(DataProcessor):
    """Add prefix to data."""
    
    def __init__(self, prefix: str):
        self.prefix = prefix
    
    def process(self, data: str) -> str:
        return f"{self.prefix}{data}"
```

## 🔍 Performance Optimization

### 1. Use Built-in Functions and Comprehensions
```python
# ❌ AVOID: Manual loops for simple operations
result = []
for x in items:
    if x > 0:
        result.append(x * 2)

# ✅ DO: Use comprehensions
result = [x * 2 for x in items if x > 0]

# ✅ DO: Use generator for memory efficiency
result = (x * 2 for x in items if x > 0)

# ✅ DO: Use built-in functions
from itertools import compress, chain, groupby
from functools import reduce
from operator import add

# Efficient filtering
active_users = list(compress(users, [u.is_active for u in users]))

# Efficient grouping
from itertools import groupby
users_by_role = {
    role: list(users) 
    for role, users in groupby(sorted_users, key=lambda u: u.role)
}
```

### 2. Caching and Memoization
```python
from functools import lru_cache, cache
from typing import Dict, Tuple
import time

# Simple caching for pure functions
@lru_cache(maxsize=128)
def expensive_calculation(n: int) -> int:
    """Cache results of expensive calculations."""
    time.sleep(1)  # Simulate expensive operation
    return n ** 2

# For Python 3.9+, use @cache for unlimited cache
@cache
def fibonacci(n: int) -> int:
    if n < 2:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Manual caching for more control
class DataCache:
    """Cache with TTL support."""
    
    def __init__(self, ttl_seconds: int = 300):
        self._cache: Dict[str, Tuple[any, float]] = {}
        self._ttl = ttl_seconds
    
    def get(self, key: str) -> Optional[any]:
        """Get value from cache if not expired."""
        if key in self._cache:
            value, timestamp = self._cache[key]
            if time.time() - timestamp < self._ttl:
                return value
            else:
                del self._cache[key]
        return None
    
    def set(self, key: str, value: any) -> None:
        """Set value in cache with current timestamp."""
        self._cache[key] = (value, time.time())
```

## 🐛 Debugging Best Practices

### 1. Use Python Debugger
```python
# Interactive debugging
import pdb

def problematic_function(data):
    result = []
    for item in data:
        # Set breakpoint
        pdb.set_trace()  # or breakpoint() in Python 3.7+
        processed = process_item(item)
        result.append(processed)
    return result

# Better: Use logging for production
import logging

logger = logging.getLogger(__name__)

def better_function(data):
    result = []
    logger.debug(f"Processing {len(data)} items")
    
    for i, item in enumerate(data):
        try:
            processed = process_item(item)
            result.append(processed)
        except Exception as e:
            logger.error(f"Failed to process item {i}: {e}", exc_info=True)
            raise
    
    logger.info(f"Successfully processed {len(result)} items")
    return result
```

### 2. Profiling
```python
# Profile code performance
import cProfile
import pstats
from functools import wraps

def profile(func):
    """Decorator to profile function execution."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        profiler = cProfile.Profile()
        profiler.enable()
        result = func(*args, **kwargs)
        profiler.disable()
        
        stats = pstats.Stats(profiler)
        stats.sort_stats('cumulative')
        stats.print_stats(10)  # Top 10 functions
        
        return result
    return wrapper

# Memory profiling
from memory_profiler import profile as memory_profile

@memory_profile
def memory_intensive_function():
    # Function that uses lots of memory
    large_list = [i for i in range(1000000)]
    return sum(large_list)
```

## 🏗️ Advanced Patterns

### 1. Context Managers
```python
from contextlib import contextmanager
import tempfile
import shutil
from typing import Generator

@contextmanager
def temporary_directory() -> Generator[Path, None, None]:
    """Create and cleanup temporary directory."""
    temp_dir = Path(tempfile.mkdtemp())
    try:
        yield temp_dir
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

# Usage
with temporary_directory() as temp_dir:
    temp_file = temp_dir / "data.txt"
    temp_file.write_text("temporary data")
    process_file(temp_file)
# Directory is automatically cleaned up

# Class-based context manager
class DatabaseTransaction:
    """Context manager for database transactions."""
    
    def __init__(self, connection):
        self.connection = connection
        self.transaction = None
    
    def __enter__(self):
        self.transaction = self.connection.begin()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.transaction.commit()
        else:
            self.transaction.rollback()
        return False  # Don't suppress exceptions
```

### 2. Decorators
```python
from functools import wraps
import time
import logging
from typing import Callable, Any

def retry(max_attempts: int = 3, delay: float = 1.0):
    """Retry decorator with exponential backoff."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        wait_time = delay * (2 ** attempt)
                        logging.warning(
                            f"{func.__name__} failed (attempt {attempt + 1}/{max_attempts}), "
                            f"retrying in {wait_time}s: {e}"
                        )
                        time.sleep(wait_time)
            
            raise last_exception
        return wrapper
    return decorator

# Usage
@retry(max_attempts=3, delay=1.0)
def unstable_network_call():
    """Make a network call that might fail."""
    response = requests.get("https://api.example.com/data")
    response.raise_for_status()
    return response.json()
```

## 🎯 Python-Specific Best Practices

### 1. String Formatting
```python
# ❌ AVOID: Old-style formatting
message = "Hello %s, you have %d messages" % (name, count)

# ❌ AVOID: .format() (unless required for compatibility)
message = "Hello {}, you have {} messages".format(name, count)

# ✅ DO: Use f-strings (Python 3.6+)
message = f"Hello {name}, you have {count} messages"

# ✅ DO: Multi-line f-strings
sql_query = f"""
    SELECT id, name, email
    FROM users
    WHERE created_at > '{start_date}'
    AND status = '{status}'
"""
```

### 2. Path Handling
```python
from pathlib import Path

# ❌ AVOID: os.path
import os
file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'file.txt')

# ✅ DO: Use pathlib
file_path = Path(__file__).parent.parent / 'data' / 'file.txt'

# Path operations
if file_path.exists():
    content = file_path.read_text()
    
# Create directories
data_dir = Path('output') / 'data'
data_dir.mkdir(parents=True, exist_ok=True)

# Iterate over files
for python_file in Path('src').rglob('*.py'):
    print(f"Found: {python_file}")
```

### 3. Data Classes and Named Tuples
```python
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime

@dataclass
class Task:
    """Represent a task with automatic methods."""
    id: int
    title: str
    completed: bool = False
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    
    def mark_complete(self) -> None:
        """Mark task as completed."""
        self.completed = True

# For immutable data
from typing import NamedTuple

class Point(NamedTuple):
    """Immutable point in 2D space."""
    x: float
    y: float
    
    def distance_from_origin(self) -> float:
        """Calculate distance from origin."""
        return (self.x ** 2 + self.y ** 2) ** 0.5
```

## 🏁 Pre-Production Checklist

Before considering any Python application production-ready:

- [ ] All functions have type hints
- [ ] Docstrings for all public modules, classes, and functions
- [ ] No bare except clauses
- [ ] All mutable default arguments replaced with None
- [ ] Configuration loaded from environment variables
- [ ] Logging configured (no print statements)
- [ ] Unit test coverage > 80%
- [ ] Integration tests for critical paths
- [ ] Requirements pinned to specific versions
- [ ] Security scan passed (pip audit)
- [ ] Code formatted with Black
- [ ] Linting passed (ruff/pylint)
- [ ] Type checking passed (mypy)
- [ ] Error tracking configured
- [ ] Secrets not hardcoded
- [ ] README with setup instructions
- [ ] API documentation (if applicable)

## 💡 Python-Specific Tips

### Always Remember:

1. **Zen of Python**: Run `import this` and follow it
2. **PEP 8**: Follow Python style guide
3. **Type Hints**: Use them everywhere
4. **Virtual Environments**: Always use them
5. **Context Managers**: Use for resource management
6. **Generators**: Use for memory efficiency
7. **List Comprehensions**: More Pythonic than loops
8. **F-strings**: Modern string formatting
9. **Pathlib**: Modern path handling
10. **Dataclasses**: Modern data structures

### Common Gotchas:

- Mutable default arguments
- Late binding closures
- Integer division changed in Python 3
- Unicode handling differences
- Relative imports in packages
- Name mangling with double underscores
- Generator exhaustion
- Modifying lists while iterating
- Python 2 vs 3 differences (always use Python 3)

Remember: Always check the latest documentation using context7 MCP before implementing any feature!