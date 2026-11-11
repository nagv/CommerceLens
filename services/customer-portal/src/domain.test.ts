import {describe, it, expect} from 'vitest';
import {cartSummary, validateCheckout, checkoutAttempt} from './domain';

const products = [{sku:'BOOK-001', name:'Book', priceCents:2900, available:3}];
const body = {customerEmail:'test@example.com',postalCode:'10001',items:[{sku:'BOOK-001',quantity:2}],paymentScenario:'success' as const,shippingScenario:'success' as const};
describe('cart and checkout', () => {
  it('calculates cents without trusting checkout prices', () => {
    expect(cartSummary(products, {'BOOK-001':2})).toEqual({subtotalCents:5800,shippingCents:500,totalCents:6300,count:2});
    expect(cartSummary(products, {})).toEqual({subtotalCents:0,shippingCents:0,totalCents:0,count:0});
  });
  it('rejects empty, malformed and unavailable carts', () => {
    expect(validateCheckout({...body,items:[]},products)).toContain('Add a product');
    expect(validateCheckout({...body,customerEmail:'invalid'},products)).toContain('email');
    expect(validateCheckout({...body,items:[{sku:'BOOK-001',quantity:4}]},products)).toContain('stock');
    expect(validateCheckout({...body,items:[{sku:'BOOK-001',quantity:1.5}]},products)).toContain('whole');
    expect(validateCheckout(body,products)).toBeNull();
  });
  it('reuses the original payload and key after timeout, even if fields changed', () => {
    const first = checkoutAttempt(body, null, ()=>'key-1');
    const retry = checkoutAttempt({...body,postalCode:'20002'},first, ()=>'key-2');
    expect(retry).toBe(first);
    expect(retry.body.postalCode).toBe('10001');
  });
});
