package main

import (
	"context"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"sort"
	"strings"
	"time"

	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgxpool"
)

type Item struct {
	SKU      string `json:"sku"`
	Quantity int    `json:"quantity"`
}
type ReserveRequest struct {
	OrderID string `json:"orderId"`
	Items   []Item `json:"items"`
}
type Product struct {
	SKU        string `json:"sku"`
	Name       string `json:"name"`
	PriceCents int64  `json:"priceCents"`
	Available  int    `json:"available"`
}
type ReservedItem struct {
	SKU        string `json:"sku"`
	Name       string `json:"name"`
	Quantity   int    `json:"quantity"`
	PriceCents int64  `json:"priceCents"`
}
type Reservation struct {
	OrderID       string         `json:"orderId"`
	Items         []ReservedItem `json:"items"`
	SubtotalCents int64          `json:"subtotalCents"`
	Status        string         `json:"status"`
}
type APIError struct {
	Status  int
	Message string
}

func (e *APIError) Error() string { return e.Message }
func validate(r ReserveRequest) error {
	if len(r.OrderID) == 0 || len(r.OrderID) > 100 || len(r.Items) == 0 || len(r.Items) > 100 {
		return &APIError{400, "orderId and 1-100 items are required"}
	}
	seen := map[string]bool{}
	for _, i := range r.Items {
		if strings.TrimSpace(i.SKU) == "" || len(i.SKU) > 100 || i.Quantity < 1 || i.Quantity > 1000 || seen[i.SKU] {
			return &APIError{400, "items require distinct SKUs and quantities between 1 and 1000"}
		}
		seen[i.SKU] = true
	}
	return nil
}
func fingerprint(r ReserveRequest) string {
	items := append([]Item(nil), r.Items...)
	sort.Slice(items, func(i, j int) bool { return items[i].SKU < items[j].SKU })
	b, _ := json.Marshal(items)
	h := sha256.Sum256(b)
	return hex.EncodeToString(h[:])
}

type Store struct{ pool *pgxpool.Pool }

func (s *Store) reserve(ctx context.Context, r ReserveRequest) (Reservation, error) {
	if err := validate(r); err != nil {
		return Reservation{}, err
	}
	tx, err := s.pool.Begin(ctx)
	if err != nil {
		return Reservation{}, err
	}
	defer tx.Rollback(ctx)
	// Serializes identical order IDs even before a reservation row exists.
	if _, err = tx.Exec(ctx, "SELECT pg_advisory_xact_lock(hashtextextended($1,0))", r.OrderID); err != nil {
		return Reservation{}, err
	}
	var previous []byte
	var hash, state string
	err = tx.QueryRow(ctx, "SELECT request_hash,body,status FROM inventory_reservations WHERE order_id=$1", r.OrderID).Scan(&hash, &previous, &state)
	if err == nil {
		if hash != fingerprint(r) || state != "reserved" {
			return Reservation{}, &APIError{409, "reservation already exists with different items or was released"}
		}
		var result Reservation
		if err = json.Unmarshal(previous, &result); err != nil {
			return result, err
		}
		return result, tx.Commit(ctx)
	}
	if !errors.Is(err, pgx.ErrNoRows) {
		return Reservation{}, err
	}
	items := append([]Item(nil), r.Items...)
	sort.Slice(items, func(i, j int) bool { return items[i].SKU < items[j].SKU })
	result := Reservation{OrderID: r.OrderID, Status: "reserved", Items: []ReservedItem{}}
	for _, i := range items {
		var p Product
		err = tx.QueryRow(ctx, "SELECT sku,name,price_cents,available FROM inventory_products WHERE sku=$1 FOR UPDATE", i.SKU).Scan(&p.SKU, &p.Name, &p.PriceCents, &p.Available)
		if errors.Is(err, pgx.ErrNoRows) {
			return Reservation{}, &APIError{404, "unknown SKU: " + i.SKU}
		}
		if err != nil {
			return Reservation{}, err
		}
		if p.Available < i.Quantity {
			return Reservation{}, &APIError{409, "insufficient stock: " + i.SKU}
		}
		if _, err = tx.Exec(ctx, "UPDATE inventory_products SET available=available-$1 WHERE sku=$2", i.Quantity, i.SKU); err != nil {
			return Reservation{}, err
		}
		result.Items = append(result.Items, ReservedItem{i.SKU, p.Name, i.Quantity, p.PriceCents})
		result.SubtotalCents += p.PriceCents * int64(i.Quantity)
	}
	body, err := json.Marshal(result)
	if err != nil {
		return Reservation{}, err
	}
	_, err = tx.Exec(ctx, "INSERT INTO inventory_reservations(order_id,request_hash,body,status) VALUES($1,$2,$3,'reserved')", r.OrderID, fingerprint(r), body)
	if err != nil {
		return Reservation{}, err
	}
	return result, tx.Commit(ctx)
}
func (s *Store) release(ctx context.Context, id string) error {
	tx, err := s.pool.Begin(ctx)
	if err != nil {
		return err
	}
	defer tx.Rollback(ctx)
	if _, err = tx.Exec(ctx, "SELECT pg_advisory_xact_lock(hashtextextended($1,0))", id); err != nil {
		return err
	}
	var body []byte
	var state string
	err = tx.QueryRow(ctx, "SELECT body,status FROM inventory_reservations WHERE order_id=$1 FOR UPDATE", id).Scan(&body, &state)
	if errors.Is(err, pgx.ErrNoRows) {
		return &APIError{404, "reservation not found"}
	}
	if err != nil {
		return err
	}
	if state == "released" {
		return tx.Commit(ctx)
	}
	var reservation Reservation
	if err = json.Unmarshal(body, &reservation); err != nil {
		return err
	}
	for _, item := range reservation.Items {
		if _, err = tx.Exec(ctx, "UPDATE inventory_products SET available=available+$1 WHERE sku=$2", item.Quantity, item.SKU); err != nil {
			return err
		}
	}
	if _, err = tx.Exec(ctx, "UPDATE inventory_reservations SET status='released' WHERE order_id=$1", id); err != nil {
		return err
	}
	return tx.Commit(ctx)
}
func (s *Store) products(ctx context.Context) ([]Product, error) {
	rows, err := s.pool.Query(ctx, "SELECT sku,name,price_cents,available FROM inventory_products ORDER BY sku")
	if err != nil {
		return nil, err
	}
	defer rows.Close()
	result := []Product{}
	for rows.Next() {
		var p Product
		if err = rows.Scan(&p.SKU, &p.Name, &p.PriceCents, &p.Available); err != nil {
			return nil, err
		}
		result = append(result, p)
	}
	return result, rows.Err()
}
func write(w http.ResponseWriter, status int, body any) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	json.NewEncoder(w).Encode(body)
}
func fail(w http.ResponseWriter, err error) {
	var api *APIError
	if errors.As(err, &api) {
		write(w, api.Status, map[string]string{"message": api.Message})
		return
	}
	log.Printf("request failed: %v", err)
	write(w, 503, map[string]string{"message": "inventory temporarily unavailable"})
}
func (s *Store) handler() http.Handler {
	mux := http.NewServeMux()
	mux.HandleFunc("GET /health", func(w http.ResponseWriter, r *http.Request) {
		ctx, cancel := context.WithTimeout(r.Context(), 2*time.Second)
		defer cancel()
		if err := s.pool.Ping(ctx); err != nil {
			fail(w, err)
			return
		}
		write(w, 200, map[string]string{"status": "ok"})
	})
	mux.HandleFunc("GET /api/products", func(w http.ResponseWriter, r *http.Request) {
		result, err := s.products(r.Context())
		if err != nil {
			fail(w, err)
			return
		}
		write(w, 200, result)
	})
	mux.HandleFunc("POST /api/reservations", func(w http.ResponseWriter, r *http.Request) {
		r.Body = http.MaxBytesReader(w, r.Body, 65536)
		decoder := json.NewDecoder(r.Body)
		decoder.DisallowUnknownFields()
		var body ReserveRequest
		if err := decoder.Decode(&body); err != nil {
			write(w, 400, map[string]string{"message": "invalid reservation JSON"})
			return
		}
		if err := decoder.Decode(&struct{}{}); err != io.EOF {
			write(w, 400, map[string]string{"message": "expected one JSON object"})
			return
		}
		ctx, cancel := context.WithTimeout(r.Context(), 5*time.Second)
		defer cancel()
		result, err := s.reserve(ctx, body)
		if err != nil {
			fail(w, err)
			return
		}
		write(w, 200, result)
	})
	mux.HandleFunc("POST /api/reservations/{id}/release", func(w http.ResponseWriter, r *http.Request) {
		ctx, cancel := context.WithTimeout(r.Context(), 5*time.Second)
		defer cancel()
		if err := s.release(ctx, r.PathValue("id")); err != nil {
			fail(w, err)
			return
		}
		write(w, 200, map[string]string{"status": "released"})
	})
	return mux
}

const schema = `CREATE TABLE IF NOT EXISTS inventory_products(sku TEXT PRIMARY KEY,name TEXT NOT NULL,price_cents BIGINT NOT NULL CHECK(price_cents>0),available INTEGER NOT NULL CHECK(available>=0));
CREATE TABLE IF NOT EXISTS inventory_reservations(order_id TEXT PRIMARY KEY,request_hash TEXT NOT NULL,body JSONB NOT NULL,status TEXT NOT NULL);
INSERT INTO inventory_products VALUES('BOOK-001','Agentic Systems Handbook',2900,100),('KIT-001','Developer Desk Kit',4900,50),('MUG-001','CommerceLens Mug',1500,100) ON CONFLICT DO NOTHING;`

func main() {
	url := os.Getenv("DATABASE_URL")
	if url == "" {
		log.Fatal("DATABASE_URL is required")
	}
	ctx, cancel := context.WithTimeout(context.Background(), 15*time.Second)
	defer cancel()
	pool, err := pgxpool.New(ctx, url)
	if err != nil {
		log.Fatal(err)
	}
	defer pool.Close()
	if _, err = pool.Exec(ctx, schema); err != nil {
		log.Fatal(err)
	}
	server := &http.Server{Addr: ":8080", Handler: (&Store{pool}).handler(), ReadHeaderTimeout: 5 * time.Second, ReadTimeout: 10 * time.Second, WriteTimeout: 10 * time.Second, IdleTimeout: 30 * time.Second}
	fmt.Println("inventory listening on :8080")
	log.Fatal(server.ListenAndServe())
}
