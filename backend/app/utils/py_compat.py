"""
Python 3.14 Compatibility Module

Handles any compatibility issues between different Python versions.
"""

import sys
from typing import Any, Dict

# Python version info
PYTHON_VERSION = sys.version_info
PYTHON_MAJOR = PYTHON_VERSION.major
PYTHON_MINOR = PYTHON_VERSION.minor
PYTHON_MICRO = PYTHON_VERSION.micro

# Version compatibility flags
IS_PYTHON_310_OR_HIGHER = PYTHON_VERSION >= (3, 10)
IS_PYTHON_311_OR_HIGHER = PYTHON_VERSION >= (3, 11)
IS_PYTHON_312_OR_HIGHER = PYTHON_VERSION >= (3, 12)
IS_PYTHON_313_OR_HIGHER = PYTHON_VERSION >= (3, 13)
IS_PYTHON_314_OR_HIGHER = PYTHON_VERSION >= (3, 14)


def get_type_hints_compat(obj: Any, globalns: Dict = None, localns: Dict = None) -> Dict:
    """
    Get type hints with Python 3.14 compatibility.
    
    Args:
        obj: Object to get type hints from
        globalns: Global namespace
        localns: Local namespace
        
    Returns:
        Dict: Type hints
    """
    try:
        from typing import get_type_hints
        return get_type_hints(obj, globalns=globalns, localns=localns)
    except Exception:
        # Fallback for edge cases
        return getattr(obj, '__annotations__', {})


def get_origin_compat(tp: Any) -> Any:
    """
    Get origin of generic type with Python 3.14 compatibility.
    
    Args:
        tp: Type to get origin from
        
    Returns:
        Any: Origin type
    """
    try:
        from typing import get_origin
        return get_origin(tp)
    except Exception:
        return getattr(tp, '__origin__', None)


def get_args_compat(tp: Any) -> tuple:
    """
    Get arguments of generic type with Python 3.14 compatibility.
    
    Args:
        tp: Type to get args from
        
    Returns:
        tuple: Type arguments
    """
    try:
        from typing import get_args
        return get_args(tp)
    except Exception:
        return getattr(tp, '__args__', ())


def is_union_type(tp: Any) -> bool:
    """
    Check if type is a Union type with Python 3.14 compatibility.
    
    Args:
        tp: Type to check
        
    Returns:
        bool: True if Union type
    """
    try:
        from types import UnionType
        return isinstance(tp, UnionType)
    except ImportError:
        # UnionType not available in older Python versions
        from typing import Union, get_origin
        return get_origin(tp) is Union


# Dictionary for Python version-specific settings
PYTHON_VERSION_SETTINGS = {
    "3.10": {
        "use_match": False,
        "use_union_syntax": False,
        "use_annotated": True,
    },
    "3.11": {
        "use_match": True,
        "use_union_syntax": False,
        "use_annotated": True,
    },
    "3.12": {
        "use_match": True,
        "use_union_syntax": True,
        "use_annotated": True,
    },
    "3.13": {
        "use_match": True,
        "use_union_syntax": True,
        "use_annotated": True,
        "use_override": True,
    },
    "3.14": {
        "use_match": True,
        "use_union_syntax": True,
        "use_annotated": True,
        "use_override": True,
        "use_performance_optimizations": True,
    },
}


def get_version_settings() -> Dict[str, bool]:
    """
    Get Python version-specific settings.
    
    Returns:
        Dict: Version-specific settings
    """
    version_key = f"{PYTHON_MAJOR}.{PYTHON_MINOR}"
    return PYTHON_VERSION_SETTINGS.get(version_key, {})


def log_version_info() -> None:
    """Log Python version information."""
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"Python Version: {PYTHON_MAJOR}.{PYTHON_MINOR}.{PYTHON_MICRO}")
    logger.info(f"Python Implementation: {sys.implementation.name}")
    logger.info(f"Python Executable: {sys.executable}")
