"""Parse construction opening labels into structured candidate fields."""

from __future__ import annotations

import re
from typing import Any

LABEL_TYPES = ("UZDB", "WDB", "DDB", "DDP")
REFERENCES = ("UKRD", "OKRB", "UKRB")


def parse_opening_label(text: str) -> dict[str, Any] | None:
    """Parse a raw opening label string.

    Returns ``None`` when the text does not look like an opening label. Missing
    fields are returned as ``None`` so callers can safely serialize the result.
    """
    normalized = _normalize_text(text)
    label_type = _parse_label_type(normalized)

    if label_type is None:
        return None

    width_mm, height_mm = _parse_rectangular_dimensions(normalized, label_type)

    return {
        "label_type": label_type,
        "width_mm": width_mm,
        "height_mm": height_mm,
        "diameter_mm": _parse_diameter(normalized),
        "ra_value": _parse_signed_value(normalized, "RA"),
        "ok_value": _parse_signed_value(normalized, "OK"),
        "reference": _parse_reference(normalized),
    }


def _normalize_text(text: str) -> str:
    """Normalize common OCR/PDF text variants without changing meaning."""
    return (
        text.upper()
        .replace("⌀", "Ø")
        .replace("Ф", "Ø")
        .replace("Р", "P")
    )


def _parse_label_type(text: str) -> str | None:
    for label_type in LABEL_TYPES:
        if re.search(rf"\b{label_type}\b|{label_type}\d", text):
            return label_type

    if re.search(r"\bHSI\s*\d+", text):
        return "HSI"

    return None


def _parse_rectangular_dimensions(text: str, label_type: str) -> tuple[int | None, int | None]:
    pattern = rf"(?:\b{label_type}\s*)?(\d{{1,3}})\s*/\s*(\d{{1,3}})"
    match = re.search(pattern, text)

    if not match:
        return None, None

    width_cm, height_cm = (int(match.group(1)), int(match.group(2)))
    return width_cm * 10, height_cm * 10


def _parse_diameter(text: str) -> int | None:
    hsi_match = re.search(r"\bHSI\s*(\d{2,3})\b", text)
    if hsi_match:
        return int(hsi_match.group(1))

    diameter_match = re.search(r"Ø\s*(\d{1,3})\b", text)
    if not diameter_match:
        return None

    value = int(diameter_match.group(1))
    if value < 100:
        return value * 10

    return value


def _parse_signed_value(text: str, marker: str) -> int | None:
    match = re.search(rf"\b{marker}\s*([-+]?\d+)\b", text)
    if not match:
        return None

    return int(match.group(1))


def _parse_reference(text: str) -> str | None:
    for reference in REFERENCES:
        if re.search(rf"\b{reference}\b", text):
            return reference

    return None
