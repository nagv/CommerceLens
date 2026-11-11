package com.commercelens.orders;

import com.fasterxml.jackson.annotation.JsonIgnore;
import java.time.Instant;
import java.util.*;

/** Checkout saga. External effects are never retried blindly after uncertain outcomes. */
public class Checkout {
 public record Item(String sku,int quantity) {}
 public record Request(String customerEmail,String postalCode,List<Item> items,String paymentScenario,String shippingScenario) {}
 public record Reservation(List<Map<String,Object>> items,long subtotalCents) {}
 public static class Order {
  public String id,status,customerEmail,postalCode,paymentId,trackingNumber,failureReason,createdAt;
  public List<Map<String,Object>> items=List.of();
  public long subtotalCents,shippingCents=500,totalCents;
  @JsonIgnore public int httpStatus=409;
  public Order() {}
  public Order(String id,Request req){this.id=id;status="pending";customerEmail=req.customerEmail();postalCode=req.postalCode();createdAt=Instant.now().toString();}
 }
 public interface Ports {
  Reservation reserve(String orderId,Request request);
  String pay(String orderId,long cents,String scenario);
  String ship(String orderId,String postalCode,String scenario);
  void release(String orderId);
  void refund(String paymentId,String orderId);
  default void checkpoint(Order order) {}
 }
 public static class RemoteFailure extends RuntimeException {public final int status;public RemoteFailure(int status,String message){super(message);this.status=status;}}
 private final Ports ports;
 public Checkout(Ports ports){this.ports=ports;}
 public static void validate(Request r){
  if(r==null||r.customerEmail()==null||r.customerEmail().length()>254||!r.customerEmail().matches("^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$")||r.postalCode()==null||!r.postalCode().matches("^[A-Za-z0-9 -]{3,16}$"))throw new IllegalArgumentException("valid customerEmail and postalCode are required");
  if(r.items()==null||r.items().isEmpty()||r.items().size()>100)throw new IllegalArgumentException("1-100 items required");
  Set<String> seen=new HashSet<>();for(Item item:r.items()){if(item==null||item.sku()==null||!item.sku().matches("^[A-Za-z0-9_-]{1,100}$")||item.quantity()<1||item.quantity()>1000||!seen.add(item.sku()))throw new IllegalArgumentException("distinct SKUs with quantities between 1 and 1000 required");}
  if(r.paymentScenario()!=null&&!Set.of("success","decline","timeout").contains(r.paymentScenario()))throw new IllegalArgumentException("invalid payment scenario");
  if(r.shippingScenario()!=null&&!Set.of("success","failure").contains(r.shippingScenario()))throw new IllegalArgumentException("invalid shipping scenario");
 }
 public Order run(String id,Request request){return run(new Order(id,request),request);}
 public Order run(Order order,Request request){
  Reservation reservation;
  try {reservation=ports.reserve(order.id,request);}catch(RemoteFailure e){order.status=e.status>=500?"manual_review":"failed";order.failureReason="Inventory reservation: "+e.getMessage();order.httpStatus=e.status>=500?503:e.status;return order;}
  order.items=reservation.items();order.subtotalCents=reservation.subtotalCents();order.totalCents=order.subtotalCents+order.shippingCents;order.status="reserved";ports.checkpoint(order);
  // Persist uncertainty before sending a payment: a crash cannot be mistaken for no charge.
  order.status="payment_unknown";ports.checkpoint(order);
  try {order.paymentId=ports.pay(order.id,order.totalCents,Objects.requireNonNullElse(request.paymentScenario(),"success"));}
  catch(RemoteFailure e){order.failureReason="Payment: "+e.getMessage();order.httpStatus=e.status>=500?504:e.status;if(e.status!=402){order.status="payment_unknown";return order;}order.status="failed";release(order);return order;}
  order.status="paid";ports.checkpoint(order);
  try {order.trackingNumber=ports.ship(order.id,request.postalCode(),Objects.requireNonNullElse(request.shippingScenario(),"success"));}
  catch(RemoteFailure e){
   order.failureReason="Shipping: "+e.getMessage();order.httpStatus=502;
   // A transport timeout can mean the carrier accepted the shipment; retain resources for review.
   if(e.status>=500){order.status="manual_review";return order;}
   order.status="failed";
   try{ports.refund(order.paymentId,order.id);}catch(RuntimeException refund){order.status="manual_review";order.failureReason+="; refund requires reconciliation";}
   release(order);return order;
  }
  order.status="confirmed";order.httpStatus=201;return order;
 }
 private void release(Order order){try{ports.release(order.id);}catch(RuntimeException release){order.status="manual_review";order.failureReason+="; stock release requires reconciliation";order.httpStatus=503;}}
}

