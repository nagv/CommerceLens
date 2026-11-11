using System.Net;
using Xunit;
public class ShippingTests {
 [Fact] public async Task PassesOrderKeyAndReturnsTracking() {
  var handler=new Handler(); var provider=new ShippingProvider(new HttpClient(handler){BaseAddress=new Uri("http://provider")});
  var result=await provider.Create(new ShipmentRequest("o1","10001","success"),CancellationToken.None);
  Assert.Equal("track-1",result.TrackingNumber); Assert.Equal("o1",handler.Key);
 }
 [Fact] public async Task FailureDoesNotProduceShipment() {
  var provider=new ShippingProvider(new HttpClient(new Handler{Code=HttpStatusCode.ServiceUnavailable}){BaseAddress=new Uri("http://provider")});
  var error=await Assert.ThrowsAsync<ProviderException>(()=>provider.Create(new ShipmentRequest("o1","10001","failure"),CancellationToken.None));
  Assert.Equal("unknown",error.Status);
 }
 [Fact] public async Task ExplicitRejectionIsSafeToCompensate() {
  var provider=new ShippingProvider(new HttpClient(new Handler{Code=HttpStatusCode.UnprocessableEntity}){BaseAddress=new Uri("http://provider")});
  var error=await Assert.ThrowsAsync<ProviderException>(()=>provider.Create(new ShipmentRequest("o1","10001","failure"),CancellationToken.None));
  Assert.Equal(422,error.Code);Assert.Equal("failed",error.Status);
 }
 class Handler:HttpMessageHandler {
  public string? Key; public HttpStatusCode Code=HttpStatusCode.OK;
  protected override Task<HttpResponseMessage> SendAsync(HttpRequestMessage request,CancellationToken token){
   Key=request.Headers.GetValues("Idempotency-Key").Single();
   return Task.FromResult(new HttpResponseMessage(Code){Content=new StringContent("{\"shipmentId\":\"ship-1\",\"status\":\"created\",\"trackingNumber\":\"track-1\",\"shippingCents\":500}",System.Text.Encoding.UTF8,"application/json")});
  }
 }
}
