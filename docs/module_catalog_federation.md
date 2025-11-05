# Module Catalog Federation Checklist

This project now ships the Module Catalog as a standalone remote bundle so you can stream the experience to tenants without bloating the host shell. Use this guide to publish and wire it up end-to-end.

## 1. Build the Remote

```bash
cd frontend
npm run build:module-catalog-remote
```

The artefacts land in `frontend/dist/catalog-remote/`:

- `remoteEntry.js` – the federation manifest
- `assets/*.js|css` – the compiled chunks

## 2. Publish the Artefacts

Upload the entire `dist/catalog-remote/` directory to your CDN or static bucket. Keep the relative structure intact so `remoteEntry.js` can resolve its sibling files.

Example (AWS S3 + CloudFront):

```bash
aws s3 sync dist/catalog-remote/ s3://cdn.tenantra.com/catalog-remote/ --delete
```

Once the files are in place, the manifest is typically reachable at:

```
https://cdn.tenantra.com/catalog-remote/remoteEntry.js
```

## 3. Point the Host at the Remote

Configure the following environment variables for the host build/runtime:

| Variable | Purpose |
|----------|---------|
| `VITE_REMOTE_MODULE_CATALOG_URL` | URL to `remoteEntry.js` |
| `VITE_REMOTE_MODULE_CATALOG_SCOPE` | Remote scope name (`tenantra_catalog`) |
| `VITE_REMOTE_MODULE_CATALOG_MODULE` | Module exposed by the remote (`./ModuleCatalog`) |

Example `.env.production` snippet:

```
VITE_REMOTE_MODULE_CATALOG_URL=https://cdn.tenantra.com/catalog-remote/remoteEntry.js
VITE_REMOTE_MODULE_CATALOG_SCOPE=tenantra_catalog
VITE_REMOTE_MODULE_CATALOG_MODULE=./ModuleCatalog
```

Rebuild / redeploy the host after updating the env.

## 4. Verify

1. Start the host (SSR dev server or production deployment) with the new env vars.
2. Load `/app/modules`.
3. In browser dev tools, confirm the network request to `remoteEntry.js` succeeds and the page renders.
4. Temporarily block the URL to ensure the fallback (`ModuleCatalogLocal`) still works.

## 5. Operate & Roll Back

- Cache policy: serve `remoteEntry.js` with a short TTL (or cache-busting file names) so new deployments roll out quickly.
- Rollbacks: publish the previous `dist/catalog-remote/` snapshot and revert the CDN pointer if a release regresses.
- Feature flags: gate the remote by tenant by setting `VITE_REMOTE_MODULE_CATALOG_URL` (or injecting a per-tenant override via settings) before rendering the route.

Keep this document updated as the federation footprint expands to other modules.***
