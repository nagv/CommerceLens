package main

import "testing"

func TestValidateRejectsInvalidAndDuplicateItems(t *testing.T) {
	for _, items := range [][]Item{{}, {{SKU: "BOOK-001", Quantity: 0}}, {{SKU: "BOOK-001", Quantity: -1}}, {{SKU: "BOOK-001", Quantity: 1}, {SKU: "BOOK-001", Quantity: 2}}} {
		if validate(ReserveRequest{OrderID: "order-1", Items: items}) == nil {
			t.Fatalf("accepted invalid items: %+v", items)
		}
	}
}

func TestFingerprintIndependentOfItemOrder(t *testing.T) {
	a := ReserveRequest{OrderID: "one", Items: []Item{{SKU: "B", Quantity: 1}, {SKU: "A", Quantity: 2}}}
	b := ReserveRequest{OrderID: "one", Items: []Item{{SKU: "A", Quantity: 2}, {SKU: "B", Quantity: 1}}}
	if fingerprint(a) != fingerprint(b) {
		t.Fatal("equivalent requests must share fingerprint")
	}
	b.Items[0].Quantity = 3
	if fingerprint(a) == fingerprint(b) {
		t.Fatal("different quantities must conflict")
	}
}
