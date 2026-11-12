# Numbered evaluation history

Evaluation numbers identify separate saved experiments. Repetitions belong to the same experiment; they are not new evaluation numbers. Pilot and recovery runs are excluded from the full-dataset comparison.

| Number | Application commit | Saved results | Scope |
|---|---|---|---|
| Eval 001 | `4c00aa4` | `baselines/v1-20261111` | Frozen V1 baseline, 45 cases |
| Eval 002 | `450c07b` | `results/quality-final-20261111` | Previous quality evaluation, 45 cases twice |
| Eval 003 | `593fa1e` | `results/eval-003` | Enhanced Ask and Plan candidate, 45 cases twice |
| Eval 004 | `d534241` | `results/eval-004` | Enhanced Plan with previous Ask path, 45 cases twice |

All four use the frozen dataset SHA-256 `2dc357b54caddca9684086ec6f7a790fc967f57649bbd37275b7bb93d29f064b`. The 24 Ask and 21 Plan cases include clarification, unknown, out-of-scope, investigation and Replan behaviors; not every case should produce a factual answer or implementation plan.

Eval 003 and Eval 004 retain Eval 002's judge implementation and numerical gates. Eval 002 included evaluator transport improvements relative to Eval 001, so that earlier comparison is not a pure application-only comparison.

The original baseline has its own checksum manifest. `experiment-history/eval-002-preservation.json` preserves hashes for all 163 files in Eval 002. Application provenance for the new runs is in `experiment-history/eval-003.json` and `experiment-history/eval-004.json`. Local raw results are ignored by Git; committed reports and comparison artifacts preserve the measured outcomes and failure categories. New experiments are also uploaded to LangSmith.

Do not overwrite earlier runs, edit golden references to improve a score, or count unassessed cases as quality failures. Use the next evaluation number for a new full run.
