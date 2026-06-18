"""Detect red annotation regions in rendered plan PNG images."""

from __future__ import annotations

from collections import deque
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image


def detect_red_regions(
    image: str | Path | Image.Image,
    min_area_px: int = 250,
) -> tuple[list[dict[str, Any]], Image.Image]:
    """Return red annotation regions and a debug mask image.

    The detector uses HSV thresholding with two red hue ranges, then applies a
    small binary dilation to connect thin red markup strokes.
    """
    pil_image = _load_rgb_image(image)
    rgb = np.asarray(pil_image)
    hsv = _rgb_to_hsv(rgb)
    red_mask = _red_hsv_mask(hsv)
    cleaned_mask = _dilate(red_mask, iterations=1)
    regions = _regions_from_mask(cleaned_mask, min_area_px=min_area_px, bbox_mask=red_mask)
    debug_mask = Image.fromarray((cleaned_mask.astype(np.uint8) * 255), mode="L")
    return regions, debug_mask


def save_red_debug_mask(mask: Image.Image, output_path: str | Path) -> None:
    """Save a red detection debug mask, creating parent folders if needed."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    mask.save(output_path)


def _load_rgb_image(image: str | Path | Image.Image) -> Image.Image:
    if isinstance(image, Image.Image):
        return image.convert("RGB")

    with Image.open(image) as opened_image:
        return opened_image.convert("RGB")


def _rgb_to_hsv(rgb: np.ndarray) -> np.ndarray:
    rgb_float = rgb.astype(np.float32) / 255.0
    red = rgb_float[..., 0]
    green = rgb_float[..., 1]
    blue = rgb_float[..., 2]

    max_channel = np.max(rgb_float, axis=-1)
    min_channel = np.min(rgb_float, axis=-1)
    delta = max_channel - min_channel

    hue = np.zeros_like(max_channel)
    nonzero_delta = delta != 0

    red_is_max = (max_channel == red) & nonzero_delta
    green_is_max = (max_channel == green) & nonzero_delta
    blue_is_max = (max_channel == blue) & nonzero_delta

    hue[red_is_max] = ((green[red_is_max] - blue[red_is_max]) / delta[red_is_max]) % 6
    hue[green_is_max] = ((blue[green_is_max] - red[green_is_max]) / delta[green_is_max]) + 2
    hue[blue_is_max] = ((red[blue_is_max] - green[blue_is_max]) / delta[blue_is_max]) + 4
    hue = hue * 60

    saturation = np.zeros_like(max_channel)
    nonzero_value = max_channel != 0
    saturation[nonzero_value] = delta[nonzero_value] / max_channel[nonzero_value]

    return np.stack([hue, saturation, max_channel], axis=-1)


def _red_hsv_mask(hsv: np.ndarray) -> np.ndarray:
    hue = hsv[..., 0]
    saturation = hsv[..., 1]
    value = hsv[..., 2]

    lower_red = hue <= 15
    upper_red = hue >= 345
    return (lower_red | upper_red) & (saturation >= 0.35) & (value >= 0.25)


def _dilate(mask: np.ndarray, iterations: int) -> np.ndarray:
    result = mask
    for _ in range(iterations):
        padded = np.pad(result, 1, mode="constant", constant_values=False)
        result = (
            padded[:-2, :-2]
            | padded[:-2, 1:-1]
            | padded[:-2, 2:]
            | padded[1:-1, :-2]
            | padded[1:-1, 1:-1]
            | padded[1:-1, 2:]
            | padded[2:, :-2]
            | padded[2:, 1:-1]
            | padded[2:, 2:]
        )

    return result


def _regions_from_mask(
    mask: np.ndarray,
    min_area_px: int,
    bbox_mask: np.ndarray | None = None,
) -> list[dict[str, Any]]:
    height, width = mask.shape
    visited = np.zeros(mask.shape, dtype=bool)
    regions = []

    for y in range(height):
        for x in range(width):
            if visited[y, x] or not mask[y, x]:
                continue

            component = _collect_component(mask, visited, x, y)
            region = _tighten_region_to_mask(component, bbox_mask) if bbox_mask is not None else component
            if region["area_px"] < min_area_px:
                continue

            regions.append(region)

    regions.sort(key=lambda region: (region["bbox_image"][1], region["bbox_image"][0]))
    return [_format_region(index + 1, region) for index, region in enumerate(regions)]


def _collect_component(
    mask: np.ndarray,
    visited: np.ndarray,
    start_x: int,
    start_y: int,
) -> dict[str, Any]:
    queue = deque([(start_x, start_y)])
    visited[start_y, start_x] = True
    min_x = max_x = start_x
    min_y = max_y = start_y
    area_px = 0

    while queue:
        x, y = queue.popleft()
        area_px += 1
        min_x = min(min_x, x)
        max_x = max(max_x, x)
        min_y = min(min_y, y)
        max_y = max(max_y, y)

        for next_x, next_y in _neighbors(x, y, mask.shape[1], mask.shape[0]):
            if visited[next_y, next_x] or not mask[next_y, next_x]:
                continue

            visited[next_y, next_x] = True
            queue.append((next_x, next_y))

    return {
        "bbox_image": [min_x, min_y, max_x - min_x + 1, max_y - min_y + 1],
        "area_px": area_px,
    }


def _tighten_region_to_mask(region: dict[str, Any], mask: np.ndarray) -> dict[str, Any]:
    x, y, width, height = region["bbox_image"]
    cropped_mask = mask[y : y + height, x : x + width]
    points = np.argwhere(cropped_mask)

    if len(points) == 0:
        return region

    min_y, min_x = points.min(axis=0)
    max_y, max_x = points.max(axis=0)
    return {
        "bbox_image": [
            int(x + min_x),
            int(y + min_y),
            int(max_x - min_x + 1),
            int(max_y - min_y + 1),
        ],
        "area_px": int(cropped_mask.sum()),
    }


def _neighbors(x: int, y: int, width: int, height: int):
    for next_x, next_y in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
        if 0 <= next_x < width and 0 <= next_y < height:
            yield next_x, next_y


def _format_region(region_number: int, region: dict[str, Any]) -> dict[str, Any]:
    return {
        "region_id": f"RED-{region_number:03d}",
        "bbox_image": region["bbox_image"],
        "area_px": region["area_px"],
        "source": "red_annotation",
    }
