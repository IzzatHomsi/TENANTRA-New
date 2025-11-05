Edge dev nginx image

Why we bake the edge nginx image for local Windows dev

- Bind-mounts on Windows (especially for nginx configs) commonly cause issues with permission/line-ending differences, file locking, and path quoting when Docker Desktop translates Windows host paths into container mounts.
- Mounting a host nginx config into a running container can also introduce duplicate directive errors or missing include files (e.g., referencing certs) that exist on the host but not in the container image.
- Baking the edge image (copying repo nginx configs into the image at build time) produces a reproducible environment across developer machines and CI, and avoids many Windows-specific bind-mount pitfalls.

How to use

- Build and start via compose (the override builds the `nginx` edge image):

  docker compose -f docker/docker-compose.yml -f docker/docker-compose.override.nginx.yml build nginx
  docker compose -f docker/docker-compose.yml -f docker/docker-compose.override.nginx.yml up -d nginx

- The edge proxy will be available on host port 80 (127.0.0.1:80) and will forward `/` to the frontend and `/api` to the backend using service names inside the compose network.
- For direct frontend debugging you can use the published frontend port 8080:

  http://127.0.0.1:8080/

Recommendations

- Use the edge proxy for a production-like experience (same-origin, cookies, CORS testing).
- Use the direct frontend port (8080) for fast static-asset debugging.
- If you need to iterate on nginx config frequently, consider using a short-lived developer image with the configs copied at build time and rebuild frequently rather than bind-mounting on Windows.

If you want, I can add a small script `docker/rebuild-edge.ps1` to automate the build/start steps and show logs.
