package com.commercelens.orders;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.http.ResponseEntity;
import org.springframework.http.converter.HttpMessageNotReadableException;
import org.springframework.web.bind.annotation.*;
import java.security.MessageDigest;
import java.util.*;

@RestController
public class OrderController {
 private final OrderStore store;private final RemoteServices remote;private final ObjectMapper json;
 public OrderController(OrderStore store,RemoteServices remote,ObjectMapper json){this.store=store;this.remote=remote;this.json=json;}
 @GetMapping("/health") public ResponseEntity<?> health(){return ResponseEntity.status(store.healthy()?200:503).body(Map.of("status","ok"));}
 @GetMapping("/api/products") public Object products(){return remote.products();}
 @GetMapping("/api/orders") public Object list(){return store.list();}
 @GetMapping("/api/orders/{id}") public ResponseEntity<?> get(@PathVariable String id){return store.get(id).<ResponseEntity<?>>map(ResponseEntity::ok).orElseGet(()->ResponseEntity.status(404).body(Map.of("message","order not found")));}
 @PostMapping("/api/orders") public ResponseEntity<?> create(@RequestHeader(value="Idempotency-Key",required=false)String key,@RequestBody Checkout.Request request){
  if(key==null||!key.matches("^[A-Za-z0-9_-]{1,100}$"))throw new IllegalArgumentException("Idempotency-Key header required (1-100 letters, numbers, hyphens or underscores)");
  Checkout.validate(request);String hash=hash(request);var order=new Checkout.Order(UUID.randomUUID().toString(),request);
  if(!store.create(order,key,hash)){var existing=store.byKey(key);if(!existing.hash().equals(hash))return ResponseEntity.status(409).body(Map.of("message","Idempotency-Key already used with different request","id",existing.order().id));return ResponseEntity.status(existing.order().httpStatus).body(existing.order());}
  try{order=new Checkout(remote).run(order,request);}catch(RuntimeException e){order.status="manual_review";order.failureReason="Checkout interrupted; reconcile external effects before retrying";order.httpStatus=503;}
  store.finish(order);return ResponseEntity.status(order.httpStatus).body(order);
 }
 private String hash(Checkout.Request req){try{var sorted=req.items().stream().sorted(Comparator.comparing(Checkout.Item::sku)).toList();var canonical=new Checkout.Request(req.customerEmail(),req.postalCode(),sorted,Objects.requireNonNullElse(req.paymentScenario(),"success"),Objects.requireNonNullElse(req.shippingScenario(),"success"));return HexFormat.of().formatHex(MessageDigest.getInstance("SHA-256").digest(json.writeValueAsBytes(canonical)));}catch(Exception e){throw new IllegalStateException(e);}}
 @ExceptionHandler({IllegalArgumentException.class,HttpMessageNotReadableException.class}) public ResponseEntity<?> bad(Exception e){return ResponseEntity.badRequest().body(Map.of("message",e instanceof IllegalArgumentException?e.getMessage():"invalid JSON request"));}
 @ExceptionHandler(Checkout.RemoteFailure.class) public ResponseEntity<?> upstream(Checkout.RemoteFailure e){return ResponseEntity.status(e.status).body(Map.of("message",e.getMessage()));}
}
