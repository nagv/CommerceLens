# Community 1

> 26 nodes · cohesion 0.18

## Key Concepts

- **.run()** (20 connections) — `src/main/java/com/commercelens/orders/Checkout.java`
- **FakePorts** (15 connections) — `src/test/java/com/commercelens/orders/CheckoutTest.java`
- **org.junit.jupiter.api.Test** (11 connections)
- **CheckoutTest** (11 connections) — `src/test/java/com/commercelens/orders/CheckoutTest.java`
- **.request()** (11 connections) — `src/test/java/com/commercelens/orders/CheckoutTest.java`
- **Ports** (10 connections) — `src/main/java/com/commercelens/orders/Checkout.java`
- **.declineReleasesReservation()** (5 connections) — `src/test/java/com/commercelens/orders/CheckoutTest.java`
- **.failedCompensationRequiresManualReview()** (5 connections) — `src/test/java/com/commercelens/orders/CheckoutTest.java`
- **.paymentConflictRetainsReservationForReconciliation()** (5 connections) — `src/test/java/com/commercelens/orders/CheckoutTest.java`
- **.shipmentFailureRefundsAndReleases()** (5 connections) — `src/test/java/com/commercelens/orders/CheckoutTest.java`
- **.successUsesAuthoritativePrices()** (5 connections) — `src/test/java/com/commercelens/orders/CheckoutTest.java`
- **.timeoutKeepsReservationForReconciliation()** (5 connections) — `src/test/java/com/commercelens/orders/CheckoutTest.java`
- **.uncertainShipmentRetainsPaymentAndReservation()** (5 connections) — `src/test/java/com/commercelens/orders/CheckoutTest.java`
- **.release()** (4 connections) — `src/main/java/com/commercelens/orders/Checkout.java`
- **CheckoutTest.java** (4 connections) — `src/test/java/com/commercelens/orders/CheckoutTest.java`
- **.checkpoint()** (3 connections) — `src/main/java/com/commercelens/orders/Checkout.java`
- **.postgresAcceptsOnlyOneConcurrentIdempotencyKey()** (3 connections) — `src/test/java/com/commercelens/orders/OrderStoreTest.java`
- **.Checkout()** (2 connections) — `src/main/java/com/commercelens/orders/Checkout.java`
- **.pay()** (2 connections) — `src/main/java/com/commercelens/orders/Checkout.java`
- **.refund()** (2 connections) — `src/main/java/com/commercelens/orders/Checkout.java`
- **.release()** (2 connections) — `src/main/java/com/commercelens/orders/Checkout.java`
- **.ship()** (2 connections) — `src/main/java/com/commercelens/orders/Checkout.java`
- **.pay()** (1 connections) — `src/test/java/com/commercelens/orders/CheckoutTest.java`
- **.refund()** (1 connections) — `src/test/java/com/commercelens/orders/CheckoutTest.java`
- **.release()** (1 connections) — `src/test/java/com/commercelens/orders/CheckoutTest.java`
- *... and 1 more nodes in this community*

## Relationships

- [Community 7](Community_7.md) (12 shared connections)
- [Community 0](Community_0.md) (5 shared connections)
- [Community 5](Community_5.md) (3 shared connections)
- [Community 3](Community_3.md) (1 shared connections)
- [Community 6](Community_6.md) (1 shared connections)
- [Community 4](Community_4.md) (1 shared connections)

## Source Files

- `src/main/java/com/commercelens/orders/Checkout.java`
- `src/test/java/com/commercelens/orders/CheckoutTest.java`
- `src/test/java/com/commercelens/orders/OrderStoreTest.java`

## Audit Trail

- EXTRACTED: 67 (82%)
- INFERRED: 15 (18%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*