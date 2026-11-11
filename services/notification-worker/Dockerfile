FROM node:22-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY tsconfig.json .
COPY src src
COPY test test
RUN npm test && npm run build
FROM node:22-alpine AS runtime
WORKDIR /app
COPY package*.json ./
RUN npm ci --omit=dev
COPY --from=build /app/dist dist
USER node
EXPOSE 8080
CMD ["node","dist/main.js"]
