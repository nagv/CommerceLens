# Plan 17: investigate a missing confirmation email

Question: An order is confirmed, but the customer hasn't received the confirmation email. Help investigate.

Status: Approved. Investigation leads only; no implementation plan.

## Expected answer

A confirmed order does not necessarily mean the customer received the email. Notification Worker handles confirmation emails separately. Without this order's delivery history, I cannot identify the cause yet.

**Possible leads and checks:**

- **Order Service:** Check whether the order's confirmation event was published.
- **Messaging and Notification Worker:** Check whether the notification was received and processed. Inspect its status, delivery attempts, and latest error.
- **Email provider:** If sending was recorded as successful, check the available provider result and intended recipient. A recorded send does not prove inbox receipt; spam or filtering is another possibility.

Start with the same order reference throughout these checks. If no notification appears in a recent-results screen, that alone does not prove it was never recorded.

Please provide the order reference, approximate confirmation time, and any notification status or error shown. Avoid repeating checkout or triggering another send before checking the original delivery outcome.
