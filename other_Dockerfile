# Frontend Build Stage
FROM node:20.10.0 as frontend-builder
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm install -g @angular/cli
RUN npm install
COPY frontend ./
RUN ng build --configuration=production

# Backend Build Stage
FROM node:20.10.0 as backend-builder
WORKDIR /backend
COPY backend/package*.json ./
RUN npm install
COPY backend ./

# Final Stage
FROM node:20.10.0-alpine
WORKDIR /app
COPY --from=frontend-builder /frontend/dist/frontend ./public
COPY --from=backend-builder /backend ./
EXPOSE 80
CMD ["node", "server.js"]
