# PlanFuge 3-Minute Demo

## Before the demo

From the repository root, start the API:

```bash
python3 -m uvicorn server.app.api:app --port 8000
```

In a second terminal, start the UI:

```bash
cd client
npm run dev
```

Open the Vite URL and confirm that `SP_U1_0003` appears in Plan Selection.

## Demo flow and talking points

### 0:00–0:30 — Select the plan

1. Select `SP_U1_0003`.
2. Point out the plan image, metadata badges, and pipeline status.
3. If an overlay is available, toggle between Original and Overlay.

Say: “PlanFuge brings the source drawing, machine-detected opening candidates, and review status into one workspace.”

### 0:30–1:20 — Show human review

1. Select `OP-003` and show its crop preview.
2. Change `OP-003` from Needs Review to Verified.
3. Select `OP-001` and change it to Rejected.
4. Edit one reference or dimension field on a third candidate.
5. Click Review Detections to save the real-plan review draft.

Say: “OCR is evidence, not the final decision. A reviewer verifies correct detections, rejects noise, and can correct extracted fields before handoff.”

### 1:20–2:10 — Export reviewed data

1. Click Export JSON.
2. Click Export CSV.
3. State that only Verified candidates enter either contract export; rejected and unresolved rows are excluded.

Say: “The downstream handoff contains only human-verified openings. Missing height, low confidence, and overweight groups remain visibly flagged for review.”

### 2:10–2:40 — Show resilience

1. Point to the source badge above the table: Saved review draft or Raw CV candidates.
2. Click Use sample candidates.
3. Point out the amber Demo sample data badge and the disabled save action.
4. Click Return to real candidates.

Say: “The demo fallback is explicitly labeled and cannot overwrite a real review. It demonstrates the workflow without pretending sample output is CV output.”

### 2:40–3:00 — Close

Say: “This MVP proves a traceable human-in-the-loop path from drawing evidence to reviewed contract data. It is not production-ready automation; the next step is measured CV/OCR quality improvement on representative plans.”

## Fallback procedure

- If the raw candidate file is unavailable, click Use sample candidates.
- Mark the WDB and DDB sample rows Verified before exporting.
- Do not click Review Detections in sample mode; it is disabled by design.
- If crop preview fails, continue with the table and explain that the original candidate crop is an evidence aid, not required for export.

## Known limitations

- Red-region detection can include revision graphics that are not openings.
- OCR and dimension parsing are imperfect; ambiguous rows require human correction.
- Grid coordinates and color zones depend on validated per-plan configuration.
- Default height is used when no nearby height label is available, and the export marks that row for review.
- The application is a single-user hackathon MVP with file-based storage, not a production multi-user review system.
