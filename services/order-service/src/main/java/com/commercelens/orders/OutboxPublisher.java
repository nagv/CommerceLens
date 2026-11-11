package com.commercelens.orders;

import org.springframework.amqp.core.*;
import org.springframework.amqp.rabbit.connection.CorrelationData;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.context.annotation.Bean;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;
import org.springframework.transaction.support.TransactionTemplate;
import java.nio.charset.StandardCharsets;
import java.util.Map;
import java.util.concurrent.TimeUnit;

@Component
public class OutboxPublisher {
 private final JdbcTemplate jdbc;private final RabbitTemplate rabbit;private final TransactionTemplate transaction;
 public OutboxPublisher(JdbcTemplate jdbc,RabbitTemplate rabbit,TransactionTemplate transaction){this.jdbc=jdbc;this.rabbit=rabbit;this.transaction=transaction;}
 @Bean public Queue orderQueue(){return new Queue("order.confirmed",true,false,false,Map.of("x-dead-letter-exchange","","x-dead-letter-routing-key","order.confirmed.dead"));}
 @Bean public Queue deadQueue(){return new Queue("order.confirmed.dead",true);}
 @Scheduled(fixedDelay=2000) public void publish(){
  // At-least-once delivery: consumers deduplicate eventId. Never lose an event on broker outage.
  transaction.executeWithoutResult(status->{
   var rows=jdbc.queryForList("SELECT event_id,payload::text AS payload FROM order_outbox WHERE published_at IS NULL ORDER BY created_at LIMIT 10 FOR UPDATE SKIP LOCKED");
   for(var row:rows){String id=(String)row.get("event_id");try{
    var props=new MessageProperties();props.setContentType("application/json");props.setDeliveryMode(MessageDeliveryMode.PERSISTENT);props.setMessageId(id);
    var correlation=new CorrelationData(id);
    rabbit.send("","order.confirmed",new Message(((String)row.get("payload")).getBytes(StandardCharsets.UTF_8),props),correlation);
    var confirm=correlation.getFuture().get(5,TimeUnit.SECONDS);
    if(!confirm.isAck()||correlation.getReturned()!=null)throw new IllegalStateException("broker did not confirm routed message");
    jdbc.update("UPDATE order_outbox SET published_at=now(),attempts=attempts+1,last_error=NULL WHERE event_id=?",id);
   }catch(Exception e){if(e instanceof InterruptedException)Thread.currentThread().interrupt();jdbc.update("UPDATE order_outbox SET attempts=attempts+1,last_error=? WHERE event_id=?",e.getClass().getSimpleName(),id);break;}}
  });
 }
}
