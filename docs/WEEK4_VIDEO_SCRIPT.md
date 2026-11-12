# CommerceLens Week 4 video walkthrough

Suggested duration: 5–7 minutes. Text in quotation marks is suggested narration. Screen directions are outside the quotations. Live responses can vary; show saved evaluation examples when discussing measured failures and scores.

## Project overview

Show the customer portal at http://localhost:3000, then the assistant at http://127.0.0.1:8090.

“My project is CommerceLens, a documentation assistant for understanding an application and planning changes across its services. The demo application has six services: Customer Portal, Order, Inventory, Payment, Shipping and Notification Worker. It includes databases, asynchronous notifications, and mock external providers for payment, shipping and email.

“The target users are engineers and technical leads who need to understand the whole application without reading every codebase. Each service has documentation, and a master catalog describes the application and its relationships. The assistant retrieves this documentation from Pinecone and uses structured relationship information to answer questions.”

## Use case and live demonstration

In Ask mode, enter: **Which service owns product prices and available stock?**

“Ask explains the application's current documented behavior. For example, the expected answer here is Inventory Service. The citations let us inspect the supporting documentation. A citation means the source was retrieved; it does not, by itself, prove that every claim is correct.”

In Plan mode, enter: **Plan a change that lets operators filter the orders currently loaded in the Operations screen by status.** Allow time for a response.

“Plan should explain the overall strategy, the impacted services, the high-level changes to each, implementation order, how the approach meets the request, alternatives and the preferred approach. For this particular request, the expected scope is filtering the already-loaded orders in Customer Portal. We should not introduce unnecessary backend changes.

“Replan lets a user choose an alternative and add constraints. Debugging questions should produce investigation leads rather than an unsupported root cause or implementation plan. The assistant is documentation-based: it cannot tell us live stock or production order status.”

If the live Plan response asks unnecessary clarification or exceeds scope, acknowledge it as a known failure rather than presenting it as a successful plan.

## Golden dataset

Open the Eval 004 dataset from the submission report. Show a question, expected response and case ID.

“I created and reviewed 45 test cases: 24 Ask and 21 Plan-mode cases. They cover individual services, cross-service workflows, the overall application, external dependencies, unavailable information, uncertainty, irrelevant questions, clarification, debugging and Replan.

“The expected answers and behaviors were reviewed against service code where needed. These are curated demo scenarios, not production-log samples. Explicit adversarial coverage and a held-out test set remain gaps.

“The same frozen cases are used across the numbered experiments. Each of the later experiments runs all 45 cases twice, producing 90 results. This helps expose variation, although two repetitions do not establish statistical significance.”

## Evaluation process

Open Eval 004 in LangSmith and select a case with scores.

“The evaluation checks more than whether the application returned an answer. Code checks validate execution, response behavior and citation identifiers. An LLM judge checks correctness, grounding, appropriate detail and the case's critical requirements. For plans, the criteria also cover scope, requirement coverage, alternatives and Replan constraints.

“RAGAS evaluates applicable factual Ask responses. We do not force its factual question-answering metrics onto clarification responses or proposed plans. Missing evaluator scores and evaluator errors stay separate from application failures.

“Human calibration is also important. Our last judge calibration agreed with human labels on eight out of ten examples, so automated scores still need review. LangSmith contains dataset-linked results and top-level traces; separate model and tool child spans remain an instrumentation gap.”

## Example failure

In the saved Eval 004 results, find **unknown-live-stock**, repetition 1. Show its input, output and failed requirements.

“This question asks: ‘How many units of BOOK-001 are available right now?’ The expected response is that the assistant does not have live inventory information. Instead, it used a value from documentation and claimed that 100 units were currently available.

“The answer included citations, but it was still wrong for the question. A documented example is not a live database reading. This illustrates why execution success and grounded-looking answers are insufficient: we must evaluate the user's intended outcome and the limits of the available evidence.”

Optionally show **replan-provider-quotes**. Explain that the saved answer asked for choices already supplied by the selected alternative instead of preserving the user's constraints.

## Changes and measured results

Show the comparison table in the Google Docs report.

“We made targeted changes to reliability controls, service retrieval, structured Plan output and bounded answer review. We preserved the original results and created new numbered experiments.

“One change made Ask worse. In Eval 003, Ask passed 28 out of 48 attempts, compared with 34 previously. We disabled the enhanced Ask path by default, and Eval 004 returned to 34 out of 48.

“Across all cases, Eval 002 had 88 successful executions out of 90, 51 quality passes, 34 quality failures and five unassessed results. Eval 004 had 90 successful executions, 52 quality passes, 36 quality failures and two unassessed judge errors.

“Execution became more reliable, but the quality improvement was only one additional pass. That is not meaningful evidence of better overall answer quality. Plan responses also became slower: average application latency increased from about 20 to 38 seconds. The changes were tested together, so we cannot attribute a separate measured gain to each change.”

## Conclusion and next steps

“The main outcome of this project is a repeatable evaluation process with preserved baselines, reviewed references, measured regressions and visible failures. It shows where the assistant works and where it is not yet ready for production.

“The next priorities are separating missing retrieval evidence from reasoning failures, preserving Plan and Replan constraints more reliably, improving judge calibration, expanding adversarial and real-user coverage, and completing child-span tracing. The report links the datasets, experiment results, prompts, code and remaining limitations.”

## Recording checklist

- Keep API keys and environment files off-screen.
- Open the portal, assistant, Google Docs report and LangSmith dataset/results before recording.
- Use saved evaluation rows for the failure and before/after comparison; do not imply a new live answer is the historical result.
- Add the Loom link to the report and confirm reviewers can access the supporting links.
