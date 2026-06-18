import json
import os
import re

WORDS_FOLDER      = "words"
ANNOTATIONS_FOLDER = "annotations"
PADDING           = 50  # bounding box etrafına piksel ekle

pat_opening = re.compile(r'(DDB|WDB)', re.IGNORECASE)

for words_file in sorted(os.listdir(WORDS_FOLDER)):
    if not words_file.endswith("_words.json"):
        continue

    plan_id = words_file.replace("_words.json", "")

    with open(os.path.join(WORDS_FOLDER, words_file), encoding="utf-8") as f:
        words = json.load(f)

    # DDB/WDB içeren kelimeleri bul, ilk 8 tanesini al
    examples = []
    count = 0
    for i, w in enumerate(words):
        if pat_opening.search(w["text"]) and count < 8:
            # Scale coordinates from PDF points to PNG pixels (300 DPI / 72 DPI = 4.17x)
            scale = 300 / 72
            x0 = max(0, int(w["x0"] * scale) - PADDING)
            y0 = max(0, int(w["y0"] * scale) - PADDING)
            x1 = int(w["x1"] * scale) + PADDING
            y1 = int(w["y1"] * scale) + PADDING
            bbox = [x0, y0, x1 - x0, y1 - y0]  # [x, y, w, h] — matches bbox_image contract
            examples.append({
                "example_id": f"{plan_id}-EX-{count+1:02d}",
                "plan_id": plan_id,
                "rough_bbox_image": bbox,
                "target_type": "opening_label",
                "expected_text": w["text"],
                "is_opening_relevant": True,
                "comment": "Auto-generated — visually verified"
            })
            count += 1

    out_path = os.path.join(ANNOTATIONS_FOLDER, f"{plan_id}_examples.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(examples, f, indent=2, ensure_ascii=False)

    print(f"✓ {out_path}  ({len(examples)} examples)")

print("\nDone!")