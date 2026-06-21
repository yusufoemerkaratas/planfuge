import { useMemo, type KeyboardEvent } from "react";

import {
  buildCandidateOverlayBoxes,
  type CandidateOverlayInput,
} from "./candidateOverlay";

interface CandidateOverlayProps {
  candidates: readonly CandidateOverlayInput[];
  imageWidth: number;
  imageHeight: number;
  selectedCandidateId: string | null;
  pulsingCandidateId: string | null;
  pulseRevision: number;
  onSelect: (candidateId: string) => void;
}

export function CandidateOverlay({
  candidates,
  imageWidth,
  imageHeight,
  selectedCandidateId,
  pulsingCandidateId,
  pulseRevision,
  onSelect,
}: CandidateOverlayProps) {
  const boxes = useMemo(
    () =>
      buildCandidateOverlayBoxes(
        candidates,
        selectedCandidateId,
        imageWidth,
        imageHeight,
      ),
    [candidates, selectedCandidateId, imageWidth, imageHeight],
  );

  const handleKeyDown = (
    event: KeyboardEvent<SVGRectElement>,
    candidateId: string,
  ) => {
    if (event.key !== "Enter" && event.key !== " ") return;
    event.preventDefault();
    onSelect(candidateId);
  };

  return (
    <svg
      className="absolute inset-0 z-10 h-full w-full pointer-events-none"
      viewBox={`0 0 ${imageWidth} ${imageHeight}`}
      preserveAspectRatio="none"
      aria-label="Interactive candidate bounding boxes"
    >
      {boxes.map((box) => {
        const isPulsing = box.candidateId === pulsingCandidateId;
        return (
          <rect
            key={`${box.candidateId}-${isPulsing ? pulseRevision : "idle"}`}
            role="button"
            tabIndex={0}
            aria-label={box.tooltip}
            x={box.x}
            y={box.y}
            width={box.width}
            height={box.height}
            stroke={box.stroke}
            strokeWidth={box.selected ? 4 : 2}
            vectorEffect="non-scaling-stroke"
            fill={box.stroke}
            fillOpacity={box.selected ? 0.18 : 0.06}
            className={`candidate-overlay-box pointer-events-auto cursor-pointer ${isPulsing ? "candidate-overlay-box-pulse" : ""}`}
            onClick={() => onSelect(box.candidateId)}
            onKeyDown={(event) => handleKeyDown(event, box.candidateId)}
          >
            <title>{box.tooltip}</title>
          </rect>
        );
      })}
    </svg>
  );
}
