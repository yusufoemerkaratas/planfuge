"""Research prototype for aligning OCR boxes to nearby orthogonal CAD lines."""

from __future__ import annotations

import numpy as np


def _longest_true_run(values: np.ndarray) -> int:
    longest = 0
    current = 0
    for value in values:
        if value:
            current += 1
            longest = max(longest, current)
        else:
            current = 0
    return longest


def _nearest_sides(indices: list[int], center: float) -> tuple[int, int] | None:
    before = [index for index in indices if index < center]
    after = [index for index in indices if index > center]
    if not before or not after:
        return None
    return max(before), min(after)


def refine_bbox_to_nearby_lines(
    grayscale: np.ndarray,
    ocr_bbox: list[int],
    search_radius: int = 80,
    dark_threshold: int = 80,
    min_line_length: int = 20,
) -> list[int] | None:
    """Return a nearby orthogonal line rectangle as ``[x, y, width, height]``.

    This spike supports axis-aligned raster drawings only. It masks OCR strokes,
    searches for long dark runs on all four sides, and returns ``None`` when a
    complete surrounding rectangle cannot be demonstrated.
    """
    if grayscale.ndim != 2 or len(ocr_bbox) != 4:
        raise ValueError("expected a grayscale image and [x, y, width, height] bbox")

    x, y, width, height = ocr_bbox
    image_height, image_width = grayscale.shape
    search_x0 = max(0, x - search_radius)
    search_y0 = max(0, y - search_radius)
    search_x1 = min(image_width, x + width + search_radius + 1)
    search_y1 = min(image_height, y + height + search_radius + 1)
    dark = grayscale[search_y0:search_y1, search_x0:search_x1] < dark_threshold

    mask_x0 = max(0, x - search_x0)
    mask_y0 = max(0, y - search_y0)
    mask_x1 = min(dark.shape[1], mask_x0 + width)
    mask_y1 = min(dark.shape[0], mask_y0 + height)
    dark[mask_y0:mask_y1, mask_x0:mask_x1] = False

    horizontal_lines = [
        row for row in range(dark.shape[0]) if _longest_true_run(dark[row, :]) >= min_line_length
    ]
    vertical_lines = [
        column for column in range(dark.shape[1]) if _longest_true_run(dark[:, column]) >= min_line_length
    ]
    horizontal_sides = _nearest_sides(horizontal_lines, mask_y0 + height / 2)
    vertical_sides = _nearest_sides(vertical_lines, mask_x0 + width / 2)
    if horizontal_sides is None or vertical_sides is None:
        return None

    top, bottom = horizontal_sides
    left, right = vertical_sides
    return [
        search_x0 + left,
        search_y0 + top,
        right - left,
        bottom - top,
    ]
