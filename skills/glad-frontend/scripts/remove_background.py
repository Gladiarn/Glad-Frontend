#!/usr/bin/env python3
"""Remove the background from a hero/product image, producing a transparent PNG.

Usage: python remove_background.py <input_path> <output_path>

Requires the `rembg` package (https://github.com/danielgatis/rembg, MIT licensed,
widely used open-source background removal). If it isn't installed, this prints
install instructions and exits non-zero rather than failing silently or
fabricating a result.

Note: on first run, rembg downloads its model weights (~176MB, U2-Net) from its
GitHub releases. This is expected, one-time, and normal for this tool.
"""
import sys


def main():
    if len(sys.argv) != 3:
        print("Usage: python remove_background.py <input_path> <output_path>", file=sys.stderr)
        sys.exit(1)

    input_path, output_path = sys.argv[1], sys.argv[2]

    try:
        from rembg import remove
        from PIL import Image
    except ImportError:
        print(
            "rembg (and Pillow) are required but not installed in this environment.\n"
            "Install with:\n"
            "  pip install rembg[cpu] pillow\n"
            "(use rembg[gpu] instead if a CUDA GPU is available and preferred)\n"
            "Not proceeding — do not fabricate a processed image.",
            file=sys.stderr,
        )
        sys.exit(1)

    with open(input_path, "rb") as f:
        input_bytes = f.read()

    output_bytes = remove(input_bytes)

    with open(output_path, "wb") as f:
        f.write(output_bytes)

    img = Image.open(output_path)
    print(f"Background removed: {output_path} ({img.width}x{img.height}, mode={img.mode})")


if __name__ == "__main__":
    main()
