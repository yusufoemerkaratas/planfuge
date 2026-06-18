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

## Manually Checked Annotation Examples (Issue #22)

Reference examples for evaluating the CV candidate extraction pipeline are stored in `data/annotations/<plan_id>_examples.json`.

| Plan        | Total examples | Opening-relevant | Non-relevant |
|-------------|---------------|-----------------|--------------|
| SP_U1_0001  | 8             | 6               | 2            |
| SP_U1_0002  | 8             | 6               | 2            |
| SP_U1_0003  | 8             | 6               | 2            |
| SP_U1_0004  | 8             | 6               | 2            |
| SP_U1_0005  | 7             | 5               | 2            |
| SP_U1_0006  | 5             | 3               | 2            |

Each entry contains: `example_id`, `plan_id`, `rough_bbox_image` [x0, y0, x1, y1], `target_type`, `expected_text`, `is_opening_relevant`, `comment`.
Bounding box coordinates are derived from `data/words/<plan_id>_words.json`.
Visualizations are available in `data/samples/<plan_id>_annotated.png`.

## Red Markup Clarification
Red cloud markings in the plans are revision/comment annotations only.
They are NOT the target openings.
All openings (DDB and WDB labels) must be detected regardless of color.
