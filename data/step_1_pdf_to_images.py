import fitz  # pymupdf
import os

PDF_FOLDER = "imports"    # PDF'lerin olduğu klasör
IMG_FOLDER = "samples"    # PNG'lerin kaydedileceği klasör

pdf_files = sorted([f for f in os.listdir(PDF_FOLDER) if f.endswith(".pdf")])
print(f"Found {len(pdf_files)} PDF files")

for pdf_name in pdf_files:
    doc = fitz.open(os.path.join(PDF_FOLDER, pdf_name))
    page = doc[0]
    mat = fitz.Matrix(300/72, 300/72)  # 300 DPI
    pix = page.get_pixmap(matrix=mat)
    out_name = pdf_name.replace(".pdf", ".png")
    out_path = os.path.join(IMG_FOLDER, out_name)
    pix.save(out_path)
    print(f"  Saved: {out_name}  ({pix.width} x {pix.height} px)")
    doc.close()

print("Done!")