import http from 'node:http';
import amqp from 'amqplib';
import pg from 'pg';
import {deliver,parseEvent} from './delivery.js';
import {watchSession} from './lifecycle.js';

const pool=new pg.Pool({connectionString:process.env.DATABASE_URL});
const sleep=(ms:number)=>new Promise(r=>setTimeout(r,ms));
let ready=false,stopping=false;
const server=http.createServer(async(req,res)=>{
 res.setHeader('Content-Type','application/json');
 try {
  if(req.method==='GET'&&req.url==='/health'){res.statusCode=ready?200:503;res.end(JSON.stringify({status:ready?'ok':'starting'}));}
  else if(req.method==='GET'&&req.url==='/api/notifications'){
   const data=await pool.query('SELECT event_id AS "eventId", order_id AS "orderId",status,attempts,last_error AS "lastError" FROM notification_deliveries ORDER BY updated_at DESC LIMIT 100');res.end(JSON.stringify(data.rows));
  }else{res.statusCode=404;res.end(JSON.stringify({message:'Not found'}));}
 }catch{res.statusCode=503;res.end(JSON.stringify({message:'Notification storage unavailable'}));}
});
server.listen(Number(process.env.PORT??8080),'0.0.0.0');
async function connect(){
 await pool.query(`CREATE TABLE IF NOT EXISTS notification_deliveries(event_id TEXT PRIMARY KEY,order_id TEXT NOT NULL,payload JSONB NOT NULL,status TEXT NOT NULL DEFAULT 'pending',attempts INTEGER NOT NULL DEFAULT 0,last_error TEXT,updated_at TIMESTAMPTZ NOT NULL DEFAULT now())`);
 const connection=await amqp.connect(process.env.RABBITMQ_URL??'amqp://guest:guest@rabbitmq:5672');
 const session=watchSession(connection,()=>{ready=false;});
 connection.on('error',e=>console.error('RabbitMQ connection error:',e.message));
 try{
 const channel=await connection.createChannel();
 session.watchChannel(channel);
 await channel.assertQueue('order.confirmed.dead',{durable:true});
 await channel.assertQueue('order.confirmed',{durable:true,arguments:{'x-dead-letter-exchange':'','x-dead-letter-routing-key':'order.confirmed.dead'}});
 await channel.prefetch(1);
 await channel.consume('order.confirmed',async message=>{
  if(!message){session.stop();return;}
  let event;
  try{event=parseEvent(message.content.toString());}catch{try{channel.nack(message,false,false);}catch{}return;}
  let db:pg.PoolClient;
  try{db=await pool.connect();}catch(error){console.error('Database unavailable');await sleep(1000);try{channel.nack(message,false,true);}catch{}return;}
  let locked=false;
  try{
   // Session lock serializes this event across workers without rolling back attempt counters on a crash.
   await db.query('SELECT pg_advisory_lock(hashtext($1))',[event.eventId]);locked=true;
   await db.query('INSERT INTO notification_deliveries(event_id,order_id,payload) VALUES($1,$2,$3) ON CONFLICT DO NOTHING',[event.eventId,event.orderId,JSON.stringify(event)]);
   const record=(await db.query('SELECT status,attempts,payload FROM notification_deliveries WHERE event_id=$1',[event.eventId])).rows[0];
   const matches=(await db.query('SELECT payload=$2::jsonb AS matches FROM notification_deliveries WHERE event_id=$1',[event.eventId,JSON.stringify(event)])).rows[0].matches;
   if(!matches){channel.nack(message,false,false);return;}
   if(record.status==='sent'){channel.ack(message);return;}
   if(record.status==='dead'){channel.nack(message,false,false);return;}
   const outcome=await deliver(record.attempts,async()=>{
    const response=await fetch((process.env.EMAIL_PROVIDER_URL??'http://mock-provider:8080')+'/email',{method:'POST',headers:{'Content-Type':'application/json','Idempotency-Key':event.eventId},body:JSON.stringify(event),signal:AbortSignal.timeout(Number(process.env.PROVIDER_TIMEOUT_MS??3000))});
    if(!response.ok)throw Error(`Email provider HTTP ${response.status}`);
    const body=await response.json() as {status?:string};
    if(body.status!=='sent')throw Error('Email provider did not confirm delivery');
   },async attempt=>{await db.query('UPDATE notification_deliveries SET attempts=$2,updated_at=now() WHERE event_id=$1',[event.eventId,attempt]);});
   await db.query('UPDATE notification_deliveries SET status=$2,attempts=$3,last_error=$4,updated_at=now() WHERE event_id=$1',[event.eventId,outcome.status,outcome.attempts,outcome.lastError]);
   if(outcome.status==='sent')channel.ack(message);else channel.nack(message,false,false);
  }catch(error){console.error('Delivery interrupted:',error instanceof Error?error.message:'unknown');await sleep(1000);try{channel.nack(message,false,true);}catch{}}
  finally{
   let broken=false;
   if(locked){try{await db.query('SELECT pg_advisory_unlock(hashtext($1))',[event.eventId]);}catch{broken=true;}}
   db.release(broken);
  }
 });
 ready=!session.ended;
 await session.done;
 }finally{
  session.stop();
  // Also discard the connection after a channel failure or startup failure; a new
  // session recreates the channel, queues and consumer instead of leaking sockets.
  try{await connection.close();}catch{}
 }
}
async function main(){while(!stopping){try{await connect();}catch(error){ready=false;console.error('Worker startup/reconnect:',error instanceof Error?error.message:'unknown');}if(!stopping)await sleep(3000);}}
process.on('SIGTERM',()=>{stopping=true;ready=false;server.close();void pool.end().finally(()=>process.exit(0));});
void main();
