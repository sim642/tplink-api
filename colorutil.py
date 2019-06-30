import colorsys

INV_PHI = 0.618033988749895


def random_det(i, s=1, v=1):
    # https://martin.ankerl.com/2009/12/09/how-to-create-random-colors-programmatically/
    h = (INV_PHI * i) % 1
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return (r, g, b)


def rgb_to_hex(r, g, b):
    return f"#{int(r * 255):02X}{int(g * 255):02X}{int(b * 255):02X}"