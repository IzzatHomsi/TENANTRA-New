# Dev Stacks (Notifications, Exports, Observability, Scheduler)

Convenience overlays and scripts to run focused dev stacks for phases 4 through 7.

## Notifications (MailHog)

- Overlay: `docker/docker-compose.override.mailhog.yml`
- Scripts:
  - PowerShell: `scripts/dev_up_phase4_notifications.ps1` (add `-WithWorker` to include the notifications worker)
  - Bash: `scripts/dev_up_phase4_notifications.sh` (`WITH_WORKER=1` to include worker)

Examples:

```powershell
./scripts/dev_up_phase4_notifications.ps1 -WithWorker
```

```bash
WITH_WORKER=1 ./scripts/dev_up_phase4_notifications.sh
```

MailHog UI: http://localhost:8025

## Exports/General (Exposed ports)

- Overlay: `docker/docker-compose.override.expose.yml` (binds backend:5000, frontend:8080 on host)
- Script: `scripts/dev_up_phase5_exports.ps1`

```powershell
./scripts/dev_up_phase5_exports.ps1
```

## Observability (Prometheus + Grafana)

- Overlay: `docker/docker-compose.override.observability.yml`
- Scripts: `scripts/dev_up_phase6_observability.ps1`, `scripts/dev_up_phase6_observability.sh`

```powershell
./scripts/dev_up_phase6_observability.ps1
```

```bash
./scripts/dev_up_phase6_observability.sh
```

Grafana: http://localhost:3000, Prometheus: http://localhost:9090

## Scheduler (Module scheduler enabled)

- Flag overlay: `docker/zz.enable-scheduler.yml` (enables `TENANTRA_ENABLE_MODULE_SCHEDULER`)
- Scripts: `scripts/dev_up_phase7_scheduler.ps1`, `scripts/dev_up_phase7_scheduler.sh`

```powershell
./scripts/dev_up_phase7_scheduler.ps1
```

```bash
./scripts/dev_up_phase7_scheduler.sh
```

Notes:

- All scripts layer the base `docker/docker-compose.yml` with `docker/docker-compose.override.dev.yml` for dev mounts.
- Combine overlays manually if you need multiple capabilities (e.g., Observability + MailHog).
- See `docs/FEATURE_FLAGS_SMTP.md` for SMTP and feature flag details.

## All-in-One (Combined)

- Scripts: `scripts/dev_up_phase4to7_all.ps1`, `scripts/dev_up_phase4to7_all.sh`
- Includes MailHog, Observability (Prometheus+Grafana), Scheduler, and Worker.
- Optional flags:
  - PowerShell: `-ExposePorts` to bind backend/frontend to host, `-Build` to force image rebuild
  - Bash: `EXPOSE_PORTS=1` and/or `BUILD=1`

Examples:

```powershell
./scripts/dev_up_phase4to7_all.ps1 -ExposePorts -Build
```

```bash
EXPOSE_PORTS=1 BUILD=1 ./scripts/dev_up_phase4to7_all.sh
```
