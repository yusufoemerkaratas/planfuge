export function buildCandidateCropUrl(
  planId: string,
  bboxImage: readonly number[],
): string | null {
  if (
    bboxImage.length !== 4 ||
    !bboxImage.every((value) => Number.isFinite(value)) ||
    bboxImage[2] <= 0 ||
    bboxImage[3] <= 0
  ) {
    return null;
  }

  const params = new URLSearchParams({
    x: String(bboxImage[0]),
    y: String(bboxImage[1]),
    width: String(bboxImage[2]),
    height: String(bboxImage[3]),
  });
  return `/api/images/candidate-crops/${encodeURIComponent(planId)}?${params}`;
}

export function buildCandidatePreviewUrl(
  planId: string,
  source: string | undefined,
  bboxImage: readonly number[],
  bboxPdf: readonly number[] | null | undefined,
  cropPath: string | null | undefined,
): string | null {
  if (cropPath) {
    const filename = cropPath.split("/").pop();
    if (filename && filename.includes("RED-")) {
      return `/api/images/crops/${encodeURIComponent(filename)}`;
    }
  }

  if (
    source === "pdf_words" &&
    bboxPdf &&
    bboxPdf.length === 4 &&
    bboxPdf.every((value) => Number.isFinite(value))
  ) {
    const params = new URLSearchParams({
      x0: String(bboxPdf[0]),
      y0: String(bboxPdf[1]),
      x1: String(bboxPdf[2]),
      y1: String(bboxPdf[3]),
    });
    return `/api/images/candidate-crops-pdf/${encodeURIComponent(planId)}?${params}`;
  }

  return buildCandidateCropUrl(planId, bboxImage);
}
