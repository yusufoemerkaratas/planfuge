from typing import Any


def compute_iou(
    bbox1: list[float] | tuple[float, ...], bbox2: list[float] | tuple[float, ...]
) -> float:
    """
    Calculate the Intersection over Union (IoU) of two bounding boxes in [x, y, w, h] format.
    """
    x1, y1, w1, h1 = bbox1
    x2, y2, w2, h2 = bbox2

    # Convert to x0, y0, x1, y1
    x0_1, y0_1, x1_1, y1_1 = x1, y1, x1 + w1, y1 + h1
    x0_2, y0_2, x1_2, y1_2 = x2, y2, x2 + w2, y2 + h2

    # Intersection coordinate limits
    int_x0 = max(x0_1, x0_2)
    int_y0 = max(y0_1, y0_2)
    int_x1 = min(x1_1, x1_2)
    int_y1 = min(y1_1, y1_2)

    int_w = max(0.0, int_x1 - int_x0)
    int_h = max(0.0, int_y1 - int_y0)

    intersection_area = int_w * int_h
    area1 = w1 * h1
    area2 = w2 * h2
    union_area = area1 + area2 - intersection_area

    if union_area <= 0:
        return 0.0

    return intersection_area / union_area


def is_center_inside(
    bbox_inner: list[float] | tuple[float, ...], bbox_outer: list[float] | tuple[float, ...]
) -> bool:
    """
    Check if the center point of bbox_inner [x, y, w, h] lies inside bbox_outer [x, y, w, h].
    """
    x_in, y_in, w_in, h_in = bbox_inner
    x_out, y_out, w_out, h_out = bbox_outer

    cx = x_in + w_in / 2.0
    cy = y_in + h_in / 2.0

    return (x_out <= cx <= x_out + w_out) and (y_out <= cy <= y_out + h_out)


def compare_candidates_to_examples(
    candidates: list[dict[str, Any]], examples: list[dict[str, Any]], iou_threshold: float = 0.1
) -> dict[str, Any]:
    """
    Compare generated candidates against manual examples.
    """
    matched_relevant = []
    missed_relevant = []
    matched_non_relevant = []
    unmatched_non_relevant = []

    # Track which candidates have matched any example
    matched_candidate_ids = set()

    for ex in examples:
        ex_id = ex.get("example_id")
        ex_bbox = ex.get("rough_bbox_image")
        is_relevant = ex.get("is_opening_relevant", True)

        best_candidate = None
        best_overlap_val = -1.0

        for cand in candidates:
            cand_bbox = cand.get("bbox_image")
            if not cand_bbox or not ex_bbox:
                continue

            iou = compute_iou(cand_bbox, ex_bbox)
            center_cand_in_ex = is_center_inside(cand_bbox, ex_bbox)
            center_ex_in_cand = is_center_inside(ex_bbox, cand_bbox)

            is_matched = (iou >= iou_threshold) or center_cand_in_ex or center_ex_in_cand

            if is_matched:
                # We rank match quality primarily by IoU, but any match counts
                overlap_score = iou if iou > 0 else 0.05
                if overlap_score > best_overlap_val:
                    best_overlap_val = overlap_score
                    best_candidate = cand

        if best_candidate:
            matched_candidate_ids.add(best_candidate.get("candidate_id"))
            match_entry = {
                "example_id": ex_id,
                "candidate_id": best_candidate.get("candidate_id"),
                "expected_text": ex.get("expected_text"),
                "raw_text": best_candidate.get("raw_text"),
            }
            if is_relevant:
                matched_relevant.append(match_entry)
            else:
                matched_non_relevant.append(match_entry)
        else:
            if is_relevant:
                missed_relevant.append(
                    {"example_id": ex_id, "expected_text": ex.get("expected_text")}
                )
            else:
                unmatched_non_relevant.append(
                    {"example_id": ex_id, "expected_text": ex.get("expected_text")}
                )

    # Unmatched candidates
    unmatched_candidates = []
    for cand in candidates:
        if cand.get("candidate_id") not in matched_candidate_ids:
            unmatched_candidates.append(cand)

    return {
        "matched_relevant": matched_relevant,
        "missed_relevant": missed_relevant,
        "matched_non_relevant": matched_non_relevant,
        "unmatched_non_relevant": unmatched_non_relevant,
        "unmatched_candidates": unmatched_candidates,
    }
