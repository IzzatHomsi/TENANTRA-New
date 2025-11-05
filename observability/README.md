Observability assets for Tenantra

- Grafana dashboards: `observability/grafana/dashboards/`
- Prometheus alerts: `docker/prometheus/rules/alerts.yml`

Exporting dashboards
- Source dashboards live under `docker/grafana-provisioning/dashboards/`.
- To sync into this folder, run `tools/export_dashboards.ps1`.

