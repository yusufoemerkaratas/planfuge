# OCR Labels to Physical CAD Geometry — Research Spike

## Problem

The OCR bounding box locates label text, not the opening represented by nearby drawing lines. Replacing it blindly would corrupt spatial checks, so a refinement must require geometric evidence and preserve the original box when evidence is incomplete.

## Approaches considered

1. **Probabilistic Hough lines** detect long line segments after edge detection. This is useful for rasterized CAD linework and rotated shapes, but requires segment pairing and strong filtering in dense drawings. See the [OpenCV Hough Line Transform documentation](https://docs.opencv.org/4.x/d9/db0/tutorial_hough_lines.html).
2. **Contours and connected components** can recover closed shapes, then rank them by distance, containment, size, and aspect ratio relative to the OCR label. Contour hierarchy can help reject nested text glyphs. See the [OpenCV contours documentation](https://docs.opencv.org/4.x/d4/d73/tutorial_py_contours_begin.html).
3. **Orthogonal run detection** searches locally for long horizontal and vertical dark-pixel runs surrounding the label. It is dependency-free and deterministic, but only supports axis-aligned rectangular geometry.

## Prototype

`src/image/physical_bbox_prototype.py` implements option 3 using NumPy:

- crop a configurable search window around the OCR box;
- threshold dark pixels;
- mask the OCR box so text strokes do not become geometry;
- find long horizontal and vertical runs on both sides of the label center;
- return `[x, y, width, height]` only when all four sides exist;
- otherwise return `None` and keep the original candidate geometry unchanged.

The tests demonstrate alignment to a synthetic CAD rectangle and safe refusal when the geometry is incomplete.

## Recommended production direction

Use a two-stage proposal and scoring pipeline:

1. Generate nearby segments with Canny + probabilistic Hough and closed-shape proposals with contours.
2. Score proposals using label-to-shape distance, containment, parallel/perpendicular line support, expected size range, and overlap with red markup.
3. Keep both `bbox_image` (OCR evidence) and a separate `physical_bbox_image`; never overwrite provenance.
4. Return no physical box below a calibrated confidence threshold.
5. Evaluate against manually annotated label-to-shape pairs before pipeline integration.

Suggested metrics are match precision/recall, physical-box IoU, center error in pixels, and refusal rate. Precision should be prioritized because a wrong physical association is less visible than a missing one.

## Spike limitations

- axis-aligned rectangles only;
- raster dark-line threshold only;
- no dashed, curved, circular, or rotated geometry;
- no disambiguation when multiple nearby rectangles are complete;
- no validation on representative annotated PlanFuge sheets;
- intentionally not integrated into the MVP candidate pipeline.
