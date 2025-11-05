# Feature Flags and SMTP Setup (Dev)

This guide summarizes the runtime feature flags and SMTP options used by the Tenantra backend during development.

## Flags

- `TENANTRA_ENABLE_PANORAMA_STUB`
  - Scope: Networking / Panorama policy drift prototype
  - Default: disabled (module returns `skipped`)
  - When enabled: the `panorama-policy-drift` module returns a stub success payload
  - How to enable: set to `true` (e.g. compose override or shell env)

- `TENANTRA_ENABLE_AWS_LIVE`
  - Scope: AWS IAM baseline runner
  - Default: disabled (runner evaluates only provided parameters)
  - When enabled: tries live AWS IAM listing (requires `boto3` and AWS credentials in env/profile). If not available, returns `skipped` with a reason (e.g., `boto3_missing`).
  - Safe for CI: default remains disabled; tests use parameter-mode unless explicitly opted-in.

Related tuning envs (used by the live IAM runner):

- `TENANTRA_AWS_MAX_KEY_AGE` (default `90`)
- `TENANTRA_AWS_REQUIRE_MFA` (default `true`)

## SMTP Settings

The backend sends notifications via SMTP. In development you can:

- Leave SMTP blank (default behavior is to no-op and report `False` on send)
- Use a local MailHog server for out-of-box testing

Environment variables (set on the `backend` service):

- `SMTP_HOST` (e.g., `mailhog` in dev)
- `SMTP_PORT` (e.g., `1025` for MailHog)
- `SMTP_USER` / `SMTP_PASS` (usually empty for MailHog)
- `SMTP_FROM` (e.g., `no-reply@tenantra.local`)
- `SMTP_TLS` (`true`/`false`)

## Compose Overlays

Development override (`docker/docker-compose.override.dev.yml`) already sets:

- `TENANTRA_ENABLE_PANORAMA_STUB=true`
- Example SMTP envs (empty by default)

MailHog overlay (`docker/docker-compose.override.mailhog.yml`):

```yaml
services:
  mailhog:
    image: mailhog/mailhog:latest
    ports:
      - "1025:1025"   # SMTP
      - "8025:8025"   # Web UI

  backend:
    environment:
      SMTP_HOST: mailhog
      SMTP_PORT: "1025"
      SMTP_TLS: "false"
      SMTP_FROM: "no-reply@tenantra.local"
```

Run dev stack with MailHog:

```bash
docker compose \
  -f docker/docker-compose.yml \
  -f docker/docker-compose.override.dev.yml \
  -f docker/docker-compose.override.mailhog.yml \
  up -d backend frontend db mailhog

# View MailHog UI
open http://localhost:8025
```
