"""
cache_images.py - pre-decode and pre-resize the DiaMOS leaves once.

Training decodes every full-resolution JPEG on every epoch, which makes the
run I/O-bound: the four DataLoader workers saturate while the GPU idles at
under 40%. This writes 256-short-side copies once so later epochs decode a
tiny file instead of a multi-megapixel one.

Short side 256 rather than a forced 256x256 square: the DiaMOS originals are
3968x2976 and 2976x3968, so squaring them squashes one axis by a third. That
destroyed the shape cue curl depends on (recall 0.909 -> 0.727). This matches
what transforms.Resize(256) does, so the cached pipeline sees the same
geometry the uncached one did.

Run from inside ml/ with the venv active: python cache_images.py
"""

import shutil
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from PIL import Image, ImageOps

SOURCE_DIR = Path(__file__).parent / "data" / "Pear" / "leaves"
CACHE_DIR = Path(__file__).parent / "data" / "Pear" / "leaves_256"
TARGET_SHORT = 256
JPEG_QUALITY = 95


def find_images(source_dir):
    """Return (source_path, destination_path) pairs, mirroring the class tree."""
    pairs = []
    for class_dir in sorted(p for p in source_dir.iterdir() if p.is_dir()):
        for image_path in sorted(class_dir.iterdir()):
            if not image_path.is_file():
                continue
            # AppleDouble metadata files end in .jpg but are not images.
            if image_path.name.startswith("._"):
                continue
            if image_path.suffix.lower() not in {".jpg", ".jpeg", ".png"}:
                continue
            destination = CACHE_DIR / class_dir.name / f"{image_path.stem}.jpg"
            pairs.append((image_path, destination))
    return pairs


def process_one(pair):
    """Decode, orient, resize short side to 256, and write. Returns (ok, path)."""
    source, destination = pair
    try:
        with Image.open(source) as image:
            # Cameras often store the sensor image unrotated plus an EXIF
            # orientation tag. PIL does NOT apply it automatically, so a
            # portrait photo would arrive sideways. Apply it explicitly.
            image = ImageOps.exif_transpose(image)

            # Guarantee three channels. A stray greyscale or CMYK file would
            # otherwise produce a tensor with the wrong channel count and
            # blow up inside the model rather than here.
            image = image.convert("RGB")

            # Scale the SHORT side to 256 and let the long side follow, so the
            # aspect ratio survives. RandomCrop(224) then has slack along the
            # long axis, which is where the crop augmentation comes from.
            width, height = image.size
            if width < height:
                new_size = (TARGET_SHORT, round(height * TARGET_SHORT / width))
            else:
                new_size = (round(width * TARGET_SHORT / height), TARGET_SHORT)

            # LANCZOS rather than BILINEAR: downsampling 12x throws away most
            # of the pixels, and LANCZOS preserves high-frequency detail far
            # better. Fine texture is the entire slug-vs-spot problem.
            image = image.resize(new_size, Image.LANCZOS)

            image.save(destination, "JPEG", quality=JPEG_QUALITY)
        return True, str(source)
    except Exception as error:
        return False, f"{source}: {error}"


def main():
    if not SOURCE_DIR.exists():
        sys.exit(f"Source directory not found: {SOURCE_DIR}")

    if CACHE_DIR.exists():
        answer = input(f"{CACHE_DIR} exists. Delete and rebuild? [y/N] ")
        if answer.strip().lower() != "y":
            sys.exit("Left alone.")
        shutil.rmtree(CACHE_DIR)

    pairs = find_images(SOURCE_DIR)
    print(f"Found {len(pairs)} images under {SOURCE_DIR}")

    # Create every destination directory up front. Doing this inside the
    # workers would have several processes racing to mkdir the same path.
    for _, destination in pairs:
        destination.parent.mkdir(parents=True, exist_ok=True)

    start = time.time()
    failures = []

    # Decoding is CPU-bound, so processes rather than threads: Python's GIL
    # would serialise threads doing this work.
    with ProcessPoolExecutor() as pool:
        for index, (ok, info) in enumerate(pool.map(process_one, pairs, chunksize=16), start=1):
            if not ok:
                failures.append(info)
            if index % 250 == 0:
                print(f"  {index}/{len(pairs)}")

    elapsed = time.time() - start
    written = len(pairs) - len(failures)
    print(f"\nWrote {written} images in {elapsed:.1f}s")

    if failures:
        print(f"\n{len(failures)} failures:")
        for failure in failures:
            print(f"  {failure}")

    print("\nPer-class counts in the cache:")
    for class_dir in sorted(p for p in CACHE_DIR.iterdir() if p.is_dir()):
        count = len(list(class_dir.iterdir()))
        print(f"  {class_dir.name:<8} {count:>5}")

    total_bytes = sum(p.stat().st_size for p in CACHE_DIR.rglob("*.jpg"))
    print(f"\nCache size: {total_bytes / 1024 / 1024:.1f} MB")


if __name__ == "__main__":
    main()
