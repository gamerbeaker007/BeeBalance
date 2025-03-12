import pytest

from src.util.large_number_util import format_large_number


@pytest.mark.parametrize("num, expected", [
    (999, "999.00"),        # Just below 1K
    (1000, "1.00K"),        # Exactly 1K
    (1500, "1.50K"),        # Midway in thousands
    (999994, "999.99K"),    # Just below 1M
    (1000000, "1.00M"),     # Exactly 1M
    (2500000, "2.50M"),     # Midway in millions
    (-1000, "-1.00K"),      # Negative thousand
    (-1500000, "-1.50M"),   # Negative million
    (0, "0.00"),            # Zero
    (123.456, "123.46"),    # Small decimal value
    (999.999, "1000.00"),   # Edge rounding at 1K
    (1000500, "1.00M"),     # Slightly over 1M, should still be 1.00M
    (1000499, "1.00M"),     # Check rounding behavior
])
def test_format_large_number(num, expected):
    assert format_large_number(num) == expected
