import fitz
import pandas as pd
import os

PDF_FOLDER = "imports"
OUTPUT_FILE = "fixtures/raw_text.csv"

all_lines = []

for pdf_name in sorted(os.listdir(PDF_FOLDER)):
    if not pdf_name.endswith(".pdf"):
        continue

    doc = fitz.open(os.path.join(PDF_FOLDER, pdf_name))
    page = doc[0]
    page_w = page.rect.width
    page_h = page.rect.height

    for block in page.get_text("blocks"):
        x0, y0, x1, y1, text, _, block_type = block
        if block_type != 0:
            continue
        for line in text.strip().split("\n"):
            line = line.strip()
            if line:
                all_lines.append({
                    "filename": pdf_name.replace(".pdf", ""),
                    "text": line,
                    "x0": round(x0, 2),
                    "y0": round(y0, 2),
                    "page_width": round(page_w, 2),
                    "page_height": round(page_h, 2),
                })
    doc.close()

df = pd.DataFrame(all_lines)
df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")
print(f"Done! {len(df)} lines saved to {OUTPUT_FILE}")