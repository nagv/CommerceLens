import {EventEmitter} from 'node:events';

export function watchSession(connection:EventEmitter,onUnavailable:()=>void){
 let ended=false;
 let resolve!:()=>void;
 const done=new Promise<void>(r=>{resolve=r;});
 const stop=()=>{if(!ended){ended=true;onUnavailable();resolve();}};
 connection.on('error',stop);
 connection.once('close',stop);
 return {done,stop,get ended(){return ended;},watchChannel(channel:EventEmitter){
  // Keep an error listener throughout teardown: EventEmitter errors otherwise terminate Node.
  channel.on('error',stop);
  channel.once('close',stop);
 }};
}
