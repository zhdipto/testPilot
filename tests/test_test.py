import io
import asyncio

import pytest
import sys
from unittest.mock import patch

from test import calculate_average, parse_input, main

def test_calculate_average_normal():
    numbers = [1, 2, 3, 4, 5]
    assert calculate_average(numbers) == 3.0

def test_calculate_average_empty():
    numbers = []
    with pytest.raises(ZeroDivisionError):
        calculate_average(numbers)

def test_calculate_average_single_element():
    numbers = [5]
    assert calculate_average(numbers) == 5.0

def test_parse_input_valid():
    args = ["1", "2", "3"]
    assert parse_input(args) == [1, 2, 3]

def test_parse_input_empty():
    args = []
    assert parse_input(args) == []

def test_parse_input_invalid():
    args = ["a", "b", "c"]
    with pytest.raises(ValueError):
        parse_input(args)

def test_parse_input_mixed():
    args = ["1", "a", "3"]
    with pytest.raises(ValueError):
        parse_input(args)

def test_main_valid():
    with patch('sys.argv', ['app.py', '1', '2', '3']):
        with patch('sys.stdout', new=io.StringIO()) as mock_stdout:
            main()
            assert mock_stdout.getvalue() == "Average: 2.00\n"

def test_main_invalid_args():
    with patch('sys.argv', ['app.py']):
        with patch('sys.stdout', new=io.StringIO()) as mock_stdout:
            main()
            assert mock_stdout.getvalue() == "Usage: python app.py <numbers>\n"

def test_main_invalid_input():
    with patch('sys.argv', ['app.py', 'a', 'b', 'c']):
        with pytest.raises(ValueError, match="invalid literal for int"):
            main()

def test_main_async():
    """Synchronous wrapper: verify main() runs correctly (main is not async)."""
    with patch('sys.argv', ['app.py', '1', '2', '3']):
        with patch('sys.stdout', new=io.StringIO()) as mock_stdout:
            main()
            assert mock_stdout.getvalue() == "Average: 2.00\n"

def test_parse_input_mock():
    with patch('sys.argv', ['app.py', '1', '2', '3']):
        numbers = parse_input(sys.argv[1:])
        assert numbers == [1, 2, 3]