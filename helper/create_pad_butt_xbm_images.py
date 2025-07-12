import os

def make_xbm(width, height, on_pixels):
    """
    Create a simple XBM image as a string.
    on_pixels: list of (x, y) tuples to set as 'on' (1), all others are 0.
    """
    # XBM stores bits LSB first in each byte, row by row
    bytes_per_row = (width + 7) // 8
    data = [0] * (bytes_per_row * height)
    for x, y in on_pixels:
        if 0 <= x < width and 0 <= y < height:
            byte_index = y * bytes_per_row + (x // 8)
            bit_index = x % 8
            data[byte_index] |= (1 << bit_index)
    # Format as C array
    hex_data = ', '.join(f'0x{b:02x}' for b in data)
    return f"""#define pad_width {width}
#define pad_height {height}
static unsigned char pad_bits[] = {{
{hex_data}
}};
"""

def main():
    height = 10
    for i in range(1, 16):
        width = i * 4
        # Example: fill the whole rectangle (all pixels on)
        on_pixels = [(x, y) for y in range(height) for x in range(width)]
        xbm_str = make_xbm(width, height, on_pixels)
        outdir = os.path.join(os.path.dirname(__file__), "png")
        os.makedirs(outdir, exist_ok=True)
        fname = os.path.join(outdir, f"butt_pad_{i}_16.xbm")
        with open(fname, "w") as f:
            f.write(xbm_str)
        print(f"Created {fname}")

if __name__ == "__main__":
    main()