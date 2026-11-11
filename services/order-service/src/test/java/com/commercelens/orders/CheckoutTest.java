package com.commercelens.orders;

import org.junit.jupiter.api.Test;
import java.util.*;
import static org.junit.jupiter.api.Assertions.*;

class CheckoutTest {
 @Test void rejectsInvalidQuantitiesAndDuplicateSkus() {
  var req=new Checkout.Request("a@example.com","12345",List.of(new Checkout.Item("BOOK-001",0)),"success","success");
  assertThrows(IllegalArgumentException.class,()->Checkout.validate(req));
  var duplicate=new Checkout.Request("a@example.com","12345",List.of(new Checkout.Item("BOOK-001",1),new Checkout.Item("BOOK-001",1)),"success","success");
  assertThrows(IllegalArgumentException.class,()->Checkout.validate(duplicate));
 }
 @Test void timeoutKeepsReservationForReconciliation() {
  var ports=new FakePorts(); ports.paymentFailure=new Checkout.RemoteFailure(504,"timeout");
  var result=new Checkout(ports).run("order-1",request());
  assertEquals("payment_unknown",result.status);
  assertFalse(ports.released);
 }
 @Test void declineReleasesReservation() {
  var ports=new FakePorts(); ports.paymentFailure=new Checkout.RemoteFailure(402,"declined");
  var result=new Checkout(ports).run("order-1",request());
  assertEquals("failed",result.status); assertTrue(ports.released); assertFalse(ports.refunded);
 }
 @Test void paymentConflictRetainsReservationForReconciliation() {
  var ports=new FakePorts();ports.paymentFailure=new Checkout.RemoteFailure(409,"provider conflict");
  var result=new Checkout(ports).run("order-1",request());
  assertEquals("payment_unknown",result.status);assertFalse(ports.released);assertFalse(ports.refunded);
 }
 @Test void shipmentFailureRefundsAndReleases() {
  var ports=new FakePorts(); ports.shippingFailure=true;
  var result=new Checkout(ports).run("order-1",request());
  assertEquals("failed",result.status); assertTrue(ports.released); assertTrue(ports.refunded);
 }
 @Test void failedCompensationRequiresManualReview() {
  var ports=new FakePorts(); ports.shippingFailure=true; ports.refundFailure=true;
  assertEquals("manual_review",new Checkout(ports).run("order-1",request()).status);
  assertTrue(ports.released);
 }
 @Test void uncertainShipmentRetainsPaymentAndReservation() {
  var ports=new FakePorts();ports.shippingFailure=true;ports.shippingStatus=504;
  var result=new Checkout(ports).run("order-1",request());
  assertEquals("manual_review",result.status);assertFalse(ports.refunded);assertFalse(ports.released);
 }
 @Test void successUsesAuthoritativePrices() {
  var result=new Checkout(new FakePorts()).run("order-1",request());
  assertEquals("confirmed",result.status); assertEquals(3400,result.totalCents);
 }
 static Checkout.Request request(){ return new Checkout.Request("a@example.com","12345",List.of(new Checkout.Item("BOOK-001",1)),"success","success"); }
 static class FakePorts implements Checkout.Ports {
  Checkout.RemoteFailure paymentFailure; boolean shippingFailure,refundFailure,released,refunded;int shippingStatus=422;
  public Checkout.Reservation reserve(String id,Checkout.Request request){return new Checkout.Reservation(List.of(Map.of("sku","BOOK-001","name","Book","quantity",1,"priceCents",2900)),2900);}
  public String pay(String id,long cents,String scenario){if(paymentFailure!=null)throw paymentFailure;return "pay-1";}
  public String ship(String id,String postal,String scenario){if(shippingFailure)throw new Checkout.RemoteFailure(shippingStatus,"shipment rejected");return "TRACK-1";}
  public void release(String id){released=true;}
  public void refund(String payment,String id){refunded=true;if(refundFailure)throw new Checkout.RemoteFailure(502,"refund unavailable");}
 }
}
