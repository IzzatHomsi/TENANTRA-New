# Content Security Policy Hardening

The platform now enforces a stricter Content-Security-Policy that blocks inline scripts and limits network access to the primary origin.

## Default Policy

Applied by both Nginx and the FastAPI `SecurityHeadersMiddleware`:

```
default-src 'self';
script-src 'self';
style-src 'self';
img-src 'self' data:;
font-src 'self';
connect-src 'self';
frame-ancestors 'none';
base-uri 'self';
form-action 'self';
```

### Notes

- Inline scripts/styles are blocked. All frontend bundles must remain hashed files served from `/assets/**`.
- `img-src` allows `data:` URIs for small inline images used in the UI.
- Grafana proxy responses continue to bypass CSP (the middleware skips headers for `/grafana`), so the embedded dashboards can load their own assets via the proxied origin.

## Overrides

- To customize the policy, set the `SEC_CSP` environment variable on the backend (FastAPI) or adjust `add_header Content-Security-Policy` in `nginx/conf.d/*`.
- When allowing extra origins (e.g., a CDN for fonts), extend `script-src`, `style-src`, or `font-src` as appropriate. Example:

```
SEC_CSP="default-src 'self'; script-src 'self' https://cdn.tenantra.com; style-src 'self' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'"
```

## Validation Checklist

1. After deploy, verify headers:
   ```bash
   curl -I https://app.tenantra.tld | grep -i content-security-policy
   curl -I https://app.tenantra.tld/app | grep -i content-security-policy
   ```
2. Exercise the app and confirm there are no CSP violations in the browser console.
3. If Grafana dashboards fail to load, ensure they are accessed via `/grafana` so the proxy removes the CSP header for those responses.

Keep this document updated when adding new third-party assets or script hosts.
