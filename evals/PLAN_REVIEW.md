# Plan evaluation and review

Review status: first case awaiting approval; remaining cases will be reviewed one at a time. The proposed coverage target is 16 cases, not yet 16 implemented golden entries. The four original Plan entries remain in golden.jsonl. Replan UI/API support is not implemented by this evaluator change.

## Scoring contract

Each plan receives eight separate semantic scores and reasons:

| Dimension | What sufficient detail means |
|---|---|
| Overall strategy | A clear, coherent approach with responsibilities, assumptions and boundaries |
| Service impacts | Necessary services and reasons, distinguishing required from conditional changes |
| Per-service details | Separate high-level descriptions of changes, interactions and relevant failure handling |
| Implementation order | Organized stages with prerequisites, dependencies and possible parallel work |
| Requirement coverage | Break the request into parts and explain how the approach satisfies each |
| Alternatives | Brief but meaningful variations and trade-offs when applicable |
| Recommendation rationale | Explain why the selected approach fits better and when another would be preferable |
| Grounding | Correct current facts; proposals and unverified assumptions explicitly distinguished |

Scores: 0 = missing/incorrect, 1 = relevant but vague/incomplete, 2 = specific and sufficient. Headings or length alone do not earn credit. Multiple valid approaches can pass review. Ground truth concerns current facts, not one mandatory implementation.

Alternatives policy is per case: required when reviewers know meaningful alternatives exist; not_applicable when they do not; conditional when applicability needs judgment. Only alternatives may receive null, with an explanation. Null is excluded from averages, not treated as a perfect score. Missing alternatives must score 0 when required. A plan must still explain why the recommended approach fits even if alternatives do not apply.

The existing plan_quality summary is the mean of applicable dimension scores divided by two (0–1). Individual dimensions remain 0–2; groundedness is grounding divided by two. Critical issues and explanations are retained locally; dimension explanations accompany LangSmith feedback. No production acceptance threshold has been set: a high mean must not hide a critical unsupported premise.

Factual RAGAS metrics remain skipped for plans. These rubrics use an LLM judge and require human calibration. Path/hash evidence identifies sources but is not file content supplied to the judge. verified_current_facts are reviewer-checked facts; retrieved contexts remain the assistant's runtime evidence.

## Proposed coverage

| Category | Cases | Review focus |
|---|---:|---|
| Single service | 2 | Useful scoped changes without invented dependencies |
| Cross-service | 4 | Integration, sequence and compatibility |
| Application-wide | 2 | Coherent strategy and phased adoption |
| External dependencies | 2 | Provider capability checks, boundaries and alternatives |
| Missing information or constraints | 2 | Clarification, assumptions and conditional recommendations |
| Irrelevant or infeasible requests | 2 | Appropriate response instead of an invented implementation |
| Replan | 2 | Respect selected alternative and original requirements; future capability |

Behavioral Plan cases should be designed and routed to behavior-specific grading when added; the eight-dimension rubric is for actual implementation plans, not a demand to produce a plan for an irrelevant question. Replan cases and their execution contract will be reviewed separately. This coverage is not claimed implemented yet.

## Plan 1: destination-based shipping

**Question:** Plan a high-level change from fixed shipping charges to destination-based rates.

**Status:** Pending user review. Meaningful alternatives are required for this case.

### Verified current facts

- Shipping Service returns a fixed $5 USD charge and validates the provider shipment charge against that fixed amount.
- Order Service calculates its total using fixed shipping before payment, then requests shipment creation after payment authorization.
- Customer Portal displays a fixed shipping estimate.
- Payment Service accepts the total from Order Service; changing its interface is not inherently necessary.
- The current Shipping implementation does not establish a destination-based quoting capability. Do not assume the external provider supports it.

### Expected overall strategy

Explain how Shipping will supply a destination-based quote, how Order will use an agreed amount before payment, and how Portal will show it before confirmation. Define assumptions around supported destinations, validity and changes. Application-managed regional rules are one reasonable starting approach; provider quotes are also acceptable if proposed conditionally and justified.

### Per-service detail

- **Shipping:** Explain rate determination, unsupported destinations and unavailable rates. Define quote terms and update existing fixed-charge shipment validation. Address the relationship between customer price and provider cost.
- **Order:** Obtain/validate the quote before payment, preserve the accepted amount across retries, and require renewed confirmation for expired or changed quotes rather than silently changing the charge.
- **Portal:** Display shipping and updated total before confirmation; refresh when destination changes; handle unavailable quotes and prevent confirmation without a valid total.
- Additional service changes must be justified. A retrieved service is not automatically a service that must change.

### Implementation sequence

1. Agree on pricing rules and the quote interface, validity and failure behavior.
2. Implement Shipping quote support and compatibility with existing checkout.
3. Integrate Order's total/payment and retry behavior. Portal development may proceed in parallel once the interface is agreed.
4. Integrate the customer-visible quote and confirmation flow.
5. Validate displayed, accepted and payment-requested amounts; cover changed destinations, quote expiry, failures and retries before enabling the flow.

### Requirement-to-solution explanation

The plan should explicitly connect destination-sensitive pricing to Shipping, correct payment totals to Order, pre-confirmation visibility to Portal, and repeat-checkout consistency to the accepted quote. Explain remaining gaps instead of claiming the requirement is satisfied merely because services were listed.

### Alternatives and preference

- **Application-managed regional rules:** Predictable business pricing without an unverified provider quote dependency; requires rule maintenance and may diverge from provider costs.
- **Provider-supplied quotes:** Potentially closer to provider pricing, conditional on verified provider support; introduces outage, validity and price-change handling.
- **Hybrid, if useful:** Provider quotes with an explicitly approved fallback policy; adds resilience but also reconciliation complexity. Not a mandatory third option.

The recommendation must explain why the choice fits the actual requirements and verified capabilities. It should identify conditions under which another option would be preferable. No specific option is the sole correct answer.
