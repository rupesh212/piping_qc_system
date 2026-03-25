# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm ci --prefer-offline

COPY . .

ARG VITE_API_URL=
ENV VITE_API_URL=$VITE_API_URL

RUN npm run build


# Serve stage
FROM nginx:alpine

# Use non-root nginx user where possible
# nginx:alpine already runs worker processes as the unprivileged 'nginx' user;
# the master process must run as root to bind port 80.
# We copy a custom nginx.conf that does not require privileged ports for workers.

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget -q http://localhost/ -O /dev/null || exit 1

CMD ["nginx", "-g", "daemon off;"]
