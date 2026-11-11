export type Event = { eventId:string;orderId:string;customerEmail:string;totalCents:number;trackingNumber:string };
export function parseEvent(raw:string):Event {
 const data=JSON.parse(raw);
 if(!data || !['eventId','orderId','customerEmail','trackingNumber'].every(k=>typeof data[k]==='string'&&data[k].length>0&&data[k].length<=320)|| !Number.isSafeInteger(data.totalCents)||data.totalCents<0 || !data.customerEmail.includes('@')) throw Error('Invalid order.confirmed event');
 return data;
}
export async function deliver(prior:number,send:()=>Promise<void>,beforeAttempt:(attempt:number)=>Promise<void>,sleep:(ms:number)=>Promise<void> = ms=>new Promise(r=>setTimeout(r,ms))){
 let attempts=prior,lastError='Attempt limit reached';
 while(attempts<3){
  attempts++; await beforeAttempt(attempts);
  try {await send(); return {status:'sent',attempts,lastError:null};}
  catch(error){lastError=error instanceof Error?error.message:'Provider failure';if(attempts<3)await sleep(250*attempts);}
 }
 return {status:'dead',attempts,lastError};
}
