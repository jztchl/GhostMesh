import os

from PIL import Image


def compress_image_under_300kb(input_path: str, output_path: str, max_size_kb=300):
    img = Image.open(input_path)
    if img.format == "PNG":
        img = img.convert("RGB")

    quality = 95
    while True:
        img.save(output_path, format="JPEG", quality=quality, optimize=True)

        size_kb = os.path.getsize(output_path) / 1024
        if size_kb <= max_size_kb or quality <= 10:
            break
        quality -= 5
    return output_path
