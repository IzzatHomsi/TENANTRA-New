# Tenantra – Master Brain Technical Overview

# 1. Overview
Tenantra is a multi-tenant, cloud-ready IT discovery, security, and compliance automation platform. It continuously scans, inventories, and secures complex IT environments—covering infrastructure, endpoints, networks, identities, configurations, and compliance posture—under a single intelligent dashboard.

The platform combines DevOps, SecOps, and ITIL-aligned management to provide automated visibility, compliance reporting, alerting, and remediation at scale.

## 2. Architecture
Tenantra is built on a modern, containerized architecture:

- **Backend:** Python/FastAPI with modular REST APIs.
- **Frontend:** React/Vite with a Tailwind CSS theme.
- **Database:** PostgreSQL with SQLAlchemy and Alembic for migrations.
- **Orchestration:** Docker Compose for easy deployment and scaling.
- **Observability:** Optional integrations with Prometheus, Grafana, Loki, and Vault.

Each tenant’s data is fully isolated by schema and RBAC policy. The system supports Dev, Staging, and Production environments.

### 2.1 Security Foundation
- **Encryption:** TLS 1.3 for data-in-transit, AES-256 for data-at-rest.
- **Key Management:** Integrated with HashiCorp Vault / Azure Key Vault.
- **Authentication:** JWT-based sessions with bcrypt-hashed passwords.
- **RBAC:** Role-based access for admin, standard, and MSP tiers.
- **Audit Logs & Compliance Trails:** Immutable and exportable per tenant.

### 2.2 Features
- **Asset Discovery & Inventory:** Automated discovery of servers, endpoints, and network devices.
- **Security & Compliance:** Continuous vulnerability and compliance scanning with built-in frameworks like CIS Benchmarks, ISO 27001, and NIST 800-53.
- **Alerting & Incident Management:** Configurable thresholds and rules with branded HTML notifications.
- **Monitoring & Analytics:** Metrics exported to Prometheus and visualized in Grafana dashboards.
- **User & Tenant Management:** Multi-tenant structure with isolated schemas and role-based dashboard views.
- **Data & Billing:** Per-tenant cost tracking and automated invoice templates.
- **DevSecOps & Automation:** GitHub Actions CI/CD pipelines and Dockerized deployment.

## 3. Backend – API & Logic

### 3.1 Backend Structure
The backend code is located in the `backend/` directory.
- **`app/`**: Contains the core application source code.
    - **`main.py`**: The main application entrypoint with the FastAPI app factory (`create_app`). It initializes middleware, routers, and background workers.
    - **`api/`**: (Implicitly structured via `routes/`) Contains the API endpoint definitions.
    - **`core/`**: Contains core logic for authentication (`auth.py`), security (`security.py`), and multi-tenancy (`tenants.py`).
    - **`models/`**: Defines the SQLAlchemy database models (e.g., `user.py`, `tenant.py`).
    - **`schemas/`**: Defines the Pydantic schemas used for API request/response validation and serialization.
    - **`services/`**: Contains business logic decoupled from the API layer.
    - **`routes/`**: Each file defines a `router` for a specific feature (e.g., `users_admin.py`, `alerts.py`). These are automatically discovered and included in `main.py`.
    - **`worker/`**: Contains the logic for the background workers.
- **`alembic/`**: Contains database migration scripts.
- **`scripts/`**: Contains helper scripts, such as `db_seed.py`.
- **`tests/`**: Contains `pytest` tests for the backend.

### 3.2 Key Modules and Their Responsibilities
- **Auth & Identity (`app/core/auth.py`, `app/core/security.py`):** Handles JWT creation, decoding, password hashing, and provides FastAPI dependencies for authenticating users and checking roles.
- **User Management (`app/routes/users_admin.py`, `app/routes/users_me.py`):** Exposes CRUD endpoints for managing users (admin) and allows users to manage their own profiles (me). Self-service routes reuse `get_current_user` so any token revoked via logout or password reset is honored uniformly. Touches the `User` model.
- **Tenants & Plans (`app/routes/tenants_admin.py`):** Provides endpoints for managing tenants. Touches the `Tenant` model.
- **Scan Scheduling & Execution (`app/routes/schedules.py`, `app/routes/module_runs.py`, `app/worker/module_scheduler.py`):** Manages the scheduling of scan modules and tracks their execution status. The `ModuleSchedulerWorker` is responsible for periodically checking for and dispatching scheduled jobs.
- **Alerts & Notifications (`app/routes/alerts.py`, `app/routes/notifications.py`, `app/worker/notifications_worker.py`):** Manages alert definitions and notification delivery. The `NotificationsWorker` processes a queue to send out emails or other notifications asynchronously.
- **Audit Logging (`app/routes/audit_logs.py`):** Provides endpoints to query the immutable audit trail of actions performed in the system.

### 3.3 REST / API Endpoints
The backend exposes a wide range of RESTful endpoints. Most are prefixed with `/api`. Here is a summary of the core ones:

| Method | Path | Purpose | Auth Required |
| --- | --- | --- | --- |
| POST | `/auth/login` | Authenticate and receive a JWT. | No |
| GET | `/users/me` | Get the current user's profile. | Yes |
| GET | `/admin/users` | Get a list of all users. | Yes (Admin) |
| POST | `/admin/users` | Create a new user. | Yes (Admin) |
| GET | `/admin/tenants` | Get a list of all tenants. | Yes (Admin) |
| GET | `/modules` | Get the list of available scan modules. | Yes |
| POST | `/schedules` | Create a new scan schedule. | Yes |
| GET | `/alerts` | Get a list of triggered alerts. | Yes |
| GET | `/audit-logs` | Get a list of audit log entries. | Yes (Admin) |

### 3.4 Configuration & Environment
- **Environment Variables:** Configuration is handled exclusively through environment variables. There is no central config file.
- **`.env` files:** The `docker-compose.yml` file loads environment variables from `.env.<TENANTRA_ENV>` (e.g., `.env.development`).
- **Critical Settings:**
    - `POSTGRES_USER`, `POSTGRES_DB`, `POSTGRES_PASSWORD_FILE`: Database connection details.
    - `SECRET_KEY`, `ALGORITHM`: Used for signing JWTs.
    - `CORS_ORIGINS`: A comma-separated list of allowed origins for CORS.
    - `TENANTRA_ENABLE_..._WORKER`: Feature flags to enable or disable background workers.
    - `TENANTRA_SCHEDULER_INTERVAL`: Sets the poll interval for the module scheduler.

### 3.5 Core Module: Security, Authentication, and Authorization
This module forms the security foundation of the Tenantra backend. It is responsible for password management, JWT-based access tokens, refresh token lifecycle, data encryption, and route-level protection.

#### 3.5.1 File Breakdown
- **`app/core/security.py`**: Low-level utilities for password hashing (`passlib`) and JWT lifecycle (`python-jose`).
- **`app/core/auth.py`**: High-level FastAPI dependencies that integrate the security utilities into the API routes for protection.
- **`app/core/tokens.py`**: Logic for issuing, rotating, and revoking refresh tokens, which are stored in the database.
- **`app/core/crypto.py`**: Symmetric encryption functionality (AES-GCM) for protecting data at rest.
- **`app/core/secrets.py`**: Secure access patterns for retrieving secrets (like JWT key) from environment variables with caching.
- **`app/services/token_blocklist.py`**: Database-backed helpers for revoking individual JWTs (logout) or whole issuance ranges (password reset). `get_current_user` consults this service so revoked tokens fail authorization immediately.

#### 3.5.2 Detailed Logic and Functions

---
##### **`app/core/secrets.py`**
This file provides centralized access to application secrets, primarily the JWT secret key and the data encryption key. It ensures that secrets are loaded only once and cached for performance, while providing secure fallbacks.

- **`get_jwt_secret() -> str`**
    - **Purpose:** To securely retrieve the JWT secret key used for signing access tokens.
    - **Logic:**
        1. It first checks if the secret is already cached in the global `_JWT_SECRET` variable. If so, it returns the cached value immediately.
        2. If not cached, it attempts to read the `JWT_SECRET_KEY` environment variable.
        3. If the environment variable is not set, it generates a new, cryptographically secure URL-safe string using `secrets.token_urlsafe(32)` as a fallback for development or ephemeral environments.
        4. The retrieved or generated secret is then stored in the `_JWT_SECRET` global variable for subsequent calls.
    - **Returns:** The JWT secret key as a string.

- **`get_enc_key() -> bytes`**
    - **Purpose:** To retrieve the key used for symmetric data encryption and decryption.
    - **Logic:**
        1. Checks for a cached key in the global `_ENC_KEY_CACHE` variable.
        2. If not cached, it attempts to read the `TENANTRA_ENC_KEY` environment variable.
        3. If `TENANTRA_ENC_KEY` is not set, it falls back to using the `JWT_SECRET` environment variable.
        4. If neither is set, it uses a hardcoded development key: `"tenantra-dev-enc-key-change-me"`. **This is a security risk in production if not overridden.**
        5. It ensures the final key is encoded into bytes, caches it in `_ENC_KEY_CACHE`, and returns it.
    - **Returns:** The encryption key as a bytes object.

---
##### **`app/core/security.py`**
This file contains the core cryptographic operations for handling passwords and JWTs.

- **Constants and Configuration:**
    - `pwd_context`: An instance of `passlib.context.CryptContext` configured to use `bcrypt` for password hashing. It automatically handles salt generation and verification.
    - `SECRET_KEY`: Loaded by calling `load_jwt_secret()`.
    - `ALGORITHM`: The algorithm used for JWT signing, read from the `JWT_ALGORITHM` environment variable, defaulting to `"HS256"`.
    - `ACCESS_TOKEN_EXPIRE_MINUTES`: The default lifetime for an access token in minutes, read from the environment variable of the same name, defaulting to `60`.

- **`load_jwt_secret() -> str`**
    - **Purpose:** To safely load the JWT secret, ensuring a default value is not used in production.
    - **Logic:**
        1. Reads the `JWT_SECRET` environment variable.
        2. If the secret is empty or matches the placeholder `"CHANGE_ME_IN_.ENV"`, it proceeds to the next checks.
        3. If the environment indicates a `pytest` run or if `TENANTRA_TEST_BOOTSTRAP` is enabled, it returns a hardcoded test secret (`"tenantra-test-secret"`). This prevents tests from failing due to a missing secret.
        4. If none of the above conditions are met (i.e., in a production-like environment), it raises a `RuntimeError` to force the administrator to set a proper secret.
    - **Returns:** The JWT secret key as a string.
    - **Throws:** `RuntimeError` if a secure secret is not configured.

- **`verify_password(plain_password: str, hashed_password: str) -> bool`**
    - **Purpose:** To securely compare a plaintext password against a hashed one.
    - **Logic:** Delegates the comparison to `pwd_context.verify()`. This function handles the complexities of extracting the salt from the hash and re-hashing the plaintext password to perform a constant-time comparison.
    - **Returns:** `True` if the passwords match, `False` otherwise.

- **`get_password_hash(password: str) -> str`**
    - **Purpose:** To create a new hash for a given plaintext password.
    - **Logic:** Delegates the hashing to `pwd_context.hash()`. This automatically generates a new salt for each password.
    - **Returns:** The bcrypt hash of the password as a string.

- **`create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str`**
    - **Purpose:** To generate a new JWT access token.
    - **Logic:**
        1. Takes a dictionary `data` to be encoded as the token's payload.
        2. Calculates the expiration time (`exp` claim) by adding the `expires_delta` (if provided) or the default `ACCESS_TOKEN_EXPIRE_MINUTES` to the current UTC time.
        3. Encodes the payload dictionary into a JWT string using `jose.jwt.encode()`, signing it with the global `SECRET_KEY` and `ALGORITHM`.
        4. Stamps both `exp` and `iat` with timezone-aware UTC timestamps so comparisons inside the token blocklist remain accurate even when host clocks drift.
    - **Returns:** The encoded JWT as a string.

- **`decode_access_token(token: str) -> Optional[dict]`**
    - **Purpose:** To validate and decode a JWT access token.
    - **Logic:**
        1. Attempts to decode the token string using `jose.jwt.decode()`, providing the `SECRET_KEY` and `ALGORITHM` for verification.
        2. The library automatically checks the token's signature and expiration time.
        3. If decoding or validation fails for any reason (e.g., invalid signature, expired token, malformed token), it catches the `JWTError` and returns `None`.
    - **Returns:** The token's payload as a dictionary if valid, otherwise `None`.

---
##### **`app/core/auth.py`**
This file acts as the bridge between the low-level security functions and the FastAPI framework, providing dependencies that can be used to protect API routes.

- **`oauth2_scheme`**: An instance of `OAuth2PasswordBearer` that tells FastAPI where the token-issuing endpoint is (`/auth/login`). It provides a simple dependency to extract the bearer token from the `Authorization` header.

- **`_resolve_user_from_token(token: str, db: Session) -> User`**
    - **Purpose:** A private helper function to resolve a user object from a JWT string.
    - **Logic:**
        1. Decodes the token using `decode_access_token()`. If decoding fails, it raises a 401 Unauthorized HTTP exception.
        2. Extracts the `sub` (subject) claim from the payload, which should contain the user's ID.
        3. Validates that the `sub` is an integer. If not, raises a 401 error.
        4. Queries the database for a `User` with that ID.
        5. If no user is found, raises a 404 Not Found error.
    - **Returns:** The SQLAlchemy `User` object if the token is valid and the user exists.
    - **Throws:** `HTTPException` for various failure cases.

- **`get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User`**
    - **Purpose:** A FastAPI dependency to get the currently authenticated user.
    - **Logic:** This is the primary dependency used to protect routes. It depends on `oauth2_scheme` to get the token and `get_db` to get a database session, then passes them to `_resolve_user_from_token`.
    - **Returns:** The authenticated `User` object. Any exceptions from the helper function will propagate up and be handled by FastAPI.

- **`get_admin_user(...) -> User`**
    - **Purpose:** A FastAPI dependency that ensures the current user is an administrator.
    - **Logic:**
        1. Manually extracts the `Authorization` header.
        2. Resolves the user from the token using `_resolve_user_from_token`.
        3. Checks the user's `role` attribute (case-insensitively) against a predefined set of admin role names (`_DEF_ADMIN_ROLES`).
        4. If the user's role is not in the set, it raises a 403 Forbidden HTTP exception.
    - **Returns:** The authenticated admin `User` object.

- **`get_settings_user(...) -> User`**
    - **Purpose:** A FastAPI dependency that ensures the current user has permissions to read settings (a broader set of roles than just admin).
    - **Logic:** Similar to `get_admin_user`, but checks the user's role against a larger set of roles (`_SETTINGS_READ_ROLES`), which includes auditors and read-only admins.
    - **Returns:** The authenticated `User` object with settings-read permissions.

---
##### **`app/core/tokens.py`**
This file manages the lifecycle of refresh tokens, which are long-lived tokens used to obtain new access tokens without requiring the user to log in again.

- **Configuration:**
    - `REFRESH_EXPIRE_DAYS`: The lifetime of a refresh token in days, defaulting to 14.
    - `REFRESH_IN_COOKIE`: A boolean flag to determine if refresh tokens should be handled in cookies (not fully implemented in this file, but the config is present).

- **`_hash_token(raw: str) -> str`**
    - **Purpose:** To securely hash the raw refresh token before storing it in the database. This prevents a database leak from exposing the raw tokens.
    - **Logic:** Uses `hashlib.sha256` to create a one-way hash of the token.

- **`issue_refresh_token(db: Session, user: User, ...) -> str`**
    - **Purpose:** To create and store a new refresh token for a user.
    - **Logic:**
        1. Generates a new, long, random token string using `secrets.token_urlsafe(48)`.
        2. Hashes the raw token using `_hash_token()`.
        3. Creates a new `RefreshToken` SQLAlchemy object, linking it to the `user_id` and storing the hash, expiration date, and metadata (user agent, IP address).
        4. Commits the new token to the database.
    - **Returns:** The **raw, unhashed** token string, which is sent to the client.

- **`rotate_refresh_token(db: Session, raw: str) -> Tuple[User, str]`**
    - **Purpose:** To exchange a valid refresh token for a new access token and a new refresh token (a security best practice).
    - **Logic:**
        1. Hashes the provided raw token and finds the corresponding `RefreshToken` in the database.
        2. Validates that the token exists, has not been revoked, and has not expired. If any check fails, raises a 401 Unauthorized error.
        3. Retrieves the associated `User`.
        4. Marks the used refresh token as revoked (`revoked_at = now`).
        5. Issues a brand new refresh token for the same user using `issue_refresh_token()`.
        6. Commits the changes to the database.
    - **Returns:** A tuple containing the `User` object and the new raw refresh token.

- **`revoke_refresh_token(db: Session, raw: str) -> None`**
    - **Purpose:** To invalidate a specific refresh token (e.g., on logout).
    - **Logic:** Finds the token by its hash and sets its `revoked_at` timestamp.

- **`revoke_all_for_user(db: Session, user_id: int) -> int`**
    - **Purpose:** To invalidate all active refresh tokens for a specific user (e.g., after a password change).
    - **Logic:** Queries for all non-revoked tokens belonging to the `user_id` and sets their `revoked_at` timestamp.
    - **Returns:** The count of tokens that were revoked.

---
##### **`app/core/crypto.py`**
This file provides generic data encryption utilities using a modern, authenticated encryption algorithm.

- **`encrypt_data(raw: str, key: bytes) -> str`**
    - **Purpose:** To encrypt a string using AES-GCM.
    - **Logic:**
        1. Derives a 256-bit encryption key from the input `key` by hashing it with SHA-256. This ensures the key is always the correct length.
        2. Generates a random 12-byte `nonce` (number used once), which is required for AES-GCM.
        3. Initializes `AESGCM` with the derived key.
        4. Encrypts the data, associating it with the nonce.
        5. Prepends the nonce to the ciphertext and base64-encodes the result. This is crucial because the same nonce is required for decryption.
    - **Returns:** A base64-encoded string containing the nonce and the ciphertext.

- **`decrypt_data(enc: str, key: bytes) -> str`**
    - **Purpose:** To decrypt a string that was encrypted with `encrypt_data`.
    - **Logic:**
        1. Base64-decodes the input string.
        2. Splits the decoded data into the 12-byte nonce and the ciphertext.
        3. Derives the decryption key from the input `key` using the same SHA-256 hashing process.
        4. Initializes `AESGCM` with the derived key.
        5. Decrypts the ciphertext using the extracted nonce. AES-GCM automatically verifies the integrity of the data. If it was tampered with, the decryption will fail.
    - **Returns:** The original plaintext string.
    - **Throws:** A `cryptography.exceptions.InvalidTag` error if decryption fails (due to a wrong key or tampered data).

### 3.6 Core Module: Tenancy, Permissions, and RBAC
This module handles multi-tenancy, defines user roles, and provides helpers for controlling access to resources based on tenant scope and role.

#### 3.6.1 File Breakdown
- **`app/core/tenants.py`**: Contains logic for resolving a user's tenant and managing tenant-specific filesystem paths.
- **`app/core/rbac.py`**: Provides generic, normalized helpers for checking user roles.
- **`app/core/permissions.py`**: Defines FastAPI dependencies for enforcing role-based and tenant-scoped access control on API routes.

#### 3.6.2 Detailed Logic and Functions

---
##### **`app/core/tenants.py`**
This file implements the core logic for isolating tenant data, both in the database and on the filesystem.

- **`TenantScope(id: int, slug: str)`**
    - **Purpose:** A simple `dataclass` to hold a user's resolved tenant ID and slug. This provides a clean, typed object to pass around the application.

- **`_allowed_root_templates() -> Sequence[str]`**
    - **Purpose:** To get the configured base paths for tenant-specific filesystem storage.
    - **Logic:**
        1. Reads the `TENANTRA_ALLOWED_EXPORT_ROOTS` environment variable.
        2. If the variable is not set, it returns a default tuple: `("/app/data/tenants/{tenant}",)`.
        3. If the variable is set, it splits the comma-separated string into a sequence of path templates.
    - **Returns:** A sequence of path templates.

- **`roots_for_tenant(tenant: str | int) -> list[str]`**
    - **Purpose:** To generate the absolute filesystem paths for a given tenant.
    - **Logic:**
        1. Takes a tenant ID or slug.
        2. Iterates through the templates provided by `_allowed_root_templates()`.
        3. For each template, it replaces the `{tenant}` placeholder with the tenant's slug.
        4. It resolves the absolute path of the generated string.
    - **Returns:** A list of absolute paths for the tenant's data directories.

- **`ensure_tenant_roots(tenant: str | int) -> list[str]`**
    - **Purpose:** To generate tenant-specific paths and ensure the directories exist on the filesystem.
    - **Logic:**
        1. Calls `roots_for_tenant()` to get the list of paths.
        2. For each path, it calls `os.makedirs(p, exist_ok=True)` to create the directory if it doesn't already exist.
    - **Returns:** The list of created/verified absolute paths.

- **`get_user_tenant_scope(user: User, db: Optional[Session] = None) -> Optional[TenantScope]`**
    - **Purpose:** To resolve the tenant scope for a given user. This is a critical function for enforcing multi-tenancy.
    - **Logic:**
        1. Checks if the `user` object exists and has a `tenant_id`. If not, returns `None`.
        2. If a database session (`db`) is provided, it queries the `Tenant` table to find the tenant matching the `user.tenant_id`. It uses the tenant's `slug` if available, otherwise defaults to a slug like `"tenant123"`.
        3. If no database session is provided, it falls back to creating a generic slug from the `tenant_id` directly.
    - **Returns:** A `TenantScope` object containing the user's tenant ID and slug, or `None` if the user has no tenant.

---
##### **`app/core/rbac.py`**
This file provides generic, reusable functions for role-based access control logic that are not tied to the FastAPI framework.

- **`_norm_roles(values: Iterable[str]) -> set`**
    - **Purpose:** A private helper to normalize a list of role strings for consistent comparison.
    - **Logic:**
        1. Iterates through the input `values`.
        2. For each value, it converts it to a string, strips whitespace, converts to lowercase, and replaces spaces with underscores.
    - **Returns:** A set of normalized role strings.

- **`has_any_role(user_roles: Iterable[str], allowed: Iterable[str]) -> bool`**
    - **Purpose:** To check if a user has at least one of the required roles.
    - **Logic:**
        1. Normalizes both the user's roles and the allowed roles using `_norm_roles()`.
        2. Performs a set intersection (`&`) between the two sets.
        3. Returns `True` if the intersection is not empty (i.e., there is at least one match).
    - **Returns:** `True` if the user has a permitted role, `False` otherwise.

- **`require_any_role(user_roles: Iterable[str], allowed: Iterable[str]) -> None`**
    - **Purpose:** To enforce that a user has one of the allowed roles, raising a `ValueError` if they do not.
    - **Logic:** Calls `has_any_role()` and raises a `ValueError` with a descriptive message if the check fails. This is intended for use in business logic layers where an `HTTPException` might not be appropriate.
    - **Throws:** `ValueError` if the role check fails.

---
##### **`app/core/permissions.py`**
This file defines FastAPI dependencies that use the RBAC and tenancy logic to protect API endpoints.

- **Role Constants:**
    - `ROLE_ADMIN`: `"admin"`
    - `ROLE_STANDARD`: `"standard_user"`

- **`require_roles(*roles: str) -> Callable[[User], User]`**
    - **Purpose:** A flexible dependency factory for creating route protectors that require one or more specific roles.
    - **Logic:**
        1. It's a factory that takes a variable number of role strings (`*roles`).
        2. It returns a new function (`_dep`) which is the actual FastAPI dependency.
        3. The `_dep` function depends on `get_current_user` to get the authenticated user.
        4. It checks if the `current_user.role` is present in the `roles` tuple.
        5. If the role does not match, it raises a 403 Forbidden `HTTPException`.
    - **Returns:** A FastAPI dependency function.
    - **Usage:** `app.get("/path", dependencies=[Depends(require_roles("admin", "super_admin"))])`

- **`require_admin(current_user: User = Depends(get_current_user)) -> User`**
    - **Purpose:** A simple, specific dependency to protect routes that require the "admin" role.
    - **Logic:** A specialized version of `require_roles`. It directly checks if `current_user.role` is not equal to `"admin"` and raises a 403 `HTTPException` if the check fails.
    - **Returns:** The `current_user` object if the user is an admin.

- **`require_tenant_scope(user_id: int, *, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> None`**
    - **Purpose:** A dependency to enforce tenant boundaries. It ensures that an admin from one tenant cannot act on a user from another tenant.
    - **Logic:**
        1. Takes a `user_id` (typically from the URL path) as an argument.
        2. Fetches the user being acted upon (`u`) from the database using this `user_id`.
        3. It checks if the `current_user` (the one making the request) is an admin and if their `tenant_id` does not match the `tenant_id` of the user being acted upon.
        4. If there is a tenant mismatch, it raises a 403 Forbidden `HTTPException`.
    - **Note:** This implementation only applies the check for admins. A standard user's ability to act on another user would be controlled by other logic.

### 3.7 Core Module: Utilities (Audit, Rate Limit, ZIP)
This section covers various utility modules in `app/core` that provide cross-cutting concerns like audit logging, rate limiting, and secure file archiving.

#### 3.7.1 File Breakdown
- **`app/core/audit.py`**: A simple, structured logger for creating an immutable audit trail.
- **`app/core/rate_limit.py`**: An in-memory, sliding-window rate limiter to prevent abuse of expensive endpoints.
- **`app/core/zipper.py`**: Secure utilities for creating ZIP archives from tenant-scoped file paths.

#### 3.7.2 Detailed Logic and Functions

---
##### **`app/core/audit.py`**
This file provides a single function for emitting structured JSON audit logs.

- **`log_audit(event: str, actor_id: str, actor_name: str, tenant: str, **extra: Any) -> None`**
    - **Purpose:** To create a standardized, machine-readable audit log entry.
    - **Logic:**
        1. Retrieves a specific logger instance named `"tenantra.audit"`.
        2. Constructs a dictionary payload containing:
            - `ts`: An ISO 8601 timestamp in UTC.
            - `event`: The name of the event being logged (e.g., `"user_login"`).
            - `actor_id`, `actor_name`: The ID and name of the user or system performing the action.
            - `tenant`: The tenant context for the event.
            - Any additional keyword arguments passed to the function are included for extra context.
        3. Serializes the dictionary to a compact JSON string.
        4. Logs the JSON string at the `INFO` level.
        5. Includes a `try...except` block to catch and log any JSON serialization errors, ensuring the logger itself does not crash the application.

---
##### **`app/core/rate_limit.py`**
This file implements a simple, in-memory rate limiter. It is not suitable for a distributed environment with multiple backend instances but works for a single-node setup.

- **`_window_max()`**
    - **Purpose:** A private helper to load the rate limit configuration from environment variables.
    - **Logic:** Reads `TENANTRA_EXPORT_RATE_WINDOW_SECONDS` (default 60) and `TENANTRA_EXPORT_RATE_MAX` (default 10).
    - **Returns:** A tuple of `(window_seconds, max_requests)`.

- **`rate_limit_export(user) -> None`**
    - **Purpose:** A function (likely used as a FastAPI dependency) to enforce a rate limit on a specific user.
    - **Logic:**
        1. It uses a global dictionary `_BUCKETS` to store timestamps of recent requests for each user ID. A `threading.Lock` (`_LOCK`) is used to make access to this dictionary thread-safe.
        2. It identifies the user by their `id` attribute. If the user object has no ID, it falls back to a single shared bucket named `"anon"`.
        3. It retrieves the request queue (`deque`) for the user's ID.
        4. It removes any timestamps from the left of the queue that are older than the configured `window`. This is the "sliding window" mechanism.
        5. It checks if the number of remaining timestamps in the queue is greater than or equal to the `maxreq` limit. If it is, a 429 Too Many Requests `HTTPException` is raised.
        6. If the user is within the limit, it appends the current timestamp to the right of the queue.
    - **Throws:** `HTTPException` if the rate limit is exceeded.

---
##### **`app/core/zipper.py`**
This file provides functions to securely create ZIP archives from files within one or more allowed base directories, preventing directory traversal attacks.

- **`_is_within_base(base: str, target: str) -> bool`**
    - **Purpose:** A security-critical helper to check if a `target` path is safely located within a `base` directory.
    - **Logic:** It compares the `os.path.realpath` of both paths to resolve any symbolic links and determine if the `target` is truly a descendant of the `base`.

- **`_safe_add_file(zf: zipfile.ZipFile, base_dir: str, abs_path: str, ...)`**
    - **Purpose:** A helper to safely add a single file to a ZIP archive.
    - **Logic:** It first uses `_is_within_base()` to ensure the file is in the allowed directory. If the check passes, it adds the file to the `ZipFile` object (`zf`), creating a relative path for the archive entry.

- **`sanitize_and_validate_paths(paths: Iterable[str], base_root: str) -> tuple[...]`**
    - **Purpose:** To validate a list of user-provided file paths against a single allowed `base_root`.
    - **Logic:**
        1. Iterates through the user-provided `paths`.
        2. For each path, it resolves the real, absolute path.
        3. It performs a series of checks:
            - Is the path within `base_root`?
            - Does the path exist?
            - Has the path already been seen (to avoid duplicates)?
        4. It separates the paths into two lists: `valid` and `rejected` (with a reason for rejection).
    - **Returns:** A tuple containing the list of valid absolute paths and a list of rejected paths with reasons.

- **`create_zip_from_paths(output_zip: str, paths: Sequence[str], base_root: str, ...)`**
    - **Purpose:** To create a ZIP file from a list of validated paths relative to a single base root.
    - **Logic:**
        1. Creates the output directory if it doesn't exist.
        2. Opens a new `ZipFile` for writing.
        3. Iterates through the `paths`. For each path, it recursively walks directories to add all child files or adds a single file, using `_safe_add_file` for each addition to ensure security.

- **`sanitize_and_validate_paths_multi(...)` and `create_zip_from_paths_multi(...)`**
    - **Purpose:** More complex versions of the functions above that work with a *sequence* of allowed `base_roots` instead of just one. This is useful when tenant data might be in more than one location.

- **`build_tenant_export_zip(tenant_id: int, output_zip: str) -> None`**
    - **Purpose:** A high-level function to create a complete data export ZIP for a specific tenant.
    - **Logic:**
        1. Defines the tenant's base data directory (e.g., `/app/data/tenants/123`).
        2. Creates a new ZIP file.
        3. Writes a `MANIFEST.txt` file into the archive.
        4. Safely walks the tenant's data directory and adds all files to the archive under a `tenant_data/` prefix.
        5. **(Optional DB Export)**: If the `Asset` model is available, it connects to the database, queries the first 10,000 assets for that tenant, formats them as a CSV, and writes the result to `assets.csv` inside the ZIP file.

### 3.8 Data Models (SQLAlchemy)
This section provides a detailed breakdown of the core SQLAlchemy models that define the application's database schema. These models are located in `backend/app/models/`.

#### 3.8.1 `app/models/tenant.py`
- **`Tenant(Base, TimestampMixin, ModelMixin)`**
    - **Purpose:** Represents an organization or customer, the top-level container for all other data in the system.
    - **Inheritance:**
        - `Base`: Declarative base from SQLAlchemy.
        - `TimestampMixin`: Adds `created_at` and `updated_at` columns with automatic timestamping.
        - `ModelMixin`: Adds default `__repr__` and `as_dict()` methods.
    - **Columns:**
        - `id` (Integer, Primary Key): Unique identifier for the tenant.
        - `name` (String, Not Null, Unique): The human-readable name of the tenant.
        - `slug` (String, Not Null, Unique): A URL-safe, unique identifier for the tenant.
        - `is_active` (Boolean, Not Null, Default: `True`): A flag to enable or disable the tenant.
        - `storage_quota_gb` (Integer, Not Null, Default: `10`): The storage quota allocated to the tenant in gigabytes.
    - **Relationships:**
        - Defines one-to-many relationships with nearly every other data model in the system (e.g., `users`, `agents`, `assets`, `scan_jobs`).
        - The `cascade="all, delete-orphan"` option on these relationships ensures that when a tenant is deleted, all of its associated data (users, assets, etc.) is automatically deleted from the database.

#### 3.8.2 `app/models/user.py`
- **`User(Base, TimestampMixin, ModelMixin)`**
    - **Purpose:** Represents a user account within a specific tenant.
    - **Columns:**
        - `id` (Integer, Primary Key): Unique identifier for the user.
        - `username` (String, Not Null, Unique): The user's login name.
        - `password_hash` (String, Not Null): The user's hashed password (using bcrypt).
        - `email` (String, Unique): The user's email address.
        - `is_active` (Boolean, Default: `True`): A flag to enable or disable the user's account.
        - `tenant_id` (Integer, Foreign Key to `tenants.id`): The ID of the tenant this user belongs to. This is the critical link for multi-tenancy.
        - `role` (String, Not Null, Default: `"standard_user"`): The user's role within the application (e.g., "admin", "standard_user").
    - **Relationships:**
        - `tenant`: A many-to-one relationship back to the `Tenant` model.
        - `audit_logs`: A one-to-many relationship to the user's entries in the audit log.
        - `refresh_tokens`: A one-to-many relationship to the user's stored refresh tokens.
        - `notification_settings`: A one-to-many relationship to the user's notification preferences.

#### 3.8.3 `app/models/role.py`
- **`Role(Base, TimestampMixin, ModelMixin)`**
    - **Purpose:** Defines a user role available in the system. While the `User` model currently stores the role as a string, this model allows for a more structured, relational approach to roles in the future.
    - **Columns:**
        - `id` (Integer, Primary Key): Unique identifier for the role.
        - `name` (String, Not Null, Unique): The name of the role (e.g., "admin").

#### 3.8.4 `app/models/module.py`
- **`Module(Base, TimestampMixin, ModelMixin)`**
    - **Purpose:** Represents a "scan module," which is a template for a specific task or check that can be run by an agent.
    - **Columns:**
        - `id` (Integer, Primary Key): Unique identifier for the module.
        - `name` (String, Not Null, Unique): The unique name of the module.
        - `category` (String): The category the module belongs to (e.g., "system_inventory", "compliance").
        - `status` (String): The module's lifecycle status (e.g., "draft", "released", "deprecated").
        - `checksum` (String): A checksum to verify the integrity of the module's script or definition.
        - `description` (Text): A detailed description of what the module does.
        - `parameter_schema` (JSON): A JSON object defining the parameters the module accepts, including their types and validation rules.
        - `enabled` (Boolean, Default: `True`): A flag to enable or disable the module globally.
    - **Relationships:**
        - `tenant_modules`: Links to the `TenantModule` association table, which defines which tenants can use this module.
        - `scan_results`: A one-to-many relationship to all results generated by this module.
    - **Properties:**
        - `is_effectively_enabled` (property): A computed property that returns `True` only if the module's `enabled` flag is true and its `status` is not a "disabled" status (like "retired" or "deprecated").

#### 3.8.5 `app/models/scan_job.py`
This file defines two related models for orchestrating scans.
- **`ScanJob(Base)`**
    - **Purpose:** Represents a request to run a scan, either on-demand or on a schedule. It acts as a container for the individual tasks.
    - **Columns:**
        - `id` (Integer, Primary Key): Unique identifier for the job.
        - `tenant_id` (Integer, Foreign Key): The tenant that owns this job.
        - `name` (String): A human-readable name for the job.
        - `schedule` (String, Nullable): A cron-like string defining when the job should run. If `NULL`, it's an on-demand job.
        - `status` (String, Default: `"pending"`): The current status of the job (e.g., "pending", "running", "completed").
        - `created_by` (Integer, Foreign Key to `users.id`): The user who created the job.
    - **Relationships:**
        - `tenant`: A many-to-one relationship to the `Tenant`.
        - `creator`: A many-to-one relationship to the `User` who created the job.
        - `results`: A one-to-many relationship to the `ScanResult` records generated by this job.
    - **Methods:**
        - `as_dict()`: Returns a dictionary representation of the model's data.

- **`ScanResult(Base)`**
    - **Purpose:** Represents the result of a single task within a `ScanJob`, typically corresponding to one agent or one asset.
    - **Table Name:** `scan_results_v2`.
    - **Columns:**
        - `id` (Integer, Primary Key): Unique identifier for the result.
        - `job_id` (Integer, Foreign Key): The ID of the parent `ScanJob`.
        - `agent_id` (Integer, Foreign Key, Nullable): The ID of the agent that performed the scan.
        - `asset_id` (Integer, Foreign Key, Nullable): The ID of the asset that was scanned.
        - `status` (String, Default: `"queued"`): The status of this specific task (e.g., "queued", "running", "success", "failed").
        - `details` (Text, Nullable): A field to store error messages or other detailed output from the scan.
    - **Methods:**
        - `as_dict()`: Returns a dictionary representation of the model's data.

### 3.9 API Route: Authentication (`/auth`)
This section details the authentication endpoints located in `backend/app/routes/auth.py`. These endpoints are responsible for user login and token introspection.

#### 3.9.1 File Breakdown
- **`app/routes/auth.py`**: Contains the route handlers for `/auth/login` and `/auth/me`.
- **`app/schemas/token.py`**: Defines the Pydantic schemas for refresh tokens (not directly used in `auth.py` but related). The schemas for login are defined directly within `auth.py`.

#### 3.9.2 Schemas (Request/Response Models)

- **`LoginJSON(BaseModel)`**
    - **Purpose:** Defines the expected JSON request body for the login endpoint.
    - **Fields:**
        - `username` (str): The user's username.
        - `password` (str): The user's plaintext password.

- **`UserOut(BaseModel)`**
    - **Purpose:** Defines the shape of the user object returned to the client. It's a security best practice to have a separate "output" model to avoid accidentally leaking sensitive fields like `password_hash`.
    - **Fields:**
        - `id` (int): The user's primary key.
        - `username` (str): The user's username.
        - `email` (Optional[str]): The user's email.
        - `is_active` (bool): The user's active status.
        - `role` (Optional[str]): The user's role. This is critical for the frontend to perform its own role-based access control on UI elements.

- **`TokenOut(BaseModel)`**
    - **Purpose:** Defines the successful response body for a login request.
    - **Fields:**
        - `access_token` (str): The newly generated JWT.
        - `token_type` (str): The token type, typically `"bearer"`.
        - `user` (UserOut): An embedded `UserOut` object, allowing the frontend to immediately know who the user is and what their role is without making a second API call.

#### 3.9.3 Endpoint: `POST /auth/login`

- **`login(request: Request, ...)`**
    - **Purpose:** To authenticate a user and issue an access token.
    - **Request Body:** The endpoint is cleverly designed to accept credentials in two common formats:
        1.  `application/x-www-form-urlencoded`: With `username` and `password` fields.
        2.  `application/json`: With a JSON body matching the `LoginJSON` schema.
    - **Logic:**
        1.  It first checks if `username` and `password` were provided as form fields.
        2.  If not, it checks the `Content-Type` header. If it's `application/json`, it attempts to parse the request body into the `LoginJSON` model. If parsing or validation fails, it raises a 422 Unprocessable Entity error.
        3.  If credentials are not provided in either format, it raises a 422 error.
        4.  It queries the database for a `User` with a matching `username`.
        5.  It then calls `verify_password()` to securely check the provided password against the stored `password_hash`.
        6.  **Security Note:** If the user is not found or the password does not match, it returns a generic 401 Unauthorized error. This prevents attackers from determining whether a username is valid or not (user enumeration).
        7.  If authentication is successful, it calls `create_access_token()`, passing the user's ID as the `sub` claim in the payload.
        8.  Finally, it constructs and returns a `TokenOut` response containing the access token and the user's profile information.

#### 3.9.4 Endpoint: `OPTIONS /auth/login`

- **`login_preflight(request: Request, ...)`**
    - **Purpose:** To handle CORS preflight requests for the login endpoint.
    - **Logic:** This is a complex and dynamic CORS handler.
        1.  It inspects the `Origin` header from the incoming request.
        2.  It builds a set of allowed origins by combining a static list from the `CORS_ALLOWED_ORIGINS` environment variable with a dynamic list from the `TenantCORSOrigin` table in the database.
        3.  It attempts to identify the tenant based on request headers (`X-Tenant-Id`, `X-Tenant-Slug`) or the hostname subdomain.
        4.  If a tenant is identified, it checks if the request's `Origin` is specifically allowed for that tenant.
        5.  If the origin is in the final list of allowed origins, it returns a 204 No Content response with the appropriate `Access-Control-Allow-*` headers, including `Access-Control-Allow-Origin: <request_origin>`.
        6.  If the origin is not allowed, it returns a 204 response without the CORS headers, effectively denying the cross-origin request.

#### 3.9.5 Endpoint: `GET /auth/me`

- **`get_current_user_me(token: str = Depends(oauth2_scheme), ...)`**
    - **Purpose:** To allow a client to validate an access token and retrieve the profile of the user associated with it.
    - **Protection:** This route is protected by the `oauth2_scheme` dependency, which ensures a valid `Authorization: Bearer <token>` header is present.
    - **Logic:**
        1.  It receives the token string from the dependency.
        2.  It calls `decode_access_token()` to validate the token and extract its payload. If the token is invalid or expired, it raises a 401 Unauthorized error.
        3.  It extracts the `user_id` from the `sub` claim in the payload.
        4.  It queries the database for the user with that ID. If the user no longer exists, it raises a 404 Not Found error.
        5.  If the user is found, it constructs and returns a `UserOut` object containing the user's public profile information, including their role.

### 3.10 API Route: User Management (`/users`)
This section details the endpoints for managing users, which are split into two files: one for users managing their own profiles (`users_me.py`) and one for administrators managing all users (`users_admin.py`).

#### 3.10.1 File Breakdown
- **`app/routes/users_me.py`**: Contains endpoints for the currently authenticated user to view and update their own profile.
- **`app/routes/users_admin.py`**: Contains CRUD (Create, Read, Update, Delete) endpoints for administrators to manage all users within their tenant scope.
- **`app/schemas/user.py`**: Defines the basic Pydantic schemas for user data, although the route files define their own more specific schemas.

#### 3.10.2 Schemas (Request/Response Models)

- **`UserAdminOut(BaseModel)`** (in `users_admin.py`)
    - **Purpose:** The data shape for a user when returned from an admin endpoint.
    - **Fields:** `id`, `username`, `email`, `is_active`, `role`, `tenant_id`.

- **`UserCreateIn(BaseModel)`** (in `users_admin.py`)
    - **Purpose:** The request body for an admin creating a new user.
    - **Fields:** `username`, `password`, `email`, `role`, `tenant_id`.
    - **Validation:** Includes a Pydantic `field_validator` for the `password` field that enforces a complexity policy (must contain lowercase, uppercase, digit, special character, and be at least 8 characters long).

- **`UserUpdateIn(BaseModel)`** (in `users_admin.py`)
    - **Purpose:** The request body for an admin updating a user. All fields are optional.
    - **Fields:** `email`, `role`, `is_active`, `password`, `tenant_id`.
    - **Validation:** Also includes a validator for the `password` field if it is provided.

- **`UserUpdateRequest(BaseModel)`** (in `users_me.py`)
    - **Purpose:** The request body for a user updating their own profile.
    - **Fields:** `new_email`, `new_password`, `current_password`. The `current_password` is required if `new_password` is set.

#### 3.10.3 Admin Endpoints (`/users`)

- **Dependencies:**
    - **`require_admin(...)`**: A route dependency defined in this file that ensures the user making the request has a role included in the `ADMIN_ROLES` set. It reuses `get_current_user` to resolve the user from the token.

- **`GET /users`**
    - **`list_users(admin: User = Depends(require_admin), ...)`**
    - **Purpose:** To list users.
    - **Logic:**
        1.  The request is protected by the `require_admin` dependency.
        2.  It checks if the authenticated admin is a "super admin" (via `_is_super_admin`).
        3.  If the user is a super admin, the query returns all users.
        4.  If the user is a standard admin, the query is filtered to only return users with the same `tenant_id` as the admin.
        5.  In development environments, it also filters out inactive users.
        6.  Returns a list of users matching the `UserAdminOut` schema.

- **`POST /users`**
    - **`create_user(payload: UserCreateIn, ...)`**
    - **Purpose:** To create a new user.
    - **Logic:**
        1.  Checks for conflicts: raises a 409 Conflict error if the `username` or `email` already exists.
        2.  **Tenant Scoping:** It calls `_resolve_tenant_scope()` to determine the correct `tenant_id` for the new user. A standard admin is forced to use their own `tenant_id`. A super admin can specify a `tenant_id` in the payload.
        3.  It validates that the resolved `tenant_id` exists in the database.
        4.  It hashes the provided password using `get_password_hash()`.
        5.  Creates a new `User` model instance, saves it to the database, and returns the new user's data.

- **`PUT /users/{user_id}`**
    - **`update_user(user_id: int, payload: UserUpdateIn, ...)`**
    - **Purpose:** To update an existing user's details.
    - **Logic:**
        1.  Finds the user by `user_id`. Raises 404 if not found.
        2.  **Tenant Scoping:** Calls `_enforce_same_tenant()` which prevents a standard admin from updating a user in another tenant (it returns a 404 to avoid leaking information). Super admins can bypass this check.
        3.  It updates the user's attributes based on the optional fields provided in the `UserUpdateIn` payload.
        4.  If a new password is provided, it is hashed.
        5.  Only a super admin can change a user's `tenant_id`.
        6.  Commits the changes and returns the updated user data.

- **`DELETE /users/{user_id}`**
    - **`delete_user(user_id: int, ...)`**
    - **Purpose:** To delete a user.
    - **Logic:**
        1.  Finds the user by `user_id`. Raises 404 if not found.
        2.  Prevents an admin from deleting themselves (raises 400).
        3.  Enforces tenant scope using `_enforce_same_tenant()`.
        4.  It attempts a "hard delete" (`db.delete(user)`).
        5.  If the hard delete fails due to a database foreign key constraint (`IntegrityError`), it means the user is referenced by other records.
        6.  In this case, it raises a 409 Conflict error in production.
        7.  In a development environment, it attempts a "soft delete" as a fallback: it sets `is_active = False` and prepends `"deleted:"` to the username to free up the unique constraint.

#### 3.10.4 Self-Service Endpoints (`/users/me`)

- **`GET /users/me`**
    - **`get_current_user(token: str = Depends(oauth2_scheme), ...)`**
    - **Purpose:** To allow an authenticated user to retrieve their own profile information.
    - **Logic:**
        1.  Protected by the `oauth2_scheme` dependency.
        2.  Decodes the token to get the `user_id`.
        3.  Fetches the user from the database.
        4.  Returns a dictionary containing the user's public information (`id`, `username`, `email`, `role`, `is_active`).

- **`PUT /users/me`**
    - **`update_current_user(update_data: UserUpdateRequest, ...)`**
    - **Purpose:** To allow a user to update their own email or password.
    - **Logic:**
        1.  Fetches the user based on the token.
        2.  If `new_email` is provided, it updates the user's email.
        3.  If `new_password` is provided:
            a. It first requires `current_password` to be present in the payload (raises 400 if not).
            b. It verifies the `current_password` against the stored hash using `verify_password()`. Raises 401 if it doesn't match.
            c. If verification passes, it hashes the `new_password` and updates the user's `password_hash`.
        4.  Commits the changes to the database and returns the updated user profile.

### 3.11 API Route: Agents & Scanning
This section details the endpoints related to agent management, scan scheduling, orchestration, and results processing. These routes form the core of Tenantra's data collection capabilities.

#### 3.11.1 File Breakdown
- **`app/routes/agents.py`**: Endpoints for agents to enroll and fetch their configuration.
- **`app/routes/agents_admin.py`**: Admin-only endpoints for listing and managing agents.
- **`app/routes/agent_logs.py`**: Endpoints for agents to submit logs and for admins to retrieve them.
- **`app/routes/schedules.py`**: Endpoints for creating, viewing, and deleting scheduled scans.
- **`app/routes/scan_orchestration.py`**: Endpoints for managing the lifecycle of "scan jobs" and their associated results.
- **`app/routes/scan_results.py`**: Endpoints for querying and exporting categorized scan data (e.g., file scans, network scans).

#### 3.11.2 Agent Management Endpoints

- **`POST /agents/enroll`** (`agents.py`)
    - **Purpose:** Allows a new agent to be created and receive its unique authentication token.
    - **Protection:** Requires an authenticated user with an "admin" or "super_admin" role.
    - **Request Body:** `{ "name": "my-new-agent" }`
    - **Logic:**
        1.  An admin user makes this call, providing a name for the new agent.
        2.  A new, cryptographically secure token is generated using `secrets.token_hex(16)`.
        3.  A new `Agent` record is created in the database, linking it to the admin's `tenant_id`.
        4.  The `agent_id` and the raw `token` are returned. This token must be securely transferred to the agent machine.

- **`GET /agents/config/{agent_id}`** (`agents.py`)
    - **Purpose:** Allows an enrolled agent to fetch its configuration.
    - **Protection:** Requires an authenticated user (which can be an agent itself, though the code uses `get_current_user`). It also enforces a tenant match between the agent and the user making the request.
    - **Logic:**
        1.  The agent makes a request to its own config endpoint.
        2.  The system fetches all `Module` definitions from the database.
        3.  It then checks for any tenant-specific overrides in the `TenantModule` table.
        4.  It computes the final list of *enabled* module names for that agent's tenant.
        5.  Returns a JSON object containing the `agent_id` and the list of enabled `modules`.

- **`GET /admin/agents`** (`agents_admin.py`)
    - **Purpose:** Allows an administrator to list all agents.
    - **Protection:** Requires an admin user (`get_admin_user`).
    - **Query Parameters:** `tenant_id` (optional) to filter agents by a specific tenant.
    - **Logic:**
        1.  Queries the `Agent` table.
        2.  If `tenant_id` is provided, it adds a filter to the query.
        3.  Returns a list of agent objects, including their `id`, `name`, `tenant_id`, and `is_active` status.

#### 3.11.3 Scan Scheduling Endpoints (`/schedules`)

- **`POST /schedules`** (`schedules.py`)
    - **Purpose:** To create a new scheduled scan.
    - **Protection:** Requires an admin user.
    - **Request Body:** A `ScheduleCreate` schema containing `module_id`, `cron_expr`, `parameters`, and optionally `agent_id` and `tenant_id`.
    - **Logic:**
        1.  Validates that the `module_id` exists.
        2.  Resolves the `tenant_id` (must be specified for super admins, defaults to the admin's own tenant otherwise).
        3.  Calculates the `next_run_at` timestamp based on the `cron_expr` using the `compute_next_run` utility.
        4.  Creates a new `ScheduledScan` record in the database with a status of "scheduled".
        5.  Returns the newly created schedule object.

- **`GET /schedules`** (`schedules.py`)
    - **Purpose:** To list existing scheduled scans.
    - **Protection:** Requires an authenticated user.
    - **Logic:**
        1.  If the user is not a super admin, the query is automatically filtered by the user's `tenant_id`.
        2.  Supports an optional `module_id` query parameter to filter by module.
        3.  Returns a list of schedule objects.

- **`DELETE /schedules/{schedule_id}`** (`schedules.py`)
    - **Purpose:** To delete a scheduled scan.
    - **Protection:** Requires an admin user and enforces tenant scope (an admin cannot delete a schedule from another tenant).
    - **Logic:** Finds the `ScheduledScan` by its ID and deletes it from the database.

#### 3.11.4 Scan Orchestration Endpoints (`/scan-orchestration`)

- **`POST /jobs`**
    - **Purpose:** To create a new on-demand scan job.
    - **Logic:** Creates a `ScanJob` record with a "pending" status. This acts as a container for one or more scan results.

- **`GET /jobs`**
    - **Purpose:** To list scan jobs for a tenant.
    - **Logic:** Returns a list of `ScanJob` records, filterable by `status`. Enforces tenant scope.

- **`GET /jobs/{job_id}`**
    - **Purpose:** To get the details of a specific scan job, including all of its child results.
    - **Logic:** Fetches the `ScanJob` and its related `ScanResult` records.

- **`POST /jobs/{job_id}/results`**
    - **Purpose:** To associate a new scan result with a job. This is likely called by the scheduler when it dispatches a task to an agent.
    - **Logic:** Creates a `ScanResult` record linked to the `job_id`.

- **`POST /results/{result_id}/status`**
    - **Purpose:** To allow an agent or worker to update the status of a specific scan task (e.g., from "running" to "completed").
    - **Logic:** Updates the `status` and `details` of a `ScanResult` record.

#### 3.11.5 Data Ingestion & Retrieval Endpoints

- **`POST /agents/{agent_id}/logs`** (`agent_logs.py`)
    - **Purpose:** Allows an agent to submit log entries.
    - **Protection:** Authenticates the agent using a unique `X-Agent-Token` provided in the request header.
    - **Request Body:** `{ "severity": "info", "message": "Agent started successfully" }`
    - **Logic:**
        1.  Authenticates the agent by comparing the provided token with the one stored in the database.
        2.  Creates a new `AgentLog` record associated with the `agent_id`.
        3.  Returns a success status.

- **`GET /agents/{agent_id}/logs`** (`agent_logs.py`)
    - **Purpose:** Allows an admin to retrieve the latest logs for a specific agent.
    - **Protection:** Requires an admin user and enforces tenant scope.
    - **Logic:** Queries the `AgentLog` table for the given `agent_id` and returns the last 100 log entries.

- **`GET /scans/files` and `GET /scans/network`** (`scan_results.py`)
    - **Purpose:** To query raw, categorized scan results for a tenant.
    - **Protection:** Requires an admin user and enforces tenant scope via the `tenant_id` query parameter.
    - **Logic:** Queries the `FileScanResult` or `NetworkScanResult` tables, joining with the `Agent` table to filter by tenant. Returns a list of result objects.

- **`GET /scans/files/export.csv` and `GET /scans/network/export.csv`** (`scan_results.py`)
    - **Purpose:** To provide a CSV export of the raw scan results.
    - **Logic:** Similar to the GET endpoints, but formats the results into a CSV file and returns it as a downloadable attachment.

### 3.12 API Route: Modules & Execution
This section covers the endpoints responsible for managing the scan module catalog, controlling tenant access to modules, and executing them.

#### 3.12.1 File Breakdown
- **`app/routes/modules.py`**: Endpoints for listing the module catalog and managing tenant-specific module enablement.
- **`app/routes/modules_admin.py`**: Admin-level endpoints for bulk-enabling modules and seeding the catalog from a source file.
- **`app/routes/module_runs.py`**: Endpoints for initiating on-demand module scans and retrieving the history of past runs.
- **`app/routes/module_mapping.py`**: Appears to be a legacy or alternative system for mapping modules directly to agents.

#### 3.12.2 Module Catalog and Enablement

- **`GET /modules/`** (`modules.py`)
    - **Purpose:** To retrieve the list of all available scan modules and their effective status for the current user's tenant.
    - **Protection:** Requires any authenticated user.
    - **Logic:**
        1.  Fetches all `Module` records from the database.
        2.  If the user belongs to a tenant, it fetches all `TenantModule` override records for that tenant.
        3.  For each module, it determines the `effective` enablement status: if a tenant override exists, it is used; otherwise, the module's global `is_effectively_enabled` status is used.
        4.  It serializes each module into a rich JSON object, including its metadata, parameter schema, and a `has_runner` flag indicating if it's executable.
        5.  Returns the full list of serialized modules.

- **`PUT /modules/{module_id}`** (`modules.py`)
    - **Purpose:** To explicitly enable or disable a module for the current admin's tenant.
    - **Protection:** Requires an "admin" or "super_admin" role.
    - **Request Body:** `{ "enabled": true }`
    - **Logic:**
        1.  Finds the `TenantModule` record for the given `module_id` and the admin's `tenant_id`.
        2.  If a record exists, it updates the `enabled` flag.
        3.  If no record exists, it creates a new `TenantModule` record to store the override.
        4.  Commits the change and returns the updated module object.

- **`PUT /admin/modules/bulk`** (`modules_admin.py`)
    - **Purpose:** To allow an admin to enable or disable multiple modules for their tenant in a single API call.
    - **Protection:** Requires an admin user.
    - **Request Body:** `{ "enable": [1, 2, 5], "disable": [3, 4] }`
    - **Logic:**
        1.  Iterates through the union of module IDs in the `enable` and `disable` lists.
        2.  For each `module_id`, it upserts a `TenantModule` record, setting the `enabled` flag to `True` if the ID was in the `enable` list.
        3.  Returns a count of the records that were changed.

- **`POST /admin/modules/seed`** (`modules_admin.py`)
    - **Purpose:** A powerful admin action to bootstrap or update the entire module catalog from a source CSV file.
    - **Protection:** Requires an admin user.
    - **Logic:**
        1.  Locates a specific CSV file within the container (e.g., `/app/docs/modules/Tenantra_Module_Backlog_PhaseLinked_v8.csv`).
        2.  Calls an importer script (`import_modules_from_csv.py`) which parses the CSV and upserts `Module` records into the database.
        3.  It also ensures a default "Port Scan" module exists for demonstration purposes.
        4.  Returns statistics on how many modules were created or updated.

#### 3.12.3 Module Execution

- **`POST /module-runs/{module_id}`** (`module_runs.py`)
    - **Purpose:** To trigger an immediate, on-demand execution of a specific module.
    - **Protection:** Requires an admin user.
    - **Request Body:** A `ModuleRunRequest` schema containing the target `agent_id` and any `parameters` required by the module's schema.
    - **Logic:**
        1.  Finds the requested `Module` by its ID.
        2.  Calls the `execute_module` service function, passing the module, tenant context, agent ID, and parameters.
        3.  The service is responsible for finding the correct Python "runner" for the module and executing it.
        4.  If no runner is implemented for the module, it raises a 400 Bad Request error.
        5.  The result of the execution is saved as a `ScanModuleResult` record.
        6.  Returns a `ModuleRunResponse` object representing the completed run record.

- **`GET /module-runs`** (`module_runs.py`)
    - **Purpose:** To retrieve a history of module run results for the admin's tenant.
    - **Protection:** Requires an admin user.
    - **Logic:**
        1.  Queries the `ScanModuleResult` table, filtered by the admin's `tenant_id`.
        2.  Can be optionally filtered by `module_id`.
        3.  Returns a list of the most recent run records.

### 3.13 API Route: Compliance & Assets
This section covers the endpoints for viewing asset inventory, analyzing compliance data, and managing the underlying compliance frameworks and rules.

#### 3.13.1 File Breakdown
- **`app/routes/assets.py`**: A read-only endpoint for listing discovered assets.
- **`app/routes/compliance.py`**: Endpoints for querying aggregated and raw compliance scan results.
- **`app/routes/compliance_export.py`**: Endpoints for exporting compliance data to CSV and PDF.
- **`app/routes/compliance_matrix.py`**: CRUD endpoints for managing the compliance frameworks and rules that define the standards.

#### 3.13.2 Asset and Compliance Data Retrieval

- **`GET /assets`** (`assets.py`)
    - **Purpose:** To provide a basic inventory of discovered assets.
    - **Protection:** Requires an authenticated user.
    - **Logic:**
        1.  Performs a simple query on the `Asset` table.
        2.  Returns a list of the first 200 assets with key fields like `hostname`, `ip_address`, and `os`.
        3.  **Note:** This endpoint does not currently implement tenant-based filtering, meaning all users can see all assets. This is a potential security gap.

- **`GET /compliance/trends`** (`compliance.py`)
    - **Purpose:** To provide aggregated time-series data for compliance dashboards.
    - **Protection:** Requires an authenticated user; data is filtered by the user's tenant.
    - **Query Parameters:** `days` (number of days for the trend), `module` (filter by a specific module name).
    - **Logic:**
        1.  Calculates a date range based on the `days` parameter.
        2.  Initializes a dictionary to hold pass/fail counts for each day in the range.
        3.  Queries the `ComplianceResult` table for all results within the date range and for the user's tenant.
        4.  Aggregates the results, incrementing the `pass` or `fail` count for each day.
        5.  Returns a list of objects, each containing a `date`, `pass` count, and `fail` count.

- **`GET /compliance/results`** (`compliance.py`)
    - **Purpose:** To retrieve a list of raw compliance scan results for detailed analysis.
    - **Protection:** Requires an authenticated user; data is filtered by the user's tenant.
    - **Query Parameters:** `limit`, `module`, `status_filter`.
    - **Logic:** Queries the `ComplianceResult` table, applying the user's tenant scope and any optional filters, and returns a list of the raw result records.

- **`GET /compliance/export.csv` & `GET /compliance/export.pdf`** (`compliance_export.py`)
    - **Purpose:** To export compliance results into downloadable file formats.
    - **Protection:** None. These endpoints are open.
    - **Logic:**
        1.  Queries the `ComplianceResult` table for the last 500 results.
        2.  Uses Python's `csv` module or the `fpdf` library to generate the file content in memory.
        3.  Returns the generated content with the appropriate `Content-Type` and `Content-Disposition` headers.
        4.  **Note:** Like the assets endpoint, these do not enforce tenant scoping and will export data from all tenants. This is a potential security gap.

#### 3.13.3 Compliance Framework Management

- **`GET /compliance-matrix/frameworks`** (`compliance_matrix.py`)
    - **Purpose:** To list all defined compliance frameworks (e.g., NIST, CIS, ISO 27001).
    - **Protection:** Requires an admin user.
    - **Logic:** Queries and returns all records from the `ComplianceFramework` table.

- **`POST /compliance-matrix/frameworks`** (`compliance_matrix.py`)
    - **Purpose:** To create a new compliance framework.
    - **Protection:** Requires an admin user.
    - **Logic:** Creates a new `ComplianceFramework` record. Enforces that the framework `code` is unique.

- **`GET /compliance-matrix/rules`** (`compliance_matrix.py`)
    - **Purpose:** To list all defined compliance rules/controls.
    - **Protection:** Requires an admin user.
    - **Query Parameters:** `framework_id` (to filter rules belonging to a specific framework).
    - **Logic:** Queries the `ComplianceRule` table and returns a list of rule objects. Each object includes a list of `framework_ids` it is mapped to.

- **`POST /compliance-matrix/rules`** (`compliance_matrix.py`)
    - **Purpose:** To create a new compliance rule and associate it with one or more frameworks.
    - **Protection:** Requires an admin user.
    - **Logic:**
        1.  Creates a new `ComplianceRule` record, ensuring the `control_id` is unique.
        2.  If `framework_ids` are provided in the payload, it creates corresponding records in the `ComplianceRuleFramework` association table to link the new rule to its parent frameworks.

- **`GET /compliance-matrix/matrix`** (`compliance_matrix.py`)
    - **Purpose:** To fetch all the data needed to render a full compliance matrix UI.
    - **Protection:** Requires an admin user.
    - **Logic:** Fetches all frameworks and all rules in two separate queries and returns them in a single response object, allowing the client to construct the full matrix.

### 3.14 API Route: Alerts & Notifications
This section details the multi-layered system for defining alert rules, managing notifications, respecting user preferences, and logging delivery history.

#### 3.14.1 File Breakdown
- **`app/routes/alerts.py`**: CRUD endpoints for managing the `AlertRule` definitions that trigger notifications.
- **`app/routes/notifications.py`**: Endpoints for creating and sending individual `Notification` instances.
- **`app/routes/notification_prefs.py`**: Endpoints for managing user- and tenant-level preferences for notification delivery.
- **`app/routes/notification_history.py`**: Endpoints for logging and querying the history of all notification delivery attempts.
- **`app/routes/notification_settings.py`**: A legacy or alternative set of endpoints for managing notification settings.

#### 3.14.2 Alert Rule Management

- **`GET /alerts`** (`alerts.py`)
    - **Purpose:** To list all alert rules for a given tenant.
    - **Protection:** Requires an admin user. Enforces tenant scope.
    - **Logic:** Queries the `AlertRule` table, filtered by the resolved `tenant_id`, and returns a list of rule objects.

- **`POST /alerts`** (`alerts.py`)
    - **Purpose:** To create a new alert rule.
    - **Protection:** Requires an admin user. Enforces tenant scope.
    - **Request Body:** A JSON object with `name`, `condition`, `threshold`, and `enabled` fields.
    - **Logic:** Creates a new `AlertRule` record in the database, associated with the admin's tenant.

- **`PUT /alerts/{alert_id}`** (`alerts.py`)
    - **Purpose:** To update an existing alert rule.
    - **Protection:** Requires an admin user. Enforces tenant scope.
    - **Logic:** Finds the `AlertRule` by ID and tenant, then updates its fields from the request payload.

- **`DELETE /alerts/{alert_id}`** (`alerts.py`)
    - **Purpose:** To delete an alert rule.
    - **Protection:** Requires an admin user. Enforces tenant scope.
    - **Logic:** Finds the `AlertRule` by ID and tenant, then deletes it from the database.

#### 3.14.3 Notification Lifecycle

- **`POST /notifications`** (`notifications.py`)
    - **Purpose:** To create a new notification record in a "queued" state.
    - **Protection:** Requires an admin user.
    - **Request Body:** A `NotificationCreate` schema with `recipient_email`, `title`, `message`, and `severity`.
    - **Logic:**
        1.  Creates a new `Notification` record in the database with `status="queued"`.
        2.  It attempts to resolve the `recipient_email` to a user in the database to link the `recipient_id`.
        3.  Logs an audit event for the creation of the notification.

- **`POST /notifications/send/{notification_id}`** (`notifications.py`)
    - **Purpose:** To trigger the immediate delivery of a queued notification.
    - **Protection:** Requires an admin user. Enforces tenant scope.
    - **Logic:**
        1.  Finds the `Notification` record.
        2.  Calls the `send_email` utility service.
        3.  Updates the notification's status to "sent" or "failed" based on the outcome.
        4.  Records a metric for the delivery attempt using `record_notification_delivery`.
        5.  Logs an audit event for the send attempt.

#### 3.14.4 Preferences and History

- **`GET /notification-prefs`** (`notification_prefs.py`)
    - **Purpose:** To get the effective notification preferences for a user or an entire tenant.
    - **Protection:** Requires an authenticated user.
    - **Logic:**
        1.  It first attempts to find a `NotificationPreference` record for the specific `user_id` (if provided).
        2.  If no user-specific override is found, it falls back to the tenant-wide default (where `user_id` is `NULL`).
        3.  If no preferences are configured at all, it returns a hardcoded, sensible default.
        4.  The preferences include dictionaries for `channels` (e.g., email on/off) and `events` (e.g., scan_failed on/off).
        5.  Responses leverage the Pydantic v2 `ConfigDict(from_attributes=True)` on `NotificationPrefsRead`, allowing `.from_orm` to keep working without legacy `Config` classes.

- **`PUT /notification-prefs`** (`notification_prefs.py`)
    - **Purpose:** To create or update notification preferences for a user or a tenant.
    - **Protection:** Requires an authenticated user. Standard users can only update their own preferences; admins can update tenant-wide settings.
    - **Logic:** "Upserts" a `NotificationPreference` record. It updates the record if one exists or creates a new one if it doesn't.
    - **Bootstrap Note:** `bootstrap_test_data()` now imports the `NotificationPreference` model before running `Base.metadata.create_all`, ensuring the backing table exists during local or CI tests without running Alembic migrations.

- **`GET /notification-history`** (`notification_history.py`)
    - **Purpose:** To retrieve a log of past notification delivery attempts.
    - **Protection:** Requires an authenticated user. Enforces tenant scope.
    - **Logic:** Queries the `NotificationLog` table, which contains detailed records of each sent notification, including the channel, recipient, status, and any errors.

### 3.15 API Route: System & Administration
This section covers a diverse set of endpoints for managing core application configuration, administrative functions, and system-level features.

#### 3.15.1 File Breakdown
- **`app/routes/tenants_admin.py`**: Basic CRUD endpoints for managing tenants.
- **`app/routes/roles.py`**: CRUD endpoints for defining user roles and assigning them.
- **`app/routes/cors_admin.py`**: Endpoints to manage per-tenant CORS origins.
- **`app/routes/app_settings.py`**: A powerful, key-value system for managing global and tenant-specific application settings.
- **`app/routes/public_settings.py`**: A read-only endpoint that exposes a safe, whitelisted subset of settings for pre-authentication UI configuration.
- **`app/routes/features.py`**: An endpoint that computes and returns a dictionary of enabled UI features for the current user.
- **`app/routes/observability_admin.py`**: Endpoints for checking the health of external services like Grafana.
- **`app/routes/network_admin.py`**: Utility endpoints for running ad-hoc network scans.
- **`app/routes/plan_presets.py`**: Endpoints to bootstrap a tenant with a pre-defined set of configurations.

#### 3.15.2 Tenant and Role Management

- **`GET /admin/tenants` & `POST /admin/tenants`** (`tenants_admin.py`)
    - **Purpose:** Provides full CRUD capabilities for `Tenant` records.
    - **Protection:** Requires an admin user.
    - **Logic:** Allows admins to list all tenants and create new ones, specifying their `name`, `slug`, and other attributes.

- **`GET /roles`, `POST /roles`, `DELETE /roles/{role_id}`** (`roles.py`)
    - **Purpose:** Provides full CRUD for `Role` definitions.
    - **Protection:** Requires an admin user.
    - **Logic:** Allows admins to create custom roles beyond the defaults. The DELETE endpoint prevents the deletion of built-in roles like "admin".

- **`POST /roles/assign`** (`roles.py`)
    - **Purpose:** To assign a role to a specific user.
    - **Protection:** Requires an admin user.
    - **Logic:** Updates the `role` attribute on a `User` record.

#### 3.15.3 Application Configuration

- **`GET /admin/settings` & `PUT /admin/settings`** (`app_settings.py`)
    - **Purpose:** To manage global (non-tenant) application settings.
    - **Protection:** Requires a user with settings-read or settings-write permissions.
    - **Logic:**
        1.  Uses a sophisticated Pydantic model (`_AppSettingsPayload`) to validate all incoming settings data.
        2.  Encrypts sensitive values (like passwords) before storing them in the `AppSetting` table.
        3.  Uses an in-memory cache and HTTP ETags to optimize performance.
        4.  Logs all changes to the audit trail.

- **`GET /admin/settings/tenant` & `PUT /admin/settings/tenant`** (`app_settings.py`)
    - **Purpose:** To manage settings for the current user's tenant, overriding global defaults.
    - **Protection:** Requires an admin user.
    - **Logic:** Same as the global settings endpoints, but all database operations are scoped to the user's `tenant_id`.

- **`GET /support/settings/public`** (`public_settings.py`)
    - **Purpose:** To expose a limited, safe subset of settings to unauthenticated users.
    - **Protection:** None (public).
    - **Logic:**
        1.  Queries only for `AppSetting` keys that are present in an explicit `WHITELIST_KEYS`.
        2.  Sanitizes the values before returning them (e.g., proxies the Grafana URL).
        3.  This allows the frontend login page to be styled with a custom theme color or to know the Grafana URL without requiring a user to be logged in.

- **`GET /features`** (`features.py`)
    - **Purpose:** To provide the UI with a simple dictionary of boolean flags indicating which features should be enabled.
    - **Protection:** Requires an authenticated user.
    - **Logic:**
        1.  Starts with a baseline set of flags based on the user's role (e.g., `billing` is `True` for admins).
        2.  Merges in global feature flags defined in `AppSettings`.
        3.  Merges in tenant-specific feature flags from `AppSettings`, which override the global ones.
        4.  Returns the final computed dictionary of flags.

#### 3.15.4 System Utilities

- **`GET /admin/observability/grafana/health`** (`observability_admin.py`)
    - **Purpose:** To check the health of the configured Grafana instance.
    - **Protection:** Requires an admin user.
    - **Logic:**
        1.  Reads the Grafana URL and credentials from `AppSettings`.
        2.  Makes an HTTP request to Grafana's `/api/health` endpoint.
        3.  Implements a circuit breaker pattern to avoid overwhelming a failing service. If health checks fail repeatedly, the circuit "opens" and subsequent requests will fail immediately for a configured timeout period.

- **`POST /admin/network/port-scan`** (`network_admin.py`)
    - **Purpose:** To allow an admin to run an ad-hoc port scan.
    - **Protection:** Requires an admin user.
    - **Logic:** Directly invokes the `PortScanModule` service with the provided host and port parameters.

- **`POST /admin/plans/networking-demo`** (`plan_presets.py`)
    - **Purpose:** To bootstrap a tenant with a pre-configured "demo" plan.
    - **Protection:** Requires an admin user with a tenant scope.
    - **Logic:**
        1.  Ensures a "Port Scan" module exists.
        2.  Creates two `ScheduledScan` records for the current tenant to run the port scan module on a recurring basis (e.g., every 30 minutes).

### 3.16 API Route: Scanning Modules
The scanning modules are a core component of Tenantra's architecture. They are designed to be database-first, meaning the authoritative source for all modules is the database, not CSV files.

#### 3.16.1 Module Lifecycle and Versioning
- **Authoritative Source:** All modules are stored in the database. CSV files are only used for one-time imports during development.
- **Versioning:** Each module has a stable UUID (`module_id`) and a semantic version. Any change to the module's logic or parameters creates a new version.
- **States:** Modules have a lifecycle: `draft` -> `qa` -> `released` -> `deprecated` -> `retired`. Only `released` modules can be scheduled.

#### 3.16.2 Database Schema
The following tables are used to manage the scanning modules:
- `modules`: Stores the identity and metadata of each module.
- `module_versions`: Stores the semantic version, checksum, parameter schema, and other details for each version of a module.
- `module_parameters`: Defines the parameters that a module accepts.
- `module_runs`: Records the execution of each module.
- `module_results`: Stores the normalized results of each module run.
- `tenant_module_enablement`: A join table that defines which tenants are allowed to use which modules.

#### 3.16.3 Naming and Identity
- **UUIDv4:** Used for `module_id`, `module_version_id`, and `module_run_id`.
- **Slug:** A unique, lowercase, kebab-case identifier for each module (e.g., `windows-autoruns`).
- **Categories:** A controlled list of categories is used to group modules (e.g., `system_inventory`, `identity`, `network_exposure`).

#### 3.16.4 Parameters and Output
- **Parameters:** Each module version has a JSON Schema that defines the parameters it accepts.
- **Output:** The output of each module run is stored in the `module_results` table in a standardized JSON format.

#### 3.16.5 Seeding and Migrations
- **Initial Load:** Modules are seeded into the database using Alembic data migrations or a deterministic seed script that reads from version-controlled fixture files (YAML or JSON).
- **Change Control:** Any change to a module requires a new Alembic data migration.

### 3.17 API Route: Billing (`/billing`)
This section covers the endpoints for managing billing plans, usage logs, and invoices, primarily for MSPs.

#### 3.17.1 File Breakdown
- **`app/routes/billing.py`**: Contains all the route handlers for the billing functionality.

#### 3.17.2 Endpoints
- **`GET /billing/plans`**: Lists all available billing plans.
- **`POST /billing/plans`**: Creates a new billing plan.
- **`GET /billing/usage`**: Lists usage logs for a tenant.
- **`POST /billing/usage`**: Creates a new usage log for a tenant.
- **`GET /billing/invoices`**: Lists invoices for a tenant.
- **`POST /billing/invoices`**: Creates a new invoice for a tenant.
- **`POST /billing/invoices/{invoice_id}/pay`**: Marks an invoice as paid.

### 3.18 API Route: Cloud (`/cloud`)
This section covers the endpoints for managing cloud accounts and assets.

#### 3.18.1 File Breakdown
- **`app/routes/cloud.py`**: Contains all the route handlers for the cloud functionality.

#### 3.18.2 Endpoints
- **`GET /cloud/accounts`**: Lists all cloud accounts for a tenant.
- **`POST /cloud/accounts`**: Creates a new cloud account for a tenant.
- **`POST /cloud/accounts/{account_id}/sync`**: Marks a cloud account as synced.
- **`GET /cloud/assets`**: Lists all cloud assets for a tenant.
- **`POST /cloud/assets`**: Creates a new cloud asset for a tenant.
- **`GET /cloud/inventory`**: Returns the cloud inventory for a tenant, including all accounts and assets.

### 3.19 API Route: Logs (`/logs`)
This section covers the endpoints for viewing backend logs.

#### 3.19.1 File Breakdown
- **`app/routes/logs.py`**: Contains all the route handlers for the logs functionality.

#### 3.19.2 Endpoints
- **`GET /logs`**: Returns the last N lines of the backend log file.

### 3.20 API Route: Telemetry (`/telemetry`)
This section covers the endpoints for ingesting web vitals telemetry data.

#### 3.20.1 File Breakdown
- **`app/routes/telemetry.py`**: Contains all the route handlers for the telemetry functionality.

#### 3.20.2 Endpoints
- **`POST /telemetry/web-vitals`**: Ingests web vitals telemetry data from the frontend.

### 3.21 API Route: Visibility (`/visibility`)
This section covers the endpoints for retrieving file and network visibility data.

#### 3.21.1 File Breakdown
- **`app/routes/visibility.py`**: Contains all the route handlers for the visibility functionality.

#### 3.21.2 Endpoints
- **`GET /visibility/files`**: Lists file visibility results.
- **`GET /visibility/network`**: Lists network visibility results.

### 3.22 API Route: Threat Intelligence (`/threat-intel`)
This section covers the endpoints for managing threat intelligence feeds and IOC hits.

#### 3.22.1 File Breakdown
- **`app/routes/threat_intel.py`**: Contains all the route handlers for the threat intelligence functionality.

#### 3.22.2 Endpoints
- **`GET /threat-intel/feeds`**: Lists all available threat intelligence feeds.
- **`POST /threat-intel/feeds`**: Creates a new threat intelligence feed.
- **`POST /threat-intel/feeds/{feed_id}/sync`**: Marks a threat intelligence feed as synced.
- **`GET /threat-intel/hits`**: Lists all IOC hits for a tenant.
- **`POST /threat-intel/hits`**: Creates a new IOC hit for a tenant.

### 3.23 API Route: Integrity (`/integrity`)
This section covers the endpoints for managing registry and boot integrity monitoring.

#### 3.23.1 File Breakdown
- **`app/routes/integrity.py`**: Contains all the route handlers for the integrity functionality.

#### 3.23.2 Endpoints
- **`GET /integrity/registry`**: Lists registry snapshots.
- **`POST /integrity/registry`**: Ingests registry snapshots and generates drift events.
- **`GET /integrity/registry/drift`**: Summarizes drift for the latest registry collection.
- **`GET /integrity/boot`**: Lists boot configurations.
- **`POST /integrity/boot`**: Ingests boot configurations and generates drift events.
- **`GET /integrity/events`**: Lists integrity events.
- **`POST /integrity/events`**: Creates a new integrity event.
- **`GET /integrity/registry/diff`**: Returns the difference between two registry snapshots.
- **`GET /integrity/services`**: Lists service snapshots.
- **`POST /integrity/services`**: Ingests service snapshots and generates drift events.
- **`GET /integrity/services/diff`**: Returns the difference between two service snapshots.
- **`GET /integrity/tasks`**: Lists task snapshots.
- **`POST /integrity/tasks`**: Ingests task snapshots and generates drift events.
- **`GET /integrity/services/baseline`**: Returns the service baseline for a tenant or agent.
- **`POST /integrity/services/baseline`**: Creates or updates the service baseline for a tenant or agent.
- **`GET /integrity/registry/baseline`**: Returns the registry baseline for a tenant or agent.
- **`POST /integrity/registry/baseline`**: Creates or updates the registry baseline for a tenant or agent.
- **`GET /integrity/tasks/baseline`**: Returns the task baseline for a tenant or agent.
- **`POST /integrity/tasks/baseline`**: Creates or updates the task baseline for a tenant or agent.

### 3.24 API Route: Processes (`/processes`)
This section covers the endpoints for managing process inventory and drift detection.

#### 3.24.1 File Breakdown
- **`app/routes/processes.py`**: Contains all the route handlers for the processes functionality.

#### 3.24.2 Endpoints
- **`GET /processes`**: Lists the latest processes for an agent.
- **`POST /processes/baseline`**: Creates or updates the process baseline for a tenant or agent.
- **`GET /processes/baseline`**: Returns the process baseline for a tenant or agent.
- **`POST /processes/report`**: Ingests a process report from an agent and generates drift events.
- **`GET /processes/drift`**: Lists process drift events.

### 3.25 API Route: Retention (`/retention`)
This section covers the endpoints for managing tenant retention policies and data export jobs.

#### 3.25.1 File Breakdown
- **`app/routes/retention.py`**: Contains all the route handlers for the retention functionality.

#### 3.25.2 Endpoints
- **`GET /retention/policy`**: Returns the retention policy for a tenant.
- **`PUT /retention/policy`**: Creates or updates the retention policy for a tenant.
- **`GET /retention/exports`**: Lists all data export jobs for a tenant.
- **`POST /retention/exports`**: Requests a new data export job for a tenant.

## 4. Frontend – Logic & UI

### 4.1 Frontend Stack & Structure
The frontend code is located in the `frontend/` directory.
- **Stack:** React 18, Vite, React Router 6, TanStack Query, Zustand, Tailwind CSS.
- **`src/`**: Contains the application source code.
    - **`main.jsx`**: The main entrypoint. It sets up the React root, providers, and router.
    - **`App.jsx`**: The root React component. It uses `useRoutes` to render the route configuration.
    - **`routes/`**: Contains the routing logic. `routeConfig.jsx` defines the application's routes, layouts, and protected areas. `PrivateRoute.jsx` implements the auth protection logic.
    - **`pages/`**: Contains the top-level components for each page/screen (e.g., `Dashboard.jsx`, `Login.jsx`).
    - **`components/`**: Contains reusable, shared components used across multiple pages.
    - **`layouts/`**: Contains layout components like `Shell.jsx`, which provides the main application frame with navigation.
    - **`store/`**: Contains the Zustand store for global client-side state management (e.g., auth state).
    - **`queries/`**: Contains TanStack React Query hooks for fetching, caching, and mutating server state.
    - **`api/`**: Contains the API client logic (using Axios) for communicating with the backend.

### 4.2 Routing & Navigation
- **Route Configuration:** Routes are defined declaratively in `frontend/src/routes/routeConfig.jsx`.
- **Protected Routes:** The `<PrivateRoute>` component wraps all routes that require authentication. It checks for the presence of an auth token in the Zustand store and redirects to `/login` if it's missing. It also supports a `requireAdmin` prop for client-side RBAC.
- **Main Routes:**
    - `/login`: Public login page.
    - `/`: The root path for the authenticated application, which renders the `ShellLayout`.
    - `/dashboard`, `/users`, `/profile`, etc.: Child routes of `/` that render specific pages within the `ShellLayout`.
- **Navigation:** The `ShellLayout` component is expected to contain the primary navigation elements (e.g., a sidebar and top bar). The links shown in the navigation would be dynamically rendered based on the user's role.

### 4.3 State Management & Data Fetching
- **API Client:** An Axios-based client in `src/api` is used for making HTTP requests. It is likely configured with a base URL from `VITE_API_URL` and an interceptor that attaches the `Authorization: Bearer <token>` header to outgoing requests.
- **Server State:** **TanStack React Query** is the primary tool for managing server state. It handles data fetching, caching, re-fetching, and optimistic updates, significantly simplifying data synchronization with the backend.
- **Client State:** **Zustand** is used for managing global client-side state, most importantly the authentication token and user profile information. This state is persisted across page loads, likely using `localStorage`.

### 4.4 Key Screens and Flows
- **Login (`/login`):** A public page with a form to submit credentials. On success, it saves the JWT from the backend and redirects to the `/dashboard`.
- **Dashboard (`/dashboard`):** The main landing page after login. It displays a high-level overview of the system's status, recent alerts, and compliance scores. It fetches data from multiple backend endpoints.
- **Users (`/users`):** An admin-only page for creating, viewing, and managing users within the tenant. It interacts with the `/admin/users` API endpoints.
- **Profile (`/profile`):** A page where users can view and edit their own profile information. It interacts with the `/users/me` API endpoints.
- **Module Catalog (`/modules`):** Displays the list of available scanning modules that can be scheduled.
- **Settings (`/admin-settings`, `/alert-settings`):** Admin-only pages for configuring various aspects of the application.

### 4.5 Frontend Styling (Facebook Theme)
The frontend implements a custom, Facebook-inspired theme to ensure a cohesive and modern user experience. The theme is defined through a set of design tokens and layout patterns documented in `docs/facebook-theme.md`.
- **Color System:** A specific color palette is defined with CSS custom properties (e.g., `--tena-primary: #1877F2`). These are aliased in Tailwind CSS for easy use (e.g., `bg-facebook-blue`).
- **Typography:** A standard font stack is used, with specific weights and sizes for headers, body copy, and muted text.
- **Layout & Spacing:** The layout is based on an 8px rhythm, with a spacing scale exposed as CSS custom properties (e.g., `--space-4` for 16px).
- **Core Components:**
    - **Header:** A Facebook-style top bar with a brand-blue background.
    - **Sidebar:** A dark slate sidebar with active items highlighted in blue.
    - **Cards:** Elevated surfaces with soft drop shadows.
    - **Buttons:** A set of buttons (primary, ghost, outline) styled to match the theme.
- **Iconography:** A set of custom SVG icons is used, located in `components/ui/Icon.jsx`.

## 5. Installation and Setup
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

## 6. Running the Application
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

## 7. Running Tests
**Backend:**
```bash
pytest backend/
```

**Frontend:**
```bash
npm test
```

## 8. CI/CD
This project uses GitHub Actions for CI/CD. The main workflows are:
- `backend-ci.yml`: Runs linting, type checking, security scans, and tests for the backend.
- `frontend-ci.yml`: Installs dependencies, runs ESLint, and builds the frontend.
- `e2e-staging.yml`: Runs end-to-end tests against a staging environment.

For more details, see the workflow files in `.github/workflows`.

## 9. Security
This section outlines the security measures in place for the Tenantra platform.

### 9.1 Authentication
Authentication is handled using JSON Web Tokens (JWT). The backend issues a short-lived access token upon successful login, which the frontend then includes in the `Authorization` header for all subsequent requests.

### 9.2 Authorization
Authorization is handled using a role-based access control (RBAC) system. The user's role is included in the JWT, and the backend uses this role to determine whether the user is authorized to perform a given action.

### 9.3 Data Isolation
Each tenant's data is isolated in the database using a separate schema for each tenant. This ensures that one tenant cannot access another tenant's data.

### 9.4 Input Validation
All user input is validated on both the frontend and the backend to prevent common security vulnerabilities such as Cross-Site Scripting (XSS) and SQL Injection.

### 9.5 Security Gaps
During the documentation review, several potential security vulnerabilities were noted:
- **Broken Access Control in `/assets` endpoint:** This endpoint leaks data across tenants.
- **Broken Access Control in `/compliance/export.*` endpoints:** These endpoints leak data across tenants.
- **Hardcoded development encryption key:** A hardcoded development encryption key in `app/core/secrets.py` could be used in production if not overridden.
