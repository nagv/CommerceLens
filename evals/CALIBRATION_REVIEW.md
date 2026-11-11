# Calibration and variant review

## Item 1 — replan-good

Approved by the user on 2026-11-10 as a passing Replan example, after direct source-code verification.

Clarification incorporated: preserve the existing delivery record and attempt count, and add recovery audit history for subsequent recovery attempts. The current worker does not retain detailed history for every previous attempt. Restricted command, authorization and manual recovery remain proposed additions.

This approval covers the corrected example, not the malformed judge output. Historical evaluation artifacts remain unchanged; the updated fixture has not been rescored.

All six items reviewed and approved on 2026-11-10. No items remain in this review batch.

## Item 2 — replan-incorrect

User approved the expected fail judgment on 2026-11-10: rejects the selected command approach, changes excluded services, discards history and replaces the notification identity used for provider duplicate protection. Historical evaluation artifacts remain unchanged.

## Item 3 — document-conflict

User approved on 2026-11-10: code-correct answers receive correctness credit independently of contradictory retrieved documentation. Grounding remains low, citations missing, and documentation conflict flagged. Passing critical factual requirements does not imply overall quality approval. Historical evaluation results unchanged.

## Item 4 — plan-historical-status-filter

User approved the question and expanded expected plan on 2026-11-10 after source verification. Both Order Service and Customer Portal change; filtering covers available stored history before pagination, without promising unavailable archived/deleted data. Category corrected to multi_service. Historical run artifacts remain unchanged.

## Item 5 — debug-confirmed-decline-stock

User approved the question and expanded investigation response on 2026-11-10 after source verification. Distinguish confirmed decline from timeout, correlate the original attempt, inspect release outcome and reservation state, and request focused evidence. No implementation plan, new payment or immediate manual release. Historical evaluation artifacts unchanged.

## Item 6 — replan-notification-portal

User approved the question and expanded expected plan on 2026-11-10. Adopt Portal-based recovery, explicitly supersede the earlier Portal exclusion, retain worker-owned safeguards and keep Order Service unchanged. Preserve the existing aggregate delivery record and add future recovery audit history. Previous-plan context clarified consistently. Historical evaluation artifacts remain unchanged; revised references have not been rerun.

## Revised evaluation run

All 45 revised application cases and 10 calibration fixtures were run after this review. See docs/REVIEWED_EVAL_RESULTS_2026-11-10.md. Results: 15 cases met critical requirements, 14 failed quality requirements, 9 execution failures and 7 judge errors. Calibration agreement remained 7/10. One stalled RAGAS task was interrupted and its original saved answer recovered for semantic scoring; the timeout remains recorded. All 45 run records uploaded to LangSmith. Earlier review notes describe the state at approval time; no historical results were overwritten.
