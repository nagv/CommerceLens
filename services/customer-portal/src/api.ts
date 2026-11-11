export class ApiError extends Error {
  constructor(message:string, public status:number, public body:unknown) {super(message);}
}
export async function request<T>(path:string, options:RequestInit={}):Promise<T> {
  const response=await fetch(path,{...options,headers:{'Content-Type':'application/json',...options.headers},signal:AbortSignal.timeout(30000)});
  const text=await response.text();
  let body:unknown;
  try {body=text ? JSON.parse(text):null;} catch {throw new ApiError('Service returned an unreadable response. Check the services and retry.',response.status,null);}
  if (!response.ok) {
    const error=body as {message?:string;detail?:string;failureReason?:string};
    throw new ApiError(error?.message || error?.failureReason || (typeof error?.detail==='string' ? error.detail : '') || `Request failed (${response.status}).`,response.status,body);
  }
  return body as T;
}
