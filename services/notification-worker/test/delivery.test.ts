import {test} from 'node:test';
import assert from 'node:assert/strict';
import {deliver, parseEvent} from '../src/delivery.js';
test('event validation rejects malformed and missing identifiers',()=>{
 assert.throws(()=>parseEvent('{}')); assert.throws(()=>parseEvent('bad json'));
 assert.equal(parseEvent(JSON.stringify({eventId:'e1',orderId:'o1',customerEmail:'a@b.com',totalCents:3000,trackingNumber:'t1'})).orderId,'o1');
});
test('bounded attempts stop after success and preserve prior attempt count',async()=>{
 let attempts=0; const saved:number[]=[];
 const result=await deliver(1,async()=>{attempts++;if(attempts===1)throw Error('provider down')},async(n)=>{saved.push(n)},async()=>{});
 assert.equal(result.status,'sent');assert.equal(result.attempts,3);assert.deepEqual(saved,[2,3]);
});
test('three failures terminate as dead with no fourth attempt',async()=>{
 let calls=0;const result=await deliver(0,async()=>{calls++;throw Error('provider down')},async()=>{},async()=>{});
 assert.equal(calls,3);assert.equal(result.status,'dead');assert.equal(result.lastError,'provider down');
});
