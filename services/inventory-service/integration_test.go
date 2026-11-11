package main

import (
	"context"
	"fmt"
	"github.com/jackc/pgx/v5/pgxpool"
	"os"
	"sync"
	"sync/atomic"
	"testing"
	"time"
)

func TestPostgresReservationsNeverOversellAndReleaseIsIdempotent(t *testing.T) {
	url := os.Getenv("TEST_DATABASE_URL")
	if url == "" {
		t.Skip("TEST_DATABASE_URL not configured")
	}
	ctx := context.Background()
	pool, err := pgxpool.New(ctx, url)
	if err != nil {
		t.Fatal(err)
	}
	defer pool.Close()
	if _, err = pool.Exec(ctx, schema); err != nil {
		t.Fatal(err)
	}
	sku := fmt.Sprintf("TEST-%d", time.Now().UnixNano())
	if _, err = pool.Exec(ctx, "INSERT INTO inventory_products VALUES($1,'Test product',100,5)", sku); err != nil {
		t.Fatal(err)
	}
	defer pool.Exec(ctx, "DELETE FROM inventory_reservations WHERE order_id LIKE $1", sku+"-%")
	defer pool.Exec(ctx, "DELETE FROM inventory_products WHERE sku=$1", sku)
	store := &Store{pool}
	var successes atomic.Int32
	var wg sync.WaitGroup
	for i := 0; i < 20; i++ {
		wg.Add(1)
		go func(i int) {
			defer wg.Done()
			_, err := store.reserve(ctx, ReserveRequest{OrderID: fmt.Sprintf("%s-%d", sku, i), Items: []Item{{SKU: sku, Quantity: 1}}})
			if err == nil {
				successes.Add(1)
			}
		}(i)
	}
	wg.Wait()
	if successes.Load() != 5 {
		t.Fatalf("expected 5 successful reservations, got %d", successes.Load())
	}
	var available int
	if err = pool.QueryRow(ctx, "SELECT available FROM inventory_products WHERE sku=$1", sku).Scan(&available); err != nil {
		t.Fatal(err)
	}
	if available != 0 {
		t.Fatalf("remaining stock=%d", available)
	}
	var id string
	if err = pool.QueryRow(ctx, "SELECT order_id FROM inventory_reservations WHERE order_id LIKE $1 LIMIT 1", sku+"-%").Scan(&id); err != nil {
		t.Fatal(err)
	}
	request := ReserveRequest{OrderID: id, Items: []Item{{SKU: sku, Quantity: 1}}}
	if _, err = store.reserve(ctx, request); err != nil {
		t.Fatalf("same request replay failed: %v", err)
	}
	request.Items[0].Quantity = 2
	if _, err = store.reserve(ctx, request); err == nil {
		t.Fatal("conflicting replay accepted")
	}
	if err = store.release(ctx, id); err != nil {
		t.Fatal(err)
	}
	if err = store.release(ctx, id); err != nil {
		t.Fatal(err)
	}
	if err = pool.QueryRow(ctx, "SELECT available FROM inventory_products WHERE sku=$1", sku).Scan(&available); err != nil {
		t.Fatal(err)
	}
	if available != 1 {
		t.Fatalf("release replay changed stock twice: %d", available)
	}
}
