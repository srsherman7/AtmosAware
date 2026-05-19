"""Generate simple PNG icons for the PWA manifest.
Run this once: python app/static/icons/generate_icons.py
Requires no external dependencies - creates minimal valid PNGs.
"""
import struct
import zlib


def create_png(width, height, color_rgb):
    """Create a minimal PNG with a solid color and a weather symbol."""

    def make_pixel_data():
        """Create raw pixel data with a simple cloud/sun icon."""
        rows = []
        cx, cy = width // 2, height // 2
        r = width // 3

        for y in range(height):
            row = b'\x00'  # filter byte
            for x in range(width):
                # Distance from center
                dx = x - cx
                dy = y - cy
                dist = (dx * dx + dy * dy) ** 0.5

                # Draw a circle (sun)
                if dist < r:
                    # Gradient from accent color to darker
                    factor = 1 - (dist / r) * 0.3
                    row += bytes([
                        int(color_rgb[0] * factor),
                        int(color_rgb[1] * factor),
                        int(color_rgb[2] * factor),
                        255
                    ])
                elif dist < r + 4:
                    # Border
                    row += bytes([255, 255, 255, 200])
                else:
                    # Background
                    row += bytes([15, 25, 35, 255])
            rows.append(row)
        return b''.join(rows)

    # PNG signature
    signature = b'\x89PNG\r\n\x1a\n'

    # IHDR chunk
    ihdr_data = struct.pack('>IIBBBBB', width, height, 8, 6, 0, 0, 0)
    ihdr = make_chunk(b'IHDR', ihdr_data)

    # IDAT chunk
    raw_data = make_pixel_data()
    compressed = zlib.compress(raw_data)
    idat = make_chunk(b'IDAT', compressed)

    # IEND chunk
    iend = make_chunk(b'IEND', b'')

    return signature + ihdr + idat + iend


def make_chunk(chunk_type, data):
    """Create a PNG chunk."""
    chunk = chunk_type + data
    length = struct.pack('>I', len(data))
    crc = struct.pack('>I', zlib.crc32(chunk) & 0xffffffff)
    return length + chunk + crc


if __name__ == '__main__':
    # RealWeather/AtmosAware accent color: #00b4d8
    accent = (0, 180, 216)

    # 192x192
    png_192 = create_png(192, 192, accent)
    with open('icon-192.png', 'wb') as f:
        f.write(png_192)
    print('Created icon-192.png')

    # 512x512
    png_512 = create_png(512, 512, accent)
    with open('icon-512.png', 'wb') as f:
        f.write(png_512)
    print('Created icon-512.png')
