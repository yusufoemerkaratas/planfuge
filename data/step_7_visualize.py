import json
import os

from PIL import Image, ImageDraw

PAGES_FOLDER = "pages"
ANNOTATIONS_FOLDER = "annotations"
OUTPUT_FOLDER = "samples"  # görsel çıktılar buraya

Image.MAX_IMAGE_PIXELS = None

for ann_file in sorted(os.listdir(ANNOTATIONS_FOLDER)):
    if not ann_file.endswith("_examples.json"):
        continue

    plan_id = ann_file.replace("_examples.json", "")
    png_path = os.path.join(PAGES_FOLDER, f"{plan_id}.png")

    if not os.path.exists(png_path):
        continue

    with open(os.path.join(ANNOTATIONS_FOLDER, ann_file), encoding="utf-8") as f:
        examples = json.load(f)

    # Resmi küçült (yoksa çok büyük olur)
    img = Image.open(png_path)
    scale = 0.15
    small = img.resize((int(img.width * scale), int(img.height * scale)))
    draw = ImageDraw.Draw(small)

    for ex in examples:
        bbox = ex["rough_bbox_image"]
        # Koordinatları küçültülmüş boyuta göre ayarla
        x0 = int(bbox[0] * scale)
        y0 = int(bbox[1] * scale)
        x1 = int(bbox[2] * scale)
        y1 = int(bbox[3] * scale)
        draw.rectangle([x0, y0, x1, y1], outline="blue", width=3)
        draw.text((x0, y0 - 15), ex["example_id"].split("-")[-1], fill="blue")

    out_path = os.path.join(OUTPUT_FOLDER, f"{plan_id}_annotated.png")
    small.save(out_path)
    print(f"✓ {out_path}")

print("\nDone! ")
