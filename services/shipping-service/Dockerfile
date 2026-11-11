FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src
COPY . .
RUN dotnet restore Shipping.csproj
FROM build AS test
RUN dotnet test tests/Shipping.Tests.csproj -c Release
FROM build AS publish
RUN dotnet publish Shipping.csproj -c Release -o /out --no-restore
FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS runtime
WORKDIR /app
COPY --from=publish /out .
USER $APP_UID
EXPOSE 8080
ENTRYPOINT ["dotnet","Shipping.dll"]
