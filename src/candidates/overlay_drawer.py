import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


def draw_candidates_overlay(image_path: Path | str, candidates_path: Path | str, output_path: Path | str) -> None:
    """Draw bounding boxes and status labels on the high-resolution plan image.

    - Verification and Review boxes are color-coded (Blue for verified, Red for needs_review).
    - Stroke line thickness scales proportionally with the plan dimensions.
    - Default font fallback is used to ensure compatibility with Docker containers.
    """
    image_path = Path(image_path)
    candidates_path = Path(candidates_path)
    output_path = Path(output_path)

    # 1. Load candidates safely
    candidates = []
    if candidates_path.is_file():
        with open(candidates_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                if isinstance(data, dict):
                    candidates = data.get("candidates", [])
                elif isinstance(data, list):
                    candidates = data
            except json.JSONDecodeError:
                pass

    # Ensure output parent directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # 2. Draw candidates overlay
    with Image.open(image_path) as img:
        # Convert to RGB to support drawing in color
        overlay = img.convert("RGB")
        draw = ImageDraw.Draw(overlay)

        # Proportional line thickness and font size
        max_dim = max(overlay.width, overlay.height)
        line_thickness = max(2, int(max_dim / 1000))
        font_size = max(12, int(max_dim / 80))

        try:
            font = ImageFont.load_default(size=font_size)
        except TypeError:
            font = ImageFont.load_default()

        for cand in candidates:
            bbox = cand.get("bbox_image")
            if not bbox or len(bbox) != 4:
                continue

            x0 = int(bbox[0])
            y0 = int(bbox[1])
            x1 = int(bbox[0] + bbox[2])
            y1 = int(bbox[1] + bbox[3])

            status = cand.get("status", "needs_review")
            if status == "verified":
                color = (0, 0, 255)  # Blue
            else:
                color = (255, 0, 0)  # Red

            # Draw hollow bounding box rectangle
            draw.rectangle([x0, y0, x1, y1], outline=color, width=line_thickness)

            # Draw candidate ID label adjacent to the box
            cand_id = cand.get("candidate_id")
            if cand_id:
                label_text = cand_id.split("-")[-1] if "-" in cand_id else cand_id
                # Position label text slightly above the box, or at the top of the image if too close to the boundary
                text_y = max(0, y0 - font_size - 2)
                draw.text((x0, text_y), label_text, fill=color, font=font)

        # Save output image
        overlay.save(output_path)
