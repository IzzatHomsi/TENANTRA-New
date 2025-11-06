# Tenantra - The Unified IT Discovery & Compliance Platform

![Build Status](https://img.shields.io/github/actions/workflow/status/IzzatHomsi/TENANTRA-New/backend-ci.yml?branch=main&style=for-the-badge)
![Code Coverage](https://img.shields.io/codecov/c/github/IzzatHomsi/TENANTRA-New?style=for-the-badge)
![License](https://img.shields.io/github/license/IzzatHomsi/TENANTRA-New?style=for-the-badge)

Tenantra is a multi-tenant, cloud-ready IT discovery, security, and compliance automation platform. It continuously scans, inventories, and secures complex IT environments—covering infrastructure, endpoints, networks, identities, configurations, and compliance posture—under a single intelligent dashboard.

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Installation and Setup](#installation-and-setup)
- [Running the Application](#running-the-application)
- [Running Tests](#running-tests)
- [CI/CD](#cicd)
- [Contributing](#contributing)
- [License](#license)
- [Contact & Support](#contact--support)

## Features

<details>
<summary>Core Features</summary>

### 1. Asset Discovery & Inventory
- Automated discovery of servers, endpoints, and network devices
- OS, role, and application fingerprinting
- Cloud/hybrid connectors (AWS EC2, Azure VMs, GCP instances)
- Agent-based and agentless modes

### 2. Security & Compliance
- Continuous vulnerability and compliance scanning
- Built-in frameworks: CIS Benchmarks, ISO 27001, NIST 800-53
- Real-time compliance scoring
- Data encryption and key rotation dashboards

### 3. Alerting & Incident Management
- Configurable thresholds and rules
- Branded HTML notifications (email/SMS/API)
- Alert history, acknowledgment, and export
- Integration hooks for SIEM and ticketing tools

### 4. Monitoring & Analytics
- Metrics exported to Prometheus
- Visualization in Grafana dashboards
- Compliance trends and SLA metrics over time

### 5. User & Tenant Management
- Multi-tenant structure with isolated schemas
- Role-based dashboard views and permissions
- Admin tools for tenant creation, feature enable/disable, and billing visibility

### 6. Data & Billing
- Per-tenant cost tracking (scan count, storage use, features)
- Automated invoice templates (CSV, PDF)
- MSP dashboards for usage analytics

### 7. DevSecOps & Automation
- GitHub Actions CI/CD pipelines
- Dockerized deployment (tenantra_backend, tenantra_frontend, tenantra_db, tenantra_adminer)
- Automated migration + seed scripts (run_migrate.sh, db_seed.py)
- Validation suite & health checks via PowerShell and curl scripts

### Differentiators
- True multi-tenant isolation with per-client encryption and audit trail.
- Modular scanning engine covering system, network, identity, and compliance layers.
- Self-contained DevOps stack deployable on-prem or cloud in minutes.
- Compliance-as-a-Service model enabling MSPs to resell scanning and reporting.
- Unified UI/UX combining dashboards, alerting, billing, and remediation.

### Built-in Intelligence
- Machine-learning-ready telemetry pipelines.
- Behavior analytics (UEBA) for anomaly detection.
- Smart remediation recommendations linked to each compliance rule.

### Deployment Options
- On-Premises, Private Cloud, or Hybrid
- Runs on Windows Server 2022, Linux (Ubuntu/Debian), or container platforms.
- HTTPS enabled via self-signed or Let’s Encrypt certificates.
- Integrates with FortiGate, TP-Link, and other firewalls for network discovery.
</details>

## Architecture

Tenantra is built on a modern, containerized architecture:

- **Backend:** Python/FastAPI with modular REST APIs.
- **Frontend:** React/Vite with a Tailwind CSS theme.
- **Database:** PostgreSQL with SQLAlchemy and Alembic for migrations.
- **Orchestration:** Docker Compose for easy deployment and scaling.
- **Observability:** Optional integrations with Prometheus, Grafana, Loki, and Vault.

## Installation and Setup

To set up the development environment, you will need:

- Python 3.11+
- Node.js 18+
- Docker and Docker Compose

**1. Clone the repository:**
```bash
git clone git@github.com:IzzatHomsi/TENANTRA-New.git
cd TENANTRA-New
```

**2. Backend Setup:**
```bash
cd backend
pip install -r requirements.txt
```

**3. Frontend Setup:**
```bash
cd frontend
npm install
```

## Running the Application

### With Docker (Recommended)

The easiest way to run the full application stack is with Docker Compose:

```bash
make up       # Start the application stack
make migrate  # Apply database migrations
make seed     # Seed the database with initial data
```

The frontend will be available at `http://localhost:5173` and the backend at `http://localhost:5000`.

### Local Development

**Backend:**
```bash
python backend/dev_server.py
```

**Frontend:**
```bash
npm run dev
```

## Running Tests

**Backend:**
```bash
pytest backend/
```

**Frontend:**
```bash
npm test
```

## CI/CD

This project uses GitHub Actions for CI/CD. The main workflows are:

- `backend-ci.yml`: Runs linting, type checking, security scans, and tests for the backend.
- `frontend-ci.yml`: Installs dependencies, runs ESLint, and builds the frontend.
- `e2e-staging.yml`: Runs end-to-end tests against a staging environment.

For more details, see the workflow files in `.github/workflows`.

## Contributing

We welcome contributions! Please see our [CONTRIBUTING.md](CONTRIBUTING.md) file for detailed guidelines on how to contribute to the project, including our code of conduct, pull request process, and coding standards.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact & Support

- **Issues:** If you find a bug or have a feature request, please [open an issue](https://github.com/IzzatHomsi/TENANTRA-New/issues).
- **Contact:** For other inquiries, you can reach out to the project maintainers.