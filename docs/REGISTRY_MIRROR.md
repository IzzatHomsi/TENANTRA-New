Docker Registry Mirror / Fallback
=================================

Long builds can be caused by Docker Hub throttling or outages. Configure a registry mirror to improve reliability:

Docker Desktop (Windows/macOS)

1) Open Docker Desktop → Settings → Docker Engine
2) Add (or merge) the following JSON:

{
  "registry-mirrors": ["https://<your-mirror-host>"]
}

3) Apply & restart Docker.

Self-managed daemon (Linux)

- Edit `/etc/docker/daemon.json` and set `registry-mirrors` similarly, then `systemctl restart docker`.

Image fallback strategy

- If you host a private mirror for base images (python, node, nginx, grafana, prom), tag/push those images to your mirror and update compose to reference them (e.g., `mirror.local/library/nginx@sha256:...`).
- Keep digests pinned for reproducibility.

