import data.configuration as c

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

def get_footprint_center(footprint: list[tuple[int, int]]) -> tuple[float, float]:
    xs = [x for x, _ in footprint]
    ys = [y for _, y in footprint]
    center_x = (min(xs) + max(xs)) / 2
    center_y = (min(ys) + max(ys)) / 2
    return (center_x+0.5, center_y+0.5)

def tiles_overlap(pos_a, shape_a, pos_b, shape_b):
    ax, ay = pos_a
    bx, by = pos_b
    for tx_a, ty_a in shape_a:
        rect_a = (
            ax + tx_a * c.BASE_MACHINE_WIDTH,
            ay + ty_a * c.BASE_MACHINE_HEIGHT,
            c.BASE_MACHINE_WIDTH,
            c.BASE_MACHINE_HEIGHT
        )
        for tx_b, ty_b in shape_b:
            rect_b = (
                bx + tx_b * c.BASE_MACHINE_WIDTH,
                by + ty_b * c.BASE_MACHINE_HEIGHT,
                c.BASE_MACHINE_WIDTH,
                c.BASE_MACHINE_HEIGHT
            )
            if (rect_a[0] < rect_b[0] + rect_b[2] and rect_a[0] + rect_a[2] > rect_b[0] and
                rect_a[1] < rect_b[1] + rect_b[3] and rect_a[1] + rect_a[3] > rect_b[1]):
                return True
    return False
