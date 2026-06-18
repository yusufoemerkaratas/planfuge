# Data Notes

## Available Plan Files
- SP_U1_0001.png
- SP_U1_0002.png
- SP_U1_0003.png
- SP_U1_0004.png
- SP_U1_0005.png
- SP_U1_0006.png

## Path
All plan images are located under: data/pages/<plan_id>.png

## Notes
- Resolution: 300 DPI
- Format: PNG
- Source: PDF floor plans (Untergeschoss 1)
- Floor: U1 (Basement Level 1)

## PDF Availability (Issue #23)
Original searchable/vector-based PDFs are available in `data/imports/` (6 files).
PyMuPDF extracts words directly — no OCR needed.
Word-level bounding boxes are stored in `data/words/<plan_id>_words.json`.

### Label counts across all 6 plans (from words.json)
| Label | Count |
|-------|-------|
| WDB   | 512   |
| DDB   | 187   |
| UZD   | 112   |
| HSI   | 10    |
| BDP   | 0     |

## Red Markup Clarification
Red cloud markings in the plans are revision/comment annotations only.
They are NOT the target openings.
All openings (DDB and WDB labels) must be detected regardless of color.
