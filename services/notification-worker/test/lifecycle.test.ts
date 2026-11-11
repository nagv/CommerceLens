import {test} from 'node:test';
import assert from 'node:assert/strict';
import {EventEmitter} from 'node:events';
import {watchSession} from '../src/lifecycle.js';

test('channel error is handled and immediately makes worker unavailable',async()=>{
 const connection=new EventEmitter(),channel=new EventEmitter();let unavailable=0;
 const session=watchSession(connection,()=>{unavailable++;});session.watchChannel(channel);
 assert.doesNotThrow(()=>channel.emit('error',Error('channel protocol error')));
 assert.equal(session.ended,true);await session.done;assert.equal(unavailable,1);
 channel.emit('close');connection.emit('close');assert.equal(unavailable,1);
});
test('channel-only close releases reconnect loop while connection stays open',async()=>{
 const connection=new EventEmitter(),channel=new EventEmitter();
 const session=watchSession(connection,()=>{});session.watchChannel(channel);
 channel.emit('close');assert.equal(session.ended,true);await session.done;
});
test('early connection closure and consumer cancellation cannot restore readiness',async()=>{
 const connection=new EventEmitter();let unavailable=0;
 const session=watchSession(connection,()=>{unavailable++;});
 connection.emit('close');session.stop();
 assert.equal(session.ended,true);await session.done;assert.equal(unavailable,1);
});
