export type Product = {sku:string; name:string; priceCents:number; available:number};
export type Checkout = {customerEmail:string; postalCode:string; items:{sku:string;quantity:number}[]; paymentScenario:'success'|'decline'|'timeout'; shippingScenario:'success'|'failure'};
export type Attempt = {key:string;body:Checkout};
export type Order = {id:string;status:string;customerEmail:string;postalCode:string;items:{sku:string;name?:string;quantity:number;priceCents?:number}[];subtotalCents:number;shippingCents:number;totalCents:number;paymentId?:string;trackingNumber?:string;failureReason?:string;createdAt:string};
export type Notification = {eventId:string;orderId:string;status:string;attempts:number;lastError?:string};
export function cartSummary(products:Product[], cart:Record<string,number>) {
  let subtotalCents=0, count=0;
  for (const p of products) { const q=cart[p.sku]||0; subtotalCents+=p.priceCents*q; count+=q; }
  const shippingCents=count ? 500 : 0;
  return {subtotalCents,shippingCents,totalCents:subtotalCents+shippingCents,count};
}
export function validateCheckout(body:Checkout, products:Product[]):string|null {
  if (!body.items.length) return 'Add a product to your cart.';
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(body.customerEmail)) return 'Enter a valid email address.';
  if (!body.postalCode.trim() || body.postalCode.trim().length>20) return 'Enter a postal code (up to 20 characters).';
  for (const item of body.items) {
    if (!Number.isInteger(item.quantity) || item.quantity<1) return 'Quantities must be positive whole numbers.';
    const product=products.find(p=>p.sku===item.sku);
    if (!product || item.quantity>product.available) return 'Your cart exceeds available stock. Refresh the catalog.';
  }
  return null;
}
export function checkoutAttempt(body:Checkout, previous:Attempt|null, makeKey:()=>string=()=>crypto.randomUUID()):Attempt {
  return previous ?? {key:makeKey(),body:structuredClone(body)};
}
export const money=(cents:number)=>new Intl.NumberFormat('en-US',{style:'currency',currency:'USD'}).format((cents||0)/100);
