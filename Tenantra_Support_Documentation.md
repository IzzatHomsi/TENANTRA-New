# Tenantra Support Documentation

This document provides a comprehensive overview of the Tenantra application for support personnel. It covers the application's core features, architecture, and configuration.

## 1. Overview

Tenantra is a multi-tenant, cloud-ready IT discovery, security, and compliance automation platform. It continuously scans, inventories, and secures complex IT environments—covering infrastructure, endpoints, networks, identities, configurations, and compliance posture—under a single intelligent dashboard.

The platform combines DevOps, SecOps, and ITIL-aligned management to provide automated visibility, compliance reporting, alerting, and remediation at scale.

### 1.1. Core Architecture

Tenantra runs as a containerized SaaS suite built on:

*   **Backend:** FastAPI (Python) with modular REST APIs.
*   **Frontend:** React/Vite dashboard.
*   **Database:** PostgreSQL.
*   **Orchestration:** Docker Compose.
*   **Optional Integrations:** Redis, Prometheus, Grafana, Loki, Vault.

Each tenant’s data is fully isolated by schema and RBAC policy. The system supports Dev, Staging, and Production environments.

### 1.2. Key Features

*   **Asset Discovery & Inventory:** Automated discovery of servers, endpoints, and network devices.
*   **Security & Compliance:** Continuous vulnerability and compliance scanning using frameworks like CIS Benchmarks, ISO 27001, and NIST 800-53.
*   **Alerting & Incident Management:** Configurable alerts and integration with SIEM and ticketing tools.
*   **Monitoring & Analytics:** Metrics exported to Prometheus and visualized in Grafana dashboards.
*   **User & Tenant Management:** Multi-tenant structure with role-based access control.
*   **Data & Billing:** Per-tenant cost tracking and automated invoicing.

## 2. Getting Started

This section covers the basic setup and initial configuration of the Tenantra application.

### 2.1. Installation

For a development environment, follow these steps:

1.  **Install dependencies:**
    ```bash
    pip install -r backend/requirements.txt
    cd frontend && npm install
    ```
2.  **Environment Variables:**
    Copy the example environment file and adjust the secrets before use:
    ```bash
    cp .env.example .env.development
    ```
3.  **Start the application stack:**
    Use the provided script to bring up the Docker containers, apply database migrations, and seed the database with initial data.
    ```bash
    ./tenantra_control_menu.sh --repo-root "$(pwd)" --no-pause
    ```
    Alternatively, you can use `make`:
    ```bash
    make up
    make migrate
    make seed
    ```
4.  **Access the application:**
    Open your web browser and navigate to `http://localhost`. You can sign in with the seeded admin credentials (the password is in the `.env.development` file).

### 2.2. Common Commands

| Command | Purpose |
| --- | --- |
| `make up` / `make down` | Start/stop the Docker stack. |
| `make migrate` | Apply database migrations. |
| `make seed` | Seed the database with default tenant and admin user. |
| `make test-all` | Run all backend and frontend tests. |
| `cd backend && uvicorn app.main:create_app --factory --reload` | Run the backend API in development mode. |
| `cd frontend && npm run dev -- --host` | Run the frontend development server. |

## 3. Core Features and Configuration

This section provides details on the core features of the Tenantra application and their configuration.

### 3.1. User and Authentication Management

User management is a core feature of Tenantra. The application provides a robust authentication system with user registration, login, and password management capabilities.

#### 3.1.1. API Endpoints

*   `POST /auth/register`: Allows a new user to register. This endpoint creates a new tenant and a new user with an 'admin' role for that tenant.
*   `POST /auth/login`: Handles user login. It accepts either form data or a JSON payload and returns a JWT access token.
*   `POST /auth/logout`: Logs out the current user by invalidating their access token.
*   `POST /auth/forgot-password`: Initiates the password reset process for a user.
*   `POST /auth/reset-password`: Completes the password reset process using a token.
*   `GET /auth/me`: Retrieves the profile of the currently authenticated user.
*   `PUT /users/me`: Allows an authenticated user to update their own profile information, such as email and password.

#### 3.1.2. Configuration

*   **Password Policy:** Password strength is validated on registration and password reset. The specific rules are defined in `backend/app/utils/password.py`.
*   **JWT Token Expiration:** The expiration time for JWT access tokens is configured in `backend/app/core/security.py`.

### 3.2. Tenant Management

Tenantra is a multi-tenant application. Administrators have the ability to manage tenants through a dedicated set of API endpoints.

#### 3.2.1. API Endpoints

*   `GET /admin/tenants`: Lists all tenants in the system. This endpoint is only accessible to administrators.
*   `POST /admin/tenants`: Creates a new tenant. This endpoint is only accessible to administrators.

#### 3.2.2. Configuration

*   **Default Tenant:** A default tenant and admin user are created when the database is seeded (`make seed`). The configuration for this is in `backend/app/seed.py`.

### 3.3. Alert Management

The alert management module allows users to define and manage alert rules for their tenants.

#### 3.3.1. API Endpoints

*   `GET /alerts`: Lists all alert rules for the current user's tenant.
*   `POST /alerts`: Creates a new alert rule for the current user's tenant.
*   `PUT /alerts/{alert_id}`: Updates an existing alert rule.
*   `DELETE /alerts/{alert_id}`: Deletes an alert rule.

#### 3.3.2. Configuration

*   Alert conditions and thresholds are configured on a per-alert basis through the API. The logic for evaluating alerts is located in the backend services related to scanning and monitoring.

### 3.4. Compliance Management

Tenantra provides features for tracking and reporting on compliance status.

#### 3.4.1. API Endpoints

*   `GET /compliance/trends`: Returns the number of passing and failing compliance scans per day for a specified time window.
*   `GET /compliance/trends/insights`: Provides a summary of compliance trends, including overall coverage, open failures, and net change.
*   `GET /compliance/results`: Lists detailed compliance scan results, with options to filter by module and status.

#### 3.4.2. Configuration

*   Compliance data is generated by scanning modules. The configuration of these modules determines what compliance checks are performed.

### 3.5. Agent Management

Agents are used to perform scans on target systems. Tenantra provides a secure way to enroll and manage agents.

#### 3.5.1. Agent Enrollment

There are two ways to enroll an agent:

1.  **Admin Enrollment:** An administrator can manually enroll an agent and receive an agent token.
2.  **Self-Enrollment:** An administrator can create an enrollment token that an agent can use to enroll itself.

#### 3.5.2. API Endpoints

*   `POST /agents/enroll`: Allows an admin to manually enroll an agent.
*   `POST /agents/enrollment-tokens`: Allows an admin to create an enrollment token.
*   `POST /agents/enroll/self`: Allows an agent to self-enroll using an enrollment token.
*   `GET /agents/config/{agent_id}`: Allows an agent to fetch its configuration from the server. This requires a valid agent token.
*   `POST /agents/results`: Allows an agent to submit scan results to the server. This requires a valid agent token.
*   `GET /admin/agents`: Lists all agents. This is an admin-only endpoint.

#### 3.5.3. Configuration

*   Agent tokens are stored securely in the database.
*   The modules that an agent is configured to run are determined by the agent's configuration, which can be managed through the API.

### 3.6. Scan Scheduling

Tenantra allows users to schedule scans to be run at regular intervals.

#### 3.6.1. API Endpoints

*   `GET /schedules`: Lists all scheduled scans for the current tenant.
*   `POST /schedules`: Creates a new scheduled scan. This requires a cron expression for the schedule.
*   `DELETE /schedules/{schedule_id}`: Deletes a scheduled scan.

#### 3.6.2. Configuration

*   Schedules are defined using cron expressions.
*   Scheduled scans are executed by a background worker process.

### 3.7. Scan Results

The results of scans can be retrieved through the API.

#### 3.7.1. API Endpoints

*   `GET /scans/files`: Retrieves file scan results for the current tenant.
*   `GET /scans/network`: Retrieves network scan results for the current tenant.
*   `GET /scans/files/export.csv`: Exports file scan results to a CSV file.
*   `GET /scans/network/export.csv`: Exports network scan results to a CSV file.

### 3.8. Cloud Discovery

Tenantra can be connected to cloud accounts to discover and inventory cloud assets.

#### 3.8.1. API Endpoints

*   `GET /cloud/accounts`: Lists cloud accounts for the current tenant.
*   `POST /cloud/accounts`: Creates a new cloud account.
*   `POST /cloud/accounts/{account_id}/sync`: Marks a cloud account as active and updates its last synced time.
*   `GET /cloud/assets`: Lists cloud assets for the current tenant.
*   `POST /cloud/assets`: Creates a new cloud asset.
*   `GET /cloud/inventory`: Returns a combined inventory of cloud accounts and assets for the current tenant.

#### 3.8.2. Configuration

*   Cloud account credentials are not stored directly in the Tenantra database. Instead, a `credential_reference` is used to securely access the credentials from a secret store like HashiCorp Vault.

## 4. Configuration

The Tenantra application is configured using environment variables. The following is a list of the key environment variables, categorized by their function.

### 4.1. Database

*   `DATABASE_URL` or `DB_URL`: The full database connection string.
*   `POSTGRES_USER`: The PostgreSQL username.
*   `POSTGRES_PASSWORD`: The PostgreSQL password.
*   `POSTGRES_PASSWORD_FILE`: Path to a file containing the PostgreSQL password.
*   `POSTGRES_DB`: The PostgreSQL database name.
*   `POSTGRES_HOST`: The PostgreSQL host.
*   `POSTGRES_PORT`: The PostgreSQL port.

### 4.2. Security

*   `TENANTRA_ENC_KEY`: A 32-byte secret key used for data encryption.
*   `JWT_SECRET`: The secret key used for signing JWTs.
*   `JWT_ALGORITHM`: The algorithm used for signing JWTs (default: `HS256`).
*   `ACCESS_TOKEN_EXPIRE_MINUTES`: The expiration time for access tokens in minutes (default: `60`).
*   `REFRESH_TOKEN_EXPIRE_DAYS`: The expiration time for refresh tokens in days (default: `14`).
*   `SEC_HSTS`: The value for the `Strict-Transport-Security` header.
*   `SEC_FRAME_OPTIONS`: The value for the `X-Frame-Options` header (default: `DENY`).
*   `SEC_CONTENT_TYPE_OPTIONS`: The value for the `X-Content-Type-Options` header (default: `nosniff`).
*   `SEC_REFERRER_POLICY`: The value for the `Referrer-Policy` header (default: `no-referrer`).

### 4.3. Email (SMTP)

*   `SMTP_HOST`: The SMTP server host.
*   `SMTP_PORT`: The SMTP server port (default: `587`).
*   `SMTP_USER`: The SMTP username.
*   `SMTP_PASS`: The SMTP password.
*   `SMTP_FROM`: The "From" address for outgoing emails.
*   `SMTP_TLS`: Whether to use TLS for SMTP (default: `true`).

### 4.4. Celery (Background Tasks)

*   `CELERY_BROKER_URL`: The URL for the Celery message broker (e.g., Redis).
*   `CELERY_RESULT_BACKEND`: The URL for the Celery result backend.
*   `CELERY_DEFAULT_QUEUE`: The default Celery queue name (default: `tenantra`).
*   `CELERY_RESULT_EXPIRES`: The expiration time for Celery results in seconds (default: `600`).

### 4.5. Logging

*   `LOG_LEVEL`: The logging level (e.g., `INFO`, `DEBUG`, `WARNING`).
*   `LOG_DIR`: The directory to store log files.
*   `TENANTRA_LOG_TO_FILE`: Whether to log to a file (default: `0`).

### 4.6. Seeding

*   `SEED_TENANT_NAME`: The name of the default tenant to create during seeding.
*   `SEED_TENANT_SLUG`: The slug of the default tenant.
*   `SEED_ADMIN_USERNAME`: The username of the default admin user.
*   `SEED_ADMIN_PASSWORD`: The password of the default admin user.
*   `SEED_ADMIN_EMAIL`: The email of the default admin user.
*   `SEED_ADMIN_ROLE`: The role of the default admin user.

### 4.7. Other

*   `APP_VERSION`: The version of the application.
*   `TENANTRA_API`: The base URL for the backend API.
*   `TENANTRA_NGINX`: The base URL for the Nginx server.
*   `TENANTRA_GRAFANA`: The base URL for the Grafana server.
*   `GRAFANA_USER`: The Grafana admin username.
*   `GRAFANA_PASS`: The Grafana admin password.
*   `TENANTRA_AUTO_IMPORT_MODULES` or `TENANTRA_IMPORT_MODULES`: Enable or disable automatic module importing on startup.
*   `TENANTRA_MODULES_CSV`: Path to the CSV file containing module definitions.
