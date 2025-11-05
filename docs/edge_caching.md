# Edge Caching & Static Delivery

Tenantra ships hashed assets via Vite, so we can leverage aggressive CDN caching without risking stale bundles. These guidelines align with the new Nginx rules.

## Immutable Assets

- Paths: `/assets/**` with hashed filenames (`index-<hash>.js`, `Card-<hash>.css`, etc.).
- Cache policy: `Cache-Control: public, max-age=31536000, immutable`.
- Host in a CDN bucket and enable `origin shield` or similar to reduce cache misses.

## HTML & Shell

- `index.html`, `robots.txt`, and other entrypoints should be cached for **60 seconds** with `stale-while-revalidate=600`. This allows fast rollouts while keeping a warm edge cache.
- CDN tip: enable `cache key normalization` so query strings don’t explode the cache (Vite includes hash, so variants are rare).

## Public Support Settings

- Endpoint: `/api/support/settings/public`.
- Cache policy: `Cache-Control: public, max-age=60, stale-while-revalidate=300`.
- Serves the theme color + other non-sensitive metadata. The host now sets the header automatically; ensure your CDN honours upstream directives.

## API & Auth

- All other API routes remain `no-cache`; avoid caching auth responses or tenant data.
- Add CDN rules to bypass cache for `/api/**` except the public settings path.

## Validation Checklist

1. After deploy, run:
   ```bash
   curl -I https://app.tenantra.tld/assets/index-<hash>.js
   curl -I https://app.tenantra.tld/index.html
   curl -I https://app.tenantra.tld/api/support/settings/public
   ```
   Verify cache headers match the policies above.
2. Confirm CDN respects the upstream `Cache-Control` values (set `respect origin headers` or override explicitly).
3. Enable Brotli (preferred) or gzip compression at the CDN to reduce first paint.

## Rollbacks

- Because bundles are immutable, rolling back means just pointing to the previous deploy (or copying the prior `dist/` snapshot). The CDN can keep the old hash cached, avoiding reload storms.
- Keep at least one previous bundle in the CDN bucket for quick fallback.***
