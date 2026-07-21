# ==========================================
# Stage 1: Build stage
# ==========================================
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package descriptors
COPY package*.json ./

# Install packages
RUN npm ci

# Copy project files
COPY . .

# Build arg for API URL — baked into the build at compile time
# Default: /api (relative, proxied by Nginx)
ARG VITE_API_URL=/api
ENV VITE_API_URL=$VITE_API_URL

# Build Vite application
RUN npm run build


# ==========================================
# Stage 2: Run stage
# ==========================================
FROM nginx:1.25-alpine

# Copy built static assets from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy custom Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Backend URL for Nginx proxy — can be overridden at runtime
# Default: http://backend:8000 (Docker Compose service name)
ARG BACKEND_URL=http://backend:8000
ENV BACKEND_URL=$BACKEND_URL

# Expose port
EXPOSE 80

# Run nginx in foreground
CMD ["nginx", "-g", "daemon off;"]