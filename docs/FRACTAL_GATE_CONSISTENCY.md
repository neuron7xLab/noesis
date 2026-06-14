# Fractal Gate Consistency

`noesis/evaluation/fractal_gate_consistency.py`. Verifies the discharge gate is
**scale-invariant**: same gate, different scale.

## Scales (small → large)

`token_decision` · `text_edit` · `code_patch` · `test_case` · `module_change` ·
`pull_request` · `release_candidate`.

## Checks (`check_fractal_consistency`)

- **Consistency probe:** one canonical input run across all scales must yield the
  same decision (`cross_scale_gate_consistency` = 1.0 by construction — a single
  `DischargeGate` judges every scale).
- **No bypass:** every scale must have a gated decision (`SCALE_BYPASSES_GATE`).
- **Verifier per scale:** every scale must carry a verifier > 0 (`SCALE_NO_VERIFIER`).
- **Release monotonicity:** `release_candidate` may not PASS while a lower scale
  fails → `false_pass_rate`. Over-rejection (release fails while all lower pass) →
  `false_reject_rate`.

`status` is FAIL on any problem or `false_pass_rate > 0`.

## Metrics

`cross_scale_gate_consistency`, `scale_specific_failure_rate`, `false_pass_rate`,
`false_reject_rate`.

```bash
python -m pytest tests/test_fractal_gate_consistency.py -q
```
