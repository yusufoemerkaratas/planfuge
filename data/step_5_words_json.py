import json
import os

import fitz

PDF_FOLDER = "imports"
WORDS_FOLDER = "words"
os.makedirs(WORDS_FOLDER, exist_ok=True)

for pdf_name in sorted(os.listdir(PDF_FOLDER)):
    if not pdf_name.endswith(".pdf"):
        continue

    plan_id = pdf_name.replace(".pdf", "")
    doc = fitz.open(os.path.join(PDF_FOLDER, pdf_name))
    page = doc[0]

    words = []
    for w in page.get_text("words"):
        x0, y0, x1, y1, text, *_ = w
        words.append(
            {
                "text": text.strip(),
                "x0": round(x0, 2),
                "y0": round(y0, 2),
                "x1": round(x1, 2),
                "y1": round(y1, 2),
                "page": 1,
            }
        )

    out_path = os.path.join(WORDS_FOLDER, f"{plan_id}_words.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(words, f, indent=2, ensure_ascii=False)

    print(f"✓ {out_path}  ({len(words)} words)")
    doc.close()

print("\nDone!")
