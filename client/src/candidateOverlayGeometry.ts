export interface CandidateOverlayInput {
  candidate_id: string;
  status: string;
  bbox_image?: unknown;
}

export interface CandidateOverlayBox {
  candidateId: string;
  tooltip: string;
  selected: boolean;
  x: number;
  y: number;
  width: number;
  height: number;
  stroke: string;
}

function statusStroke(status: string): string {
  if (status === "verified") return "#16a34a";
  if (status === "needs_review") return "#dc2626";
  return "#eab308";
}

function isValidBoundingBox(
  value: unknown,
): value is [number, number, number, number] {
  if (!Array.isArray(value) || value.length !== 4) return false;
  if (!value.every((coordinate) => Number.isFinite(coordinate))) return false;
  return value[2] > 0 && value[3] > 0;
}

export function buildCandidateOverlayBoxes(
  candidates: readonly CandidateOverlayInput[],
  selectedCandidateId: string | null = null,
  imageWidth?: number,
  imageHeight?: number,
): CandidateOverlayBox[] {
  return candidates.flatMap((candidate) => {
    if (!isValidBoundingBox(candidate.bbox_image)) return [];
    const [x, y, width, height] = candidate.bbox_image;
    if (
      imageWidth !== undefined &&
      imageHeight !== undefined &&
      (x >= imageWidth || y >= imageHeight || x + width <= 0 || y + height <= 0)
    ) {
      return [];
    }

    return [
      {
        candidateId: candidate.candidate_id,
        tooltip: `${candidate.candidate_id} — ${candidate.status}`,
        selected: candidate.candidate_id === selectedCandidateId,
        x,
        y,
        width,
        height,
        stroke: statusStroke(candidate.status),
      },
    ];
  });
}
