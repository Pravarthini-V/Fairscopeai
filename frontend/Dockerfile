# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci --legacy-peer-deps

COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine

RUN apk add --no-cache gettext

COPY --from=builder /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf.template

EXPOSE 80

# Substitute $BACKEND_URL at runtime then start nginx.
# Set BACKEND_URL in your Railway frontend service to the backend's internal URL,
# e.g. http://backend.railway.internal:8000
CMD ["/bin/sh", "-c", "[ -n \"$BACKEND_URL\" ] || { echo 'ERROR: BACKEND_URL is not set'; exit 1; } && envsubst '$BACKEND_URL' < /etc/nginx/conf.d/default.conf.template > /etc/nginx/conf.d/default.conf && nginx -g 'daemon off;'"]
