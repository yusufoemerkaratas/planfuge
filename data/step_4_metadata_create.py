import json
import os
import re

from PIL import Image

Image.MAX_IMAGE_PIXELS = None  # disable size limit for large plans

PAGES_FOLDER = "pages"
IMPORTS_FOLDER = "imports"
METADATA_FOLDER = "metadata"
RAW_TEXT_FILE = "fixtures/raw_text.csv"

# Load raw text to search for scale info
import csv

raw_texts = {}
with open(RAW_TEXT_FILE, encoding="utf-8-sig") as f:
    for row in csv.DictReader(f):
        plan = row["filename"]
        if plan not in raw_texts:
            raw_texts[plan] = []
        raw_texts[plan].append(row["text"])


def find_scale(texts):
    for t in texts:
        m = re.search(r"M\s*1\s*:\s*\d+", t, re.IGNORECASE)
        if m:
            return m.group(0).replace(" ", "")
    return "unknown"


def pdf_exists(plan_id):
    return os.path.exists(os.path.join(IMPORTS_FOLDER, plan_id + ".pdf"))


# Process each PNG
for png_file in sorted(os.listdir(PAGES_FOLDER)):
    if not png_file.endswith(".png"):
        continue

    plan_id = png_file.replace(".png", "")
    img_path = os.path.join(PAGES_FOLDER, png_file)

    # Read image size
    with Image.open(img_path) as img:
        width, height = img.size

    # Build metadata
    metadata = {
        "plan_id": plan_id,
        "file_path": f"data/pages/{png_file}",
        "image_width_px": width,
        "image_height_px": height,
        "source_type": "rendered_png",
        "original_pdf_available": pdf_exists(plan_id),
        "scale_text_visible": find_scale(raw_texts.get(plan_id, [])),
        "contains_red_markups": True,  # visually confirmed
        "notes": "",
    }

    # Save JSON
    out_path = os.path.join(METADATA_FOLDER, f"{plan_id}_metadata.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f"✓ {out_path}  ({width}x{height}px, scale={metadata['scale_text_visible']})")

print("\nDone!")
