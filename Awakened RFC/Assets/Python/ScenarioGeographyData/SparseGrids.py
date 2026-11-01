# Compact authored grids. Coordinates use north-to-south row order. Python 2.4.


def expand(width, height, planes):
    """Expand default values and inclusive (row, first x, last x) spans once."""
    result = []
    for plane in planes:
        if isinstance(plane, int):
            if plane < 0 or plane >= len(result):
                raise ValueError("Invalid shared geography plane")
            result.append(result[plane])
            continue
        default, values = plane
        rows = [[default] * width for y in range(height)]
        occupied = set()
        for value, spans in values:
            for y, first, last in spans:
                if not (0 <= y < height and 0 <= first <= last < width):
                    raise ValueError("Geography span is outside the profile grid")
                for x in range(first, last + 1):
                    if (x, y) in occupied:
                        raise ValueError("Overlapping geography spans")
                    occupied.add((x, y))
                    rows[y][x] = value
        result.append(tuple(tuple(row) for row in rows))
    return tuple(result)
