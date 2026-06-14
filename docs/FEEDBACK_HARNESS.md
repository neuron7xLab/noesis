# Feedback Harness — proxy → anchored measurement

`noesis/feedback.py`. The node that converts the stack from *proxy* (structural
consistency) to *measurement* (demonstrated usefulness), using human-labeled
ground truth:

```
input → artifact → human verdict ("works" / "fails")  [+ optional HRV]
```

This is the verifier that `residual_promotion.py` demands: **data promotes a proxy
to a measurement; nothing else does.**

## Fail-closed

Below `MIN_PAIRS` (12) labeled pairs → `status = INSUFFICIENT_DATA`,
`anchored_quality = null`, never a calibrated PASS. The proxy stays a proxy until
reality says otherwise.

## Calibration report

When enough labels exist:
- `anchored_quality` — mean real reward (measured usefulness, not proxy).
- `calibration_gap` — `mean(proxy) − anchored_quality`; positive beyond tolerance
  (0.15) → `verdict = PROXY_OVERCLAIMS` (the proxy lies); else `ALIGNED`.
- `proxy_reality_alignment` — Pearson correlation of proxy vs reward (`null` if
  variance degenerate).
- `provenance` — input source; `synthetic_fixture` data is for testing the
  machinery only, never a real release claim.
- `hrv_coverage` — fraction of pairs carrying a physiological state reading.

Schema: `schemas/feedback_calibration.schema.json`.

## Run

```bash
python -m noesis.cli feedback ingest data/feedback_pairs.example.json   # exit 0 = CALIBRATED
python -m noesis.cli feedback status
python -m pytest tests/test_feedback.py -q
```

> Next (step 2): wire `anchored_quality` into the failure-weighted release verdict
> so a green release means *measured useful*, not *structurally consistent*. Bring
> ~15–20 real labeled pairs and it stops being synthetic.
