# SSR Deployment Guide

Tenantra now ships a production-ready SSR bundle that streams HTML and hydrates React Query state.

## Build Steps

```bash
cd frontend
npm run build            # SPA assets
npm run build:ssr        # SSR bundle (dist-ssr/entry-server.js)
```

## Serve the App

```bash
SSR_API_BASE=https://api.tenantra.tld \
SSR_PORT=4173 \
SSR_SSL_CERT=/etc/ssl/certs/tenantra.crt \
SSR_SSL_KEY=/etc/ssl/private/tenantra.key \
npm run ssr:serve
```

- Without `SSR_SSL_*` the server falls back to HTTP.
- The server streams HTML (`renderToPipeableStream`), dehydrates React Query caches, and serves static assets from `dist/`.

## Loaders

- Loader stack lives in `frontend/server/loaders.mjs`.
- Currently prefetches public support settings so the shell theme renders before hydration.
- Add additional loaders to prefetch auth/session data once cookies or headers are available.

## Measuring TTFB

```bash
curl -w "TTFB: %{time_starttransfer}\nTotal: %{time_total}\n" \
  -o /dev/null -s https://app.tenantra.tld/app/dashboard
```

- Goal: sub-100 ms TTFB for cached responses.
- Monitor `http_request_duration_seconds` Prometheus metric for backend latency.

## CDN/Proxy

- Terminate TLS upstream (e.g., Nginx) and proxy `/` to the SSR server.
- Continue serving `/assets/**` via CDN with immutable caching as documented in `docs/edge_caching.md`.

Keep iterating on loaders to cover authenticated data and leverage React Query’s `dehydrate/hydrate` for cache reuse.
