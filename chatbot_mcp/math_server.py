from __future__ import annotations
from fastmcp import FastMCP
import math
import asyncio

mcp = FastMCP("airth")

def _as_number(x):
    # accept ints and floats or numeric strings ; raise clean errors otherwise
    if isinstance(x, (int, float)):
        return float(x)

    if isinstance(x, str):
        return float(x.strip())
    
    raise TypeError("Expected a number int/float or numeric strings")

# Basic Arithmetic
@mcp.tool()
async def add(a: float, b: float) -> float:
    """Return a + b"""
    return _as_number(a) + _as_number(b)

@mcp.tool()
async def subtract(a: float, b: float) -> float:
    """Return a - b"""
    return _as_number(a) - _as_number(b)

@mcp.tool()
async def multiply(a: float, b: float) -> float:
    """Return a * b"""
    return _as_number(a) * _as_number(b)

@mcp.tool()
async def divide(a: float, b: float) -> float:
    """Return a / b (raises ZeroDivisionError if b is 0)"""
    a_num, b_num = _as_number(a), _as_number(b)
    if b_num == 0:
        raise ValueError("Division by zero")
    return a_num / b_num

# Powers and Roots
@mcp.tool()
async def power(base: float, exponent: float) -> float:
    """Return base ** exponent (a^b)"""
    return math.pow(_as_number(base), _as_number(exponent))

@mcp.tool()
async def square_root(x: float) -> float:
    """Return square root of x (x^0.5). x must be non-negative."""
    num = _as_number(x)
    if num < 0:
        raise ValueError("Square root of negative number")
    return math.sqrt(num)

@mcp.tool()
async def nth_root(base: float, n: float) -> float:
    """Return nth root of base (base^(1/n))"""
    base_num, n_num = _as_number(base), _as_number(n)
    if n_num == 0:
        raise ValueError("nth root exponent cannot be zero")
    if base_num < 0 and n_num % 2 == 0:
        raise ValueError("Even root of negative number")
    return math.pow(base_num, 1 / n_num)

# Trigonometric Functions (radians)
@mcp.tool()
async def sin(x: float) -> float:
    """Return sine of x (x in radians)"""
    return math.sin(_as_number(x))

@mcp.tool()
async def cos(x: float) -> float:
    """Return cosine of x (x in radians)"""
    return math.cos(_as_number(x))

@mcp.tool()
async def tan(x: float) -> float:
    """Return tangent of x (x in radians)"""
    return math.tan(_as_number(x))

@mcp.tool()
async def degrees_to_radians(degrees: float) -> float:
    """Convert degrees to radians"""
    return math.radians(_as_number(degrees))

@mcp.tool()
async def radians_to_degrees(radians: float) -> float:
    """Convert radians to degrees"""
    return math.degrees(_as_number(radians))

# Logarithms and Exponentials
@mcp.tool()
async def log(x: float) -> float:
    """Return natural logarithm (ln) of x. x must be positive."""
    num = _as_number(x)
    if num <= 0:
        raise ValueError("Logarithm of non-positive number")
    return math.log(num)

@mcp.tool()
async def log10(x: float) -> float:
    """Return base-10 logarithm of x. x must be positive."""
    num = _as_number(x)
    if num <= 0:
        raise ValueError("Logarithm of non-positive number")
    return math.log10(num)

@mcp.tool()
async def exp(x: float) -> float:
    """Return e^x (exponential function)"""
    return math.exp(_as_number(x))

# Statistics
@mcp.tool()
async def average(numbers: list[float]) -> float:
    """Return arithmetic mean of a list of numbers"""
    nums = [_as_number(n) for n in numbers]
    return sum(nums) / len(nums)

@mcp.tool()
async def sum_numbers(numbers: list[float]) -> float:
    """Return sum of a list of numbers"""
    return sum(_as_number(n) for n in numbers)

if __name__ == "__main__":
    mcp.run()

