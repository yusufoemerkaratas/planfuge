import assert from "node:assert/strict";
import test from "node:test";

import { buildCandidateOverlayBoxes } from "./candidateOverlay.ts";

test("maps candidate image geometry to an SVG overlay box", () => {
  const boxes = buildCandidateOverlayBoxes([
    {
      candidate_id: "OP-001",
      status: "needs_review",
      bbox_image: [120, 340, 180, 90],
    },
  ]);

  assert.deepEqual(boxes, [
    {
      candidateId: "OP-001",
      tooltip: "OP-001 — needs_review",
      selected: false,
      x: 120,
      y: 340,
      width: 180,
      height: 90,
      stroke: "#dc2626",
    },
  ]);
});

test("colors candidate boxes by review status", () => {
  const boxes = buildCandidateOverlayBoxes([
    {
      candidate_id: "OP-001",
      status: "verified",
      bbox_image: [0, 0, 10, 10],
    },
    {
      candidate_id: "OP-002",
      status: "needs_review",
      bbox_image: [10, 10, 10, 10],
    },
    {
      candidate_id: "OP-003",
      status: "duplicate_candidate",
      bbox_image: [20, 20, 10, 10],
    },
    {
      candidate_id: "OP-004",
      status: "rejected",
      bbox_image: [30, 30, 10, 10],
    },
  ]);

  assert.deepEqual(
    boxes.map((box) => box.stroke),
    ["#16a34a", "#dc2626", "#eab308", "#eab308"],
  );
});

test("marks the selected box and describes it for the tooltip", () => {
  const boxes = buildCandidateOverlayBoxes(
    [
      {
        candidate_id: "OP-042",
        status: "verified",
        bbox_image: [1, 2, 3, 4],
      },
    ],
    "OP-042",
  );

  assert.equal(boxes[0]?.selected, true);
  assert.equal(boxes[0]?.tooltip, "OP-042 — verified");
});

test("skips invalid candidate geometry without hiding valid boxes", () => {
  const boxes = buildCandidateOverlayBoxes([
    {
      candidate_id: "OP-INVALID-SHAPE",
      status: "needs_review",
      bbox_image: [10, 20, 30],
    },
    {
      candidate_id: "OP-MISSING",
      status: "needs_review",
    },
    {
      candidate_id: "OP-NULL",
      status: "needs_review",
      bbox_image: null,
    },
    {
      candidate_id: "OP-INVALID-WIDTH",
      status: "needs_review",
      bbox_image: [10, 20, 0, 30],
    },
    {
      candidate_id: "OP-INVALID-FINITE",
      status: "needs_review",
      bbox_image: [10, Number.NaN, 20, 30],
    },
    {
      candidate_id: "OP-VALID",
      status: "verified",
      bbox_image: [10, 20, 30, 40],
    },
  ]);

  assert.deepEqual(
    boxes.map((box) => box.candidateId),
    ["OP-VALID"],
  );
});

test("skips boxes that are completely outside the displayed image", () => {
  const boxes = buildCandidateOverlayBoxes(
    [
      {
        candidate_id: "OP-OUTSIDE",
        status: "needs_review",
        bbox_image: [120, 10, 20, 20],
      },
      {
        candidate_id: "OP-PARTIAL",
        status: "needs_review",
        bbox_image: [90, 10, 20, 20],
      },
    ],
    null,
    100,
    100,
  );

  assert.deepEqual(
    boxes.map((box) => box.candidateId),
    ["OP-PARTIAL"],
  );
});
