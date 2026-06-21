import assert from "node:assert/strict";
import test from "node:test";

import {
  buildCandidateCropUrl,
  buildCandidatePreviewUrl,
} from "./cropPreview.ts";

test("builds a crop URL from the selected candidate bbox", () => {
  assert.equal(
    buildCandidateCropUrl("PLAN 1", [10, 20, 30, 40]),
    "/api/images/candidate-crops/PLAN%201?x=10&y=20&width=30&height=40",
  );
});

test("rejects invalid crop geometry", () => {
  assert.equal(buildCandidateCropUrl("PLAN-1", [10, 20, 0, 40]), null);
  assert.equal(buildCandidateCropUrl("PLAN-1", [10, Number.NaN, 30, 40]), null);
});

test("prefers OCR-derived crop paths for preview", () => {
  assert.equal(
    buildCandidatePreviewUrl(
      "PLAN-1",
      "pdf_words",
      [10, 20, 30, 40],
      [1, 2, 3, 4],
      "/app/outputs/crops/PLAN-1_RED-004.png",
    ),
    "/api/images/crops/PLAN-1_RED-004.png",
  );
});

test("ignores candidate-specific auto-generated crop paths", () => {
  assert.equal(
    buildCandidatePreviewUrl(
      "PLAN-1",
      "pdf_words",
      [10, 20, 30, 40],
      [1, 2, 3, 4],
      "/app/outputs/crops/PLAN-1_OP-001.png",
    ),
    "/api/images/candidate-crops-pdf/PLAN-1?x0=1&y0=2&x1=3&y1=4",
  );
});

test("uses PDF bbox preview for pdf_words candidates without crop paths", () => {
  assert.equal(
    buildCandidatePreviewUrl(
      "PLAN-1",
      "pdf_words",
      [10, 20, 30, 40],
      [1, 2, 3, 4],
      null,
    ),
    "/api/images/candidate-crops-pdf/PLAN-1?x0=1&y0=2&x1=3&y1=4",
  );
});
