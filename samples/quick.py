#!/usr/bin/env python3
"""Sample script for testing py-power-profile."""

import time
import math


def fibonacci(n):
    """Calculate the nth Fibonacci number."""
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


def heavy_computation():
    """Perform some heavy computation."""
    result = 0
    for i in range(1000):
        result += math.sin(i) * math.cos(i)
    return result


def light_operation():
    """Perform a light operation."""
    return 42


def main():
    """Main function with various operations."""
    print("Starting sample script...")
    
    # Light operation
    result1 = light_operation()
    print(f"Light operation result: {result1}")
    
    # Heavy computation
    result2 = heavy_computation()
    print(f"Heavy computation result: {result2}")
    
    # Fibonacci calculation
    result3 = fibonacci(10)
    print(f"Fibonacci(10): {result3}")
    
    # Sleep a bit
    time.sleep(0.1)
    
    print("Sample script completed!")


if __name__ == "__main__":
    main() 