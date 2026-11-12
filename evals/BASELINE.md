# V1 baseline before reliability fixes

The frozen baseline is `baselines/v1-20261111/`, captured from `live-monorepo-preserved-20261111` at application commit `4c00aa4`.

- `golden.jsonl`: exact 45-case dataset used for the baseline.
- `runs.jsonl`: original per-case application responses, traces and judgments.
- `summary.json`: original scores and LangSmith experiment identifiers.
- `failure-categories.json`: 15 application failures, 10 answer-quality failures and 6 evaluator error records (5 judge, 1 RAGAS).
- `human_review.csv`: review worksheet.
- `manifest.json`: integrity checksums and baseline identity.

Categories measure different things and can overlap. Application failure means no accepted response was delivered; quality failure means a successfully assessed response missed critical requirements; evaluator error means the assessment failed. Skips and unassessed outcomes are not quality failures. Calibration was 8/10 and is documented in the migration report.

Never overwrite baseline artifacts or revise its expected answers to make a fix pass. Store future results in a new run directory and compare like-for-like cases, judge settings, and metrics. Verify manifest SHA256 checksums before comparison. One stochastic rerun does not establish a stable improvement.
