using System.Net.Http.Json;
using System.Text.Json;

var builder = WebApplication.CreateBuilder(args);
builder.WebHost.UseUrls("http://0.0.0.0:8080");
builder.Services.AddHttpClient<ShippingProvider>(client => {
 client.BaseAddress = new Uri(Environment.GetEnvironmentVariable("SHIPPING_PROVIDER_URL") ?? "http://mock-provider:8080");
 client.Timeout = TimeSpan.FromSeconds(double.Parse(Environment.GetEnvironmentVariable("PROVIDER_TIMEOUT_SECONDS") ?? "3",System.Globalization.CultureInfo.InvariantCulture));
});
var app = builder.Build();
app.MapGet("/health", () => Results.Ok(new {status="ok"}));
app.MapGet("/api/shipping/rate", () => Results.Ok(new {shippingCents=500,currency="USD"}));
app.MapPost("/api/shipments", async (ShipmentRequest input, ShippingProvider provider, CancellationToken token) => {
 if(string.IsNullOrWhiteSpace(input.OrderId) || input.OrderId.Length>128 || string.IsNullOrWhiteSpace(input.PostalCode) || input.PostalCode.Length>32 || input.Scenario is not ("success" or "failure"))
  return Results.BadRequest(new {message="Valid orderId, postalCode and scenario are required"});
 try {return Results.Ok(await provider.Create(input,token));}
 catch(OperationCanceledException){return Results.Json(new {message="Shipping provider timed out; shipment outcome unknown",status="unknown"},statusCode:504);}
 catch(ProviderException e){return Results.Json(new {message=e.Message,status=e.Status},statusCode:e.Code);}
 catch(HttpRequestException){return Results.Json(new {message="Shipping provider unavailable; shipment outcome unknown",status="unknown"},statusCode:502);}
 catch(JsonException){return Results.Json(new {message="Invalid shipping provider response; shipment outcome unknown",status="unknown"},statusCode:502);}
});
app.Run();

public record ShipmentRequest(string OrderId,string PostalCode,string Scenario="success");
public record Shipment(string ShipmentId,string Status,string TrackingNumber,int ShippingCents);
public class ProviderException(string message,int code=502,string status="unknown"):Exception(message){public int Code{get;}=code; public string Status{get;}=status;}
public class ShippingProvider(HttpClient client){
 public async Task<Shipment> Create(ShipmentRequest input,CancellationToken token){
  using var request=new HttpRequestMessage(HttpMethod.Post,"/shipments"){Content=JsonContent.Create(input)};
  request.Headers.Add("Idempotency-Key",input.OrderId);
  using var response=await client.SendAsync(request,token);
  if(!response.IsSuccessStatusCode){
   // Only an explicit provider rejection proves no shipment was created.
   if(response.StatusCode==System.Net.HttpStatusCode.UnprocessableEntity)
    throw new ProviderException("Shipping request rejected",422,"failed");
   throw new ProviderException("Shipping provider unavailable; shipment outcome unknown");
  }
  var shipment=await response.Content.ReadFromJsonAsync<Shipment>(cancellationToken:token);
  if(shipment is null || shipment.Status!="created" || string.IsNullOrWhiteSpace(shipment.ShipmentId) || string.IsNullOrWhiteSpace(shipment.TrackingNumber) || shipment.ShippingCents!=500)
   throw new ProviderException("Invalid shipping provider response; shipment outcome unknown");
  return shipment;
 }
}
