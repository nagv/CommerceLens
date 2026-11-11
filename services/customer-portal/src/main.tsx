import React, {useEffect,useState} from 'react';
import {createRoot} from 'react-dom/client';
import {cartSummary,validateCheckout,checkoutAttempt,money,type Product,type Checkout,type Attempt,type Order,type Notification} from './domain';
import {ApiError,request} from './api';
import './styles.css';

const STORAGE='commercelens.checkout.v1';
function savedAttempt():Attempt|null {try {const value=JSON.parse(sessionStorage.getItem(STORAGE)||'null'); return value?.key && value?.body?.items ? value : null;} catch {return null;}}
function Status({value}:{value:string}) {return <span className={`status status-${value.toLowerCase()}`}>{value.replaceAll('_',' ')}</span>;}
function App() {
  const [tab,setTab]=useState<'shop'|'operations'>('shop');
  const [products,setProducts]=useState<Product[]>([]),[orders,setOrders]=useState<Order[]>([]),[notifications,setNotifications]=useState<Notification[]>([]);
  const [cart,setCart]=useState<Record<string,number>>({}),[email,setEmail]=useState(''),[postal,setPostal]=useState('');
  const [payment,setPayment]=useState<Checkout['paymentScenario']>('success'),[shipping,setShipping]=useState<Checkout['shippingScenario']>('success');
  const [attempt,setAttempt]=useState<Attempt|null>(savedAttempt),[selected,setSelected]=useState<Order|null>(null);
  const [busy,setBusy]=useState(false),[loading,setLoading]=useState(true),[error,setError]=useState(''),[notice,setNotice]=useState(''),[loadErrors,setLoadErrors]=useState<string[]>([]);
  async function refresh() {
    setLoading(true);
    const result=await Promise.allSettled([request<Product[]>('/api/products'),request<Order[]>('/api/orders'),request<Notification[]>('/api/notifications')]);
    const errors:string[]=[];
    if(result[0].status==='fulfilled')setProducts(result[0].value);else errors.push('Catalog unavailable. Start inventory and order services.');
    if(result[1].status==='fulfilled')setOrders(result[1].value);else errors.push('Order history unavailable.');
    if(result[2].status==='fulfilled')setNotifications(result[2].value);else errors.push('Notification worker unavailable. Orders can still be placed.');
    setLoadErrors(errors);setLoading(false);
  }
  useEffect(()=>{void refresh();},[]);
  const summary=cartSummary(products,cart);
  const pendingTotal=attempt ? cartSummary(products,Object.fromEntries(attempt.body.items.map(i=>[i.sku,i.quantity]))) : summary;
  function quantity(sku:string, n:number) {setCart(old=>{const next={...old}; if(n>0)next[sku]=n;else delete next[sku];return next;});}
  async function submit(event:React.FormEvent) {
    event.preventDefault();setError('');setNotice('');
    const body:Checkout={customerEmail:email.trim(),postalCode:postal.trim(),items:Object.entries(cart).map(([sku,quantity])=>({sku,quantity})),paymentScenario:payment,shippingScenario:shipping};
    if(!attempt){const invalid=validateCheckout(body,products);if(invalid){setError(invalid);return;}}
    const next=checkoutAttempt(body,attempt);
    try {sessionStorage.setItem(STORAGE,JSON.stringify(next));} catch {setError('Browser storage is unavailable. Enable session storage before checkout so retries remain safe.');return;}
    setAttempt(next);setBusy(true);
    try {
      const order=await request<Order>('/api/orders',{method:'POST',headers:{'Idempotency-Key':next.key},body:JSON.stringify(next.body)});
      setSelected(order);setNotice(`Order ${order.id} — ${order.status.replaceAll('_',' ')}.`);
    } catch(e) {
      const payload=e instanceof ApiError ? e.body as {order?:Order;id?:string;status?:string}:null;
      if(payload?.order)setSelected(payload.order);else if(payload?.id&&payload.status)setSelected(payload as Order);
      setError(e instanceof ApiError ? e.message : 'Connection interrupted. The order outcome may be unknown. Retry this same checkout to recover its status.');
    } finally {setBusy(false);await refresh();}
  }
  function newOrder() {
    if(attempt && !window.confirm('Start a different order? Check order history first: a previous payment may still be pending. Retrying the existing checkout is safer if its outcome is unknown.'))return;
    sessionStorage.removeItem(STORAGE);setAttempt(null);setCart({});setError('');setNotice('');setSelected(null);
  }
  async function detail(id:string) {try {setSelected(await request<Order>(`/api/orders/${encodeURIComponent(id)}`));setError('');}catch(e){setError(e instanceof Error?e.message:'Unable to load order.');}}
  return <div className="app">
    <header><a className="brand" href="/" aria-label="CommerceLens home"><span className="brand-mark">C<span>↗</span></span><span>Commerce<span className="light">Lens</span></span></a><div className="header-right"><span className="environment"><i/> LOCAL SANDBOX</span><span className="avatar">CL</span></div></header>
    <nav aria-label="Main navigation"><button className={tab==='shop'?'active':''} onClick={()=>setTab('shop')}>Storefront</button><button className={tab==='operations'?'active':''} onClick={()=>setTab('operations')}>Operations <span className="count">{orders.length}</span></button><span className="nav-note">One checkout. Connected services.</span></nav>
    <main>
      <section className="hero"><div><p className="eyebrow">COMMERCE, UNDER THE LENS</p><h1>{tab==='shop'?'Small essentials. Big connections.':'Every order tells a story.'}</h1><p>{tab==='shop'?'A real checkout journey through inventory, payments, shipping, and notifications.':'Follow orders across services and inspect delivery outcomes.'}</p></div><div className="hero-number"><span>06</span><small>independent services</small></div></section>
      <div className="mock-banner"><span>◈</span><p><strong>Demo provider mode.</strong> Payment, shipping, and email use local HTTP mocks. No real charge or message is sent.</p></div>
      {loadErrors.map(message=><div className="alert warning" role="status" key={message}>{message}</div>)}
      {error&&<div className="alert error" role="alert">{error}</div>}{notice&&<div className="alert success" role="status">{notice}</div>}
      {tab==='shop'?<div className="shop-layout"><section><div className="section-heading"><div><p className="eyebrow">THE COLLECTION</p><h2>Built for the curious.</h2></div><button className="text-button" onClick={()=>void refresh()} disabled={loading}>{loading?'Loading…':'↻ Refresh stock'}</button></div>
        <div className="products">{products.map((p,i)=><article className="product" key={p.sku}><div className={`product-art art-${i%3}`} aria-hidden="true"><span className="art-label">COMMERCE / ESSENTIALS</span><div className={`object object-${i%3}`}>{i%3===0?<><span>AGENTIC<br/>SYSTEMS</span><small>A FIELD GUIDE</small></>:i%3===1?<><b>⌘</b><small>MAKE SOMETHING</small></>:<b>C↗</b>}</div><span className="product-index">0{i+1}</span></div><div className="product-info"><small>{p.sku} · {p.available} available</small><h3>{p.name}</h3><div className="product-bottom"><strong>{money(p.priceCents)}</strong><button className="add-button" disabled={!!attempt||p.available<=0||(cart[p.sku]||0)>=p.available} onClick={()=>quantity(p.sku,(cart[p.sku]||0)+1)} aria-label={`Add ${p.name} to cart`}>+ Add{cart[p.sku]?` (${cart[p.sku]})`:''}</button></div></div></article>)}</div>
        {!loading&&!products.length&&<div className="empty">No products loaded. Start the backend services, then refresh.</div>}
        <div className="journey"><p className="eyebrow">BEHIND YOUR CHECKOUT</p><div><span>Reserve stock</span><b>→</b><span>Authorize payment</span><b>→</b><span>Create shipment</span><b>→</b><span>Send confirmation</span></div></div>
      </section><aside className="checkout"><div className="section-heading"><h2>Your checkout</h2><span className="count">{pendingTotal.count}</span></div>
        {attempt?<div className="attempt-note"><strong>Checkout saved</strong><p>{attempt.body.customerEmail} · {attempt.body.postalCode}</p><p>Retries reuse the same request and payment key, including after a page refresh.</p></div>:<div className="cart-lines">{products.filter(p=>cart[p.sku]).map(p=><div className="cart-line" key={p.sku}><div><strong>{p.name}</strong><small>{money(p.priceCents)} each</small></div><input aria-label={`Quantity for ${p.name}`} type="number" min="0" max={p.available} value={cart[p.sku]} onChange={e=>quantity(p.sku,Math.max(0,Math.floor(Number(e.target.value)||0)))}/></div>)}{!summary.count&&<p className="muted">Your next idea starts with something small. Add an essential to begin.</p>}</div>}
        <form onSubmit={submit}><fieldset disabled={busy||!!attempt}><label>Email address<input type="email" placeholder="you@example.com" value={email} onChange={e=>setEmail(e.target.value)} required={!attempt}/></label><label>Postal code<input placeholder="10001" maxLength={20} value={postal} onChange={e=>setPostal(e.target.value)} required={!attempt}/></label><details className="scenarios"><summary>Test a service scenario</summary><label>Payment provider<select value={payment} onChange={e=>setPayment(e.target.value as Checkout['paymentScenario'])}><option value="success">Authorization succeeds</option><option value="decline">Payment declined</option><option value="timeout">Provider timeout</option></select></label><label>Shipping provider<select value={shipping} onChange={e=>setShipping(e.target.value as Checkout['shippingScenario'])}><option value="success">Shipment created</option><option value="failure">Provider failure</option></select></label><p>Use an email containing <code>fail-email</code> to test notification retries.</p></details></fieldset>
        <div className="totals"><div><span>Subtotal estimate</span><span>{money(pendingTotal.subtotalCents)}</span></div><div><span>Shipping</span><span>{money(pendingTotal.shippingCents)}</span></div><div className="grand-total"><strong>Total estimate</strong><strong>{money(pendingTotal.totalCents)}</strong></div></div><p className="fine-print">Final price and stock are validated by the services.</p><button className="primary" type="submit" disabled={busy||(!attempt&&!summary.count)}>{busy?'Processing checkout…':attempt?'Retry / recover this order':'Place demo order'} <span>↗</span></button>{attempt&&<button className="text-button new-order" type="button" disabled={busy} onClick={newOrder}>Start a new order</button>}</form>
      </aside></div>:<section><div className="metrics"><div><small>Orders recorded</small><strong>{orders.length}</strong></div><div><small>Confirmed</small><strong>{orders.filter(o=>o.status.toLowerCase()==='confirmed').length}</strong></div><div><small>Needs attention</small><strong>{orders.filter(o=>o.status.toLowerCase()!=='confirmed').length}</strong></div><div><small>Notification records</small><strong>{notifications.length}</strong></div></div><div className="section-heading"><h2>Order activity</h2><button className="text-button" disabled={loading} onClick={()=>void refresh()}>{loading?'Refreshing…':'↻ Refresh activity'}</button></div><div className="table-wrap"><table><thead><tr><th>Order</th><th>Customer</th><th>Status</th><th>Total</th><th>Created</th><th/></tr></thead><tbody>{orders.map(o=><tr key={o.id}><td><code>{o.id.slice(0,8)}</code></td><td>{o.customerEmail}</td><td><Status value={o.status}/></td><td>{money(o.totalCents)}</td><td>{new Date(o.createdAt).toLocaleString()}</td><td><button className="text-button" onClick={()=>void detail(o.id)}>Details ↗</button></td></tr>)}</tbody></table>{!orders.length&&<div className="empty">No orders yet. Place a demo order in the storefront.</div>}</div><h2 className="notifications-title">Notification delivery</h2><div className="notification-list">{notifications.map(n=><article key={n.eventId}><div><code>{n.orderId.slice(0,8)}</code><Status value={n.status}/></div><p>{n.attempts} delivery attempt{n.attempts===1?'':'s'}</p>{n.lastError&&<p className="failure">{n.lastError}</p>}</article>)}{!notifications.length&&<p className="muted">Delivery records appear after confirmed orders are consumed. Refresh to check progress.</p>}</div></section>}
      {selected&&<section className="order-detail" aria-label="Selected order"><div className="section-heading"><div><p className="eyebrow">ORDER DETAILS</p><h2>{selected.id}</h2></div><button className="text-button" onClick={()=>setSelected(null)}>Close</button></div><Status value={selected.status}/><div className="detail-grid"><p><small>Customer</small>{selected.customerEmail}</p><p><small>Total</small>{money(selected.totalCents)}</p><p><small>Tracking</small>{selected.trackingNumber||'Not available'}</p><p><small>Payment</small>{selected.paymentId||'Not available'}</p></div>{selected.failureReason&&<p className="failure">{selected.failureReason}</p>}<ul>{selected.items?.map(i=><li key={i.sku}>{i.name||i.sku} × {i.quantity}</li>)}</ul></section>}
      <footer><span>CommerceLens <span className="muted">/ Connected commerce, made visible.</span></span><span>Application assistant · planned next</span></footer>
    </main>
  </div>;
}
createRoot(document.getElementById('root')!).render(<React.StrictMode><App/></React.StrictMode>);
