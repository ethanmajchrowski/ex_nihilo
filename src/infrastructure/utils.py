def interpolate(value, range_a_start, range_a_end, value_a, value_b):
    if value <= range_a_start:
        return value_a
    elif value >= range_a_end:
        return value_b
    else:
        # Normalize value to 0-1 within the input range
        t = (value - range_a_start) / (range_a_end - range_a_start)
        # Interpolate linearly between value_a and value_b
        return value_a + t * (value_b - value_a)

def interpolate_color(value, range_start, range_end, color_a, color_b):
    def clamp(x): return max(0, min(255, int(x)))

    r = clamp(interpolate(value, range_start, range_end, color_a[0], color_b[0]))
    g = clamp(interpolate(value, range_start, range_end, color_a[1], color_b[1]))
    b = clamp(interpolate(value, range_start, range_end, color_a[2], color_b[2]))
    return (r, g, b)