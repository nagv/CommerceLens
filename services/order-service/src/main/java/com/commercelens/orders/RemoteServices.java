package com.commercelens.orders;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import java.net.URI;
import java.net.http.*;
import java.time.Duration;
import java.util.*;

@Component
public class RemoteServices implements Checkout.Ports {
 private final String inventory,payment,shipping;private final ObjectMapper json;private final OrderStore store;
 private final HttpClient client=HttpClient.newBuilder().connectTimeout(Duration.ofSeconds(2)).build();
 public RemoteServices(@Value("${inventory.url}")String inventory,@Value("${payment.url}")String payment,@Value("${shipping.url}")String shipping,ObjectMapper json,OrderStore store){this.inventory=inventory;this.payment=payment;this.shipping=shipping;this.json=json;this.store=store;}
 private JsonNode request(String method,String url,Object body){
  try{
   var builder=HttpRequest.newBuilder(URI.create(url)).timeout(Duration.ofSeconds(8)).header("Content-Type","application/json");
   if(body==null)builder.GET();else builder.method(method,HttpRequest.BodyPublishers.ofString(json.writeValueAsString(body)));
   var response=client.send(builder.build(),HttpResponse.BodyHandlers.ofString());
   if(response.statusCode()<200||response.statusCode()>=300){String message="upstream returned HTTP "+response.statusCode();try{JsonNode error=json.readTree(response.body());message=error.path("message").asText(error.path("detail").asText(message));}catch(Exception ignored){}throw new Checkout.RemoteFailure(response.statusCode(),message);}
   return json.readTree(response.body());
  }catch(Checkout.RemoteFailure e){throw e;}catch(Exception e){if(e instanceof InterruptedException)Thread.currentThread().interrupt();throw new Checkout.RemoteFailure(504,"upstream response unavailable; outcome may be uncertain");}
 }
 public JsonNode products(){return request("GET",inventory+"/api/products",null);}
 public Checkout.Reservation reserve(String id,Checkout.Request req){var result=request("POST",inventory+"/api/reservations",Map.of("orderId",id,"items",req.items()));var items=json.convertValue(result.path("items"),new TypeReference<List<Map<String,Object>>>(){});long subtotal=result.path("subtotalCents").asLong(-1);if(subtotal<0||items==null)throw new Checkout.RemoteFailure(502,"invalid inventory response");return new Checkout.Reservation(items,subtotal);}
 public String pay(String id,long cents,String scenario){return required(request("POST",payment+"/api/payments",Map.of("orderId",id,"amountCents",cents,"currency","USD","scenario",scenario)),"paymentId");}
 public String ship(String id,String postal,String scenario){return required(request("POST",shipping+"/api/shipments",Map.of("orderId",id,"postalCode",postal,"scenario",scenario)),"trackingNumber");}
 private String required(JsonNode body,String key){String value=body.path(key).asText();if(value.isBlank())throw new Checkout.RemoteFailure(504,"invalid provider response; outcome uncertain");return value;}
 public void release(String id){request("POST",inventory+"/api/reservations/"+id+"/release",Map.of());}
 public void refund(String paymentId,String id){request("POST",payment+"/api/payments/"+paymentId+"/refund",Map.of("orderId",id));}
 public void checkpoint(Checkout.Order order){store.checkpoint(order);}
}
