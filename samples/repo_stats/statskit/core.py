"""Descriptive statistics over numeric sequences."""


def mean(values):
    """Return the arithmetic mean of values."""
    if not values:
        raise ValueError("mean() requires at least one value")
    return sum(values) / len(values)


def median(values):
    """Return the median of values.

    BUG: for an even-length input the median is the average of the two middle
    values; this returns the upper middle value instead.
    """
    if not values:
        raise ValueError("median() requires at least one value")
    ordered = sorted(values)
    return ordered[len(ordered) // 2]
