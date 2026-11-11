FROM golang:1.23-alpine AS build
WORKDIR /app
COPY go.* ./
RUN go mod download
COPY . .
RUN go test ./... && CGO_ENABLED=0 go build -o /inventory .
FROM alpine:3.21
RUN apk add --no-cache ca-certificates && adduser -D app
USER app
COPY --from=build /inventory /inventory
EXPOSE 8080
ENTRYPOINT ["/inventory"]
