#!/usr/bin/env python3
"""Upscale/enhance an image so it's high quality enough for a hero/landing background.

Usage: python upscale_image.py <input_path> <output_path> [--scale 2]

Tries Real-ESRGAN (https://github.com/xinntao/Real-ESRGAN) via its
`realesrgan-ncnn-vulkan` CLI binary first, since it gives genuinely sharper
results on photographic images than simple interpolation. If that binary
isn't available, falls back to a high-quality Lanczos resize via Pillow and
says so explicitly in the output — this is a real quality difference, not an
implementation detail to hide.
"""
import argparse
import shutil
import subprocess
import sys


def try_realesrgan(input_path: str, output_path: str, scale: int) -> bool:
    binary = shutil.which("realesrgan-ncnn-vulkan")
    if not binary:
        return False
    result = subprocess.run(
        [binary, "-i", input_path, "-o", output_path, "-s", str(scale)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"realesrgan-ncnn-vulkan failed: {result.stderr.strip()}", file=sys.stderr)
        return False
    return True


def fallback_lanczos(input_path: str, output_path: str, scale: int) -> None:
    from PIL import Image

    img = Image.open(input_path)
    new_size = (img.width * scale, img.height * scale)
    upscaled = img.resize(new_size, Image.LANCZOS)
    upscaled.save(output_path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_path")
    parser.add_argument("output_path")
    parser.add_argument("--scale", type=int, default=2)
    args = parser.parse_args()

    if try_realesrgan(args.input_path, args.output_path, args.scale):
        print(f"Upscaled with Real-ESRGAN ({args.scale}x): {args.output_path}")
        return

    try:
        fallback_lanczos(args.input_path, args.output_path, args.scale)
    except ImportError:
        print(
            "Neither realesrgan-ncnn-vulkan nor Pillow is available.\n"
            "Install one of:\n"
            "  Real-ESRGAN (better quality): https://github.com/xinntao/Real-ESRGAN/releases\n"
            "  Pillow (fallback, lower quality): pip install pillow\n"
            "Not proceeding — do not fabricate a processed image.",
            file=sys.stderr,
        )
        sys.exit(1)

    print(
        f"NOTE: Real-ESRGAN not found, used Lanczos resize fallback ({args.scale}x) "
        f"instead — lower quality than Real-ESRGAN would give. "
        f"Install realesrgan-ncnn-vulkan for better results: {args.output_path}"
    )


if __name__ == "__main__":
    main()
