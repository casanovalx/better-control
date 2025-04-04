#!/usr/bin/env python3

import warnings
import contextlib

@contextlib.contextmanager
def suppress_specific_warnings(category, message_pattern=None):
    """Context manager to suppress specific warnings.
    
    Args:
        category: Warning category to suppress (e.g., DeprecationWarning)
        message_pattern: Optional string pattern to match in warning message
    """
    # Define a filter function that checks both category and message
    def custom_filter(message, category_match, filename, lineno, file=None, line=None):
        if issubclass(category_match, category):
            if message_pattern is None or message_pattern in str(message):
                return None  # Suppress the warning
        return message  # Show the warning
    
    # Save the old showwarning function
    old_showwarning = warnings.showwarning
    
    try:
        # Replace with our custom filter
        warnings.showwarning = custom_filter
        yield
    finally:
        # Restore the original function
        warnings.showwarning = old_showwarning
