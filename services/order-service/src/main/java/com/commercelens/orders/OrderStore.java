package com.commercelens.orders;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Repository;
import org.springframework.transaction.annotation.Transactional;
import java.util.*;

@Repository
public class OrderStore {
 private final JdbcTemplate jdbc;private final ObjectMapper json;
 public OrderStore(JdbcTemplate jdbc,ObjectMapper json){this.jdbc=jdbc;this.json=json;}
 String encode(Object value){try{return json.writeValueAsString(value);}catch(Exception e){throw new IllegalStateException(e);}}
 Checkout.Order decode(String value,int status){try{var order=json.readValue(value,Checkout.Order.class);order.httpStatus=status;return order;}catch(Exception e){throw new IllegalStateException(e);}}
 public boolean create(Checkout.Order order,String key,String hash){return jdbc.update("INSERT INTO orders(id,idempotency_key,request_hash,body) VALUES(?,?,?,?::jsonb) ON CONFLICT(idempotency_key) DO NOTHING",order.id,key,hash,encode(order))==1;}
 public Existing byKey(String key){return jdbc.queryForObject("SELECT request_hash,body::text,http_status FROM orders WHERE idempotency_key=?",(r,n)->new Existing(r.getString(1),decode(r.getString(2),r.getInt(3))),key);}
 public record Existing(String hash,Checkout.Order order){}
 public Optional<Checkout.Order> get(String id){return jdbc.query("SELECT body::text,http_status FROM orders WHERE id=?",(r,n)->decode(r.getString(1),r.getInt(2)),id).stream().findFirst();}
 public List<Checkout.Order> list(){return jdbc.query("SELECT body::text,http_status FROM orders ORDER BY created_at DESC LIMIT 200",(r,n)->decode(r.getString(1),r.getInt(2)));}
 public void checkpoint(Checkout.Order order){jdbc.update("UPDATE orders SET body=?::jsonb WHERE id=?",encode(order),order.id);}
 @Transactional public void finish(Checkout.Order order){
  jdbc.update("UPDATE orders SET body=?::jsonb,http_status=? WHERE id=?",encode(order),order.httpStatus,order.id);
  if("confirmed".equals(order.status)){
   String eventId="order-confirmed-"+order.id;
   var event=Map.of("eventId",eventId,"orderId",order.id,"customerEmail",order.customerEmail,"totalCents",order.totalCents,"trackingNumber",order.trackingNumber);
   jdbc.update("INSERT INTO order_outbox(event_id,payload) VALUES(?,?::jsonb) ON CONFLICT DO NOTHING",eventId,encode(event));
  }
 }
 public boolean healthy(){return Integer.valueOf(1).equals(jdbc.queryForObject("SELECT 1",Integer.class));}
}
