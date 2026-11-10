# Ask evaluation policy

Ask explains CommerceLens at a high level using static master and service documentation. It has no live business-data, production monitoring, or deployment lookup tools. Code may be inspected by reviewers to verify references, but is not indexed or sent to the assistant.

Expected behaviors: answer (supported facts), partial_answer (supported portion plus missing information), unknown (requested information unavailable), uncertain (relevant evidence exists but cannot establish the requested conclusion), clarify (ask one focused question), redirect (briefly explain CommerceLens scope).

Clarification is single-turn only: score the clarification request, not a subsequent conversation. Unknown is not proof that a feature does not exist. Uncertainty is not a self-reported probability. Do not infer live values, guarantees or production state from static examples.

Application factual claims need valid evidence citations. Pure scope, clarification and unavailable-information responses do not. A response that mixes these with application facts must cite the facts. Model labels are routing metadata, not proof of semantic correctness; human-calibrated semantic grading judges the actual response.

Execution success and answer quality are separate. A valid abstention can execute successfully and still be inappropriate for an answerable question. Lexical phrase coverage is diagnostic only. Factual RAGAS scores apply to factual answer cases, not behavioral cases. Quality must be reported with evaluator coverage; skipped metrics never mean a passing score.

All new cases are review candidates. Previously approved references remain approved. This is a development set, not an independent held-out benchmark. Paraphrases, false-premise and partial-answer cases can be added after review; multi-turn flows are excluded. The existing payment documentation conflict is deliberately retained; correctness follows the approved answer and groundedness follows retrieved evidence independently.
