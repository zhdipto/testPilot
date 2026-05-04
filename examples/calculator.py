"""Sample source file — use this to try out TestPilot's generate command.

Run:
    testpilot generate examples/calculator.py -o tests/
"""


def add(a: float, b: float) -> float:
    """Return the sum of *a* and *b*."""
    return a + b


def subtract(a: float, b: float) -> float:
    """Return the difference of *a* and *b*."""
    return a - b


def multiply(a: float, b: float) -> float:
    """Return the product of *a* and *b*."""
    return a * b


def divide(a: float, b: float) -> float:
    """Return *a* divided by *b*.

    Raises:
        ZeroDivisionError: if *b* is zero.
    """
    if b == 0:
        raise ZeroDivisionError("Cannot divide by zero.")
    return a / b


def power(base: float, exp: float) -> float:
    """Return *base* raised to the power of *exp*."""
    return base ** exp
