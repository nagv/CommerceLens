# Plan 5: filter loaded orders by status

Question: Plan a change that lets operators filter the orders currently loaded in the Operations screen by status.

Status: Approved. This example illustrates expected depth; justified alternatives are acceptable.

## Verified current behavior

Customer Portal receives and displays order statuses but has no status filter. Order Service returns the latest 200 orders, so this request concerns the loaded list, not all historical orders.

## Overall implementation strategy

Filter within Customer Portal using existing loaded order information. Operators select a status, see matches immediately and can return to the full loaded list. Filtering changes presentation only; it does not modify orders or search beyond the loaded results.

## Impacted service and implementation details

### Customer Portal

- Add a labeled status selector above the list with All statuses as the default.
- Use understandable labels for statuses present in loaded orders. Keep distinct outcomes, such as uncertain payment and confirmed failure, distinct.
- Preserve ordering and access to order details when filtering.
- Show matching count versus loaded total, explain no matches and provide a clear reset action.
- Preserve the selection on refresh and recalculate matches against refreshed data.
- Label summary figures clearly so loaded-list totals are not mistaken for filtered counts.
- Support keyboard operation and an accessible control label.

### Other services

No backend change is required because the Portal already receives statuses. Searching the entire order history would be a separate Order Service search/pagination enhancement, not part of this request.

## Implementation order

1. Agree labels, default selection, refresh behavior, totals and the visible loaded-list limitation.
2. Add the Portal control and filter the existing list, preserving ordering and details.
3. Handle no matches, reset and refresh without unexpectedly clearing selection.
4. Validate each status, empty results, reset, refreshed statuses and order details; check keyboard use and confirm filtering does not modify orders.

## How this approach satisfies the request

- Operators find orders by status without scanning the list manually.
- Existing browser data allows immediate filtering.
- Explicit scope avoids implying all historical orders were searched.
- The implementation remains within Portal because required information already exists.

## Alternatives and recommendation

- **Status selector — recommended:** Compact, supports several distinct statuses and scales to more labels.
- **Clickable status tabs or summary cards:** Makes common categories visible, but uses more space and must not obscure less common statuses.
- **Backend filtering:** Appropriate for larger historical searches, but requires Order changes and pagination beyond the current loaded-list scope.

Prefer the selector for a focused Portal change. Prefer backend filtering only if the requirement expands beyond loaded orders. Evaluate useful single-service detail without rewarding unnecessary backend work.
