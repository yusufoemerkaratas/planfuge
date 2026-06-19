import assert from "node:assert/strict";
import test from "node:test";

import {
  canSaveCandidates,
  candidateSourceFromApi,
  candidateSourceLabel,
} from "./sampleMode.ts";

test("sample candidates cannot overwrite a real plan review", () => {
  assert.equal(canSaveCandidates("sample"), false);
  assert.equal(canSaveCandidates("raw"), true);
  assert.equal(canSaveCandidates("review"), true);
});

test("candidate API sources have distinct user-facing labels", () => {
  assert.equal(candidateSourceFromApi("review"), "review");
  assert.equal(candidateSourceFromApi("file"), "raw");
  assert.equal(candidateSourceLabel("review"), "Saved review draft");
  assert.equal(candidateSourceLabel("raw"), "Raw CV candidates");
  assert.equal(candidateSourceLabel("sample"), "Demo sample data");
});
