###########################################
# Frontend service Dockerfile for Tenantra #
###########################################

#
# This Dockerfile builds the Tenantra frontend (React/Vite).  It uses
# a multi-stage build to keep the final image small and secure.  The
# build stage installs Node dependencies and builds the static site,
# while the runtime stage uses Nginx to serve the compiled assets.  We
# deliberately avoid running `apt-get` in this Dockerfile because
# npm/node images already contain everything needed.  This ensures
# there is no possibility of stale APT lock files causing build
# failures.

# Build stage: compile the frontend assets
# Pin the Node base image to a specific digest for reproducibility and
# explicitly set the target platform.  Without the platform constraint
# BuildKit may attempt to pull a multi-arch manifest and fail when the
# digest is not available.  Using the pinned digest from the stable
# release and setting `--platform=linux/amd64` ensures the correct
# image is pulled.
# Use a pinned digest for the Node.js 20 Bookworm image.  The previous digest
# referenced in this Dockerfile was removed from Docker Hub, which caused
# builds to fail with a "not found" error.  The digest below corresponds
# to the current Node.js 20 Bookworm image as of October 2025.  Pinning
# the digest ensures reproducible builds and locks the image to a specific
# version.  If this digest becomes unavailable in the future, update it
# to the latest digest for node:20-bookworm.
FROM --platform=linux/amd64 node:20-bookworm@sha256:8cdc6b9b711af0711cc6139955cc1331fab5e0a995afd3260c52736fbc338059 AS build

# Set working directory
WORKDIR /app

# Copy package manifests and install dependencies with npm
# Note: build context is the repository root, so copy the frontend-specific
# package files explicitly.
COPY frontend/package.json frontend/package-lock.json ./
RUN --mount=type=cache,target=/root/.npm \
    # Use npm install in the dev build to tolerate minor lockfile mismatches
    # and avoid failing the Docker build during local development.
    npm install --legacy-peer-deps --no-audit --progress=false

# Copy the frontend source code into the build stage
COPY frontend/ ./

# Build the production-ready static files
RUN npm run build

# Runtime stage: serve files with nginx
FROM --platform=linux/amd64 nginx:stable@sha256:d9c62df87ab2f884f401f81e170f2dd3f7e0b0ba6983a144cf73f2015698a13c

# Configure Nginx to serve the build output
COPY --from=build /app/dist /usr/share/nginx/html
# Copy our curated frontend nginx config into the runtime image
COPY ../docker/nginx/frontend_default.conf /etc/nginx/conf.d/default.conf

# Generate a hardened nginx.conf within the image but include conf.d/*.conf
# so the baked-in `frontend_default.conf` is used. This avoids defining a
# competing server block with =404 which prevented SPA routes from falling
# back to /index.html.
RUN set -eux; \
        printf '%s\n' \
            'worker_processes auto;' \
            '' \
            '# Write the PID file into the world-writable /tmp directory.' \
            '# The default (/run/nginx.pid) is not writable in read-only containers.' \
            'pid /tmp/nginx.pid;' \
            '' \
            'events {' \
            '    worker_connections 1024;' \
            '}' \
            '' \
            'http {' \
            '    include       /etc/nginx/mime.types;' \
            '    default_type  application/octet-stream;' \
            '    sendfile        on;' \
            '    keepalive_timeout 65;' \
            '    # Place temporary files in /tmp (mounted as tmpfs via compose)' \
            '    client_body_temp_path /tmp/client_temp;' \
            '    proxy_temp_path       /tmp/proxy_temp_path;' \
            '    fastcgi_temp_path     /tmp/fastcgi_temp;' \
            '    uwsgi_temp_path       /tmp/uwsgi_temp;' \
            '    scgi_temp_path        /tmp/scgi_temp;' \
            '    # Load per-site configuration (our frontend_default.conf defines the server)' \
            '    include /etc/nginx/conf.d/*.conf;' \
            '}' > /etc/nginx/nginx.conf

# Expose the port the frontend listens on
EXPOSE 80

# Start Nginx in the foreground
CMD ["nginx", "-g", "daemon off;"]