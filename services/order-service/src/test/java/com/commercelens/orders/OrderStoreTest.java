package com.commercelens.orders;

import com.fasterxml.jackson.databind.ObjectMapper;
import org.junit.jupiter.api.Test;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.datasource.DriverManagerDataSource;
import org.springframework.jdbc.datasource.init.ResourceDatabasePopulator;
import org.springframework.core.io.ClassPathResource;
import java.util.UUID;
import java.util.concurrent.*;
import static org.junit.jupiter.api.Assertions.*;
import static org.junit.jupiter.api.Assumptions.assumeTrue;

class OrderStoreTest {
 @Test void postgresAcceptsOnlyOneConcurrentIdempotencyKey() throws Exception {
  String url=System.getenv("TEST_JDBC_URL");assumeTrue(url!=null,"TEST_JDBC_URL not configured");
  var ds=new DriverManagerDataSource(url,System.getenv("TEST_DB_USER"),System.getenv("TEST_DB_PASSWORD"));
  new ResourceDatabasePopulator(new ClassPathResource("schema.sql")).execute(ds);
  var jdbc=new JdbcTemplate(ds);var store=new OrderStore(jdbc,new ObjectMapper());String key="test-"+UUID.randomUUID();
  try(var executor=Executors.newFixedThreadPool(8)){
   var jobs=new java.util.ArrayList<Callable<Boolean>>();
   for(int i=0;i<20;i++)jobs.add(()->store.create(new Checkout.Order(UUID.randomUUID().toString(),CheckoutTest.request()),key,"same-hash"));
   int successes=0;for(var result:executor.invokeAll(jobs))if(result.get())successes++;
   assertEquals(1,successes);assertEquals("same-hash",store.byKey(key).hash());
  }finally{jdbc.update("DELETE FROM orders WHERE idempotency_key=?",key);}
 }
}
