# Tenantra Sprint-Ready Task List

**IMPORTANT:** At the end of each sprint, ensure `docs/Tenantra_Master_Brain_v1.0.md` is updated with all relevant details.
**IMPORTANT:** when you done you should rebuild all containers by using option 1 or option 6 (with no cash ) form @tenantra_control_menu.sh check if there is any error during the budling or in the containers, if everything ok perform the test for this sprint  
**IMPORTANT:** after you done and everything is green commit theses changes with corresponding comment to this Sprint  and changes and update @/docs/Tenantra_Master_Brain_v1.0.md with these changes up on the corresponding section for each change  
**IMPORTANT:** **Output Format Requirements**
   * **Do NOT print your full reasoning or file content.**
   * **Do NOT produce large text dumps while analyzing.**
   * **Do NOT echo back the project documents.**
   * **Only output the final sprint task list summary**, not the full analysis.
   
**IMPORTANT:** 
  **Final Output Rule**

   * Only show a **short summary of sprints and epics** on screen. 
   
This document organizes all development tasks into focused sprints to provide a clear roadmap for improving the Tenantra application.


## EPIC: Identity & Tenant Onboarding & Security Hardening

### Sprint 1: Foundational Security & User Lifecycle

#### Sprint Analysis
*   **Impact:** This sprint is critical and will have a widespread impact on the application's core. Fixing tenant isolation will alter the data access layer for the entire backend. Implementing email services and authentication flows will change the user onboarding and login experience. All subsequent features that handle data will depend on the correctness of the security fixes in this sprint.
*   **Needs:** A fully configured and accessible email service (e.g., SMTP server credentials or a third-party API key like SendGrid) is a hard dependency. This must be available as a secret/environment variable for the backend.
*   **Considerations:**
    *   **Security:** The tenant isolation fix is the highest priority. It requires a meticulous audit of every database query to ensure a `tenant_id` filter is applied everywhere. Failure to do so leaves the entire platform's data exposed. For password resets, use short-lived, single-use, cryptographically secure tokens.
    *   **User Experience:** The signup and password reset flows should be seamless. Provide clear feedback to the user (e.g., "A password reset link has been sent to your email").
    *   **Testing:** Rigorous integration and end-to-end tests are required to validate tenant isolation. These tests must simulate multiple tenants and users trying to access each other's data.
*   **Preferable to Have (Nice-to-Haves):**
    *   **Audit Trails:** Log security-sensitive events like password resets, failed login attempts, and tenant join requests.
    *   **Branded Emails:** Use HTML templates for emails to provide a professional and consistent user experience.
    *   **Role-Based Approval:** For the "Join Tenant" feature, allow different roles (e.g., Admin, Owner) to approve requests.

---

*   **Task: [Security-1.1] Fix Broken Tenant Isolation**
    *   **Objective:** Ensure users can only see data belonging to their own tenant.
    *   **Acceptance Criteria:**
        1.  A new user account associated with "Tenant A" CANNOT see "Default Tenant" or "All Tenants" options unless explicitly granted.
        2.  All API endpoints that return lists of resources (assets, users, etc.) are strictly filtered by the authenticated user's `tenant_id`.
        3.  A full audit of the backend repository/data access layer is completed to ensure queries are tenant-aware.
    *   **Dependencies:** None.
    *   **Impacted Areas:**
        *   `backend/app/repositories/*` (All repository files)
        *   `backend/app/core/dependencies.py` (Update auth/dependency logic)
        *   `backend/tests/test_access_control.py` (New tests)
    *   **Labels:** Backend, Security, Critical
    *   **Test Scenarios:**
        1.  **Positive Case:** Log in as User A in Tenant A. Call list endpoints for `/assets`, `/users`, and `/agents`. Verify that only resources associated with Tenant A are returned.
        2.  **Negative Case (IDOR):** As User A (Tenant A), attempt to directly access a resource from Tenant B via its ID (e.g., `/api/v1/assets/{tenant_b_asset_id}`). Verify a 403 Forbidden or 404 Not Found error is returned.
        3.  **Cross-Tenant Creation:** As User A (Tenant A), attempt to create a new resource (e.g., a new user) with a `tenant_id` belonging to Tenant B. The backend should ignore the request body's `tenant_id` and assign the new resource to Tenant A.
        4.  **Admin View (Optional):** If a super-admin role exists, verify they can see resources across all tenants when no specific tenant filter is applied.

*   **Task: [Identity-1.1] Implement "Forgot Password" Flow**
    *   **Objective:** Allow users to securely reset their password.
    *   **Acceptance Criteria:**
        1.  User clicks "Forgot Password" on the login page.
        2.  User enters their email and receives a password reset link.
        3.  The link directs to a secure page to enter a new password.
        4.  Password is updated, and the user can log in with the new credentials.
    *   **Dependencies:** Email service configuration (SMTP/API).
    *   **Impacted Areas:**
        *   `frontend/src/pages/Login.jsx`
        *   `frontend/src/pages/ResetPassword.jsx` (New)
        *   `backend/app/api/v1/auth.py` (New endpoints)
        *   `backend/app/services/email_service.py` (New)
    *   **Labels:** Backend, Frontend, Security
    *   **Test Scenarios:**
        1.  **Happy Path:** User enters a valid, existing email. They receive an email and use the link to successfully reset their password.
        2.  **Non-Existent Email:** User enters an email address not associated with any account. The UI shows a generic success message to prevent user enumeration, and no email is sent.
        3.  **Expired Token:** User waits longer than the token's expiry time and then clicks the reset link. They should be shown an "expired link" error and prompted to start the process again.
        4.  **Token Reuse:** User successfully resets their password, then attempts to use the same reset link again. The link should now be invalid.

*   **Task: [Identity-1.2] Implement Signup Email Verification & Welcome Email**
    *   **Objective:** Verify new user emails and send a welcome message upon successful registration.
    *   **Acceptance Criteria:**
        1.  Upon signup, a verification email is sent to the user's address.
        2.  User must click the link to activate their account.
        3.  After verification, a welcome email is sent.
    *   **Dependencies:** Email service configuration.
    *   **Impacted Areas:**
        *   `backend/app/api/v1/users.py`
        *   `backend/app/services/email_service.py`
    *   **Labels:** Backend
    *   **Test Scenarios:**
        1.  **Happy Path:** A new user signs up, receives the verification email, clicks the link, and their account becomes active. They can then log in successfully. A welcome email is also received.
        2.  **Login Before Verification:** A new user signs up but tries to log in before clicking the verification link. The login attempt must fail with a clear "account not verified" error message.
        3.  **Resend Verification:** The UI should provide an option for a user to request a new verification email if they did not receive the first one.
        4.  **Invalid Verification Link:** A user attempts to visit a malformed or fake verification URL. The activation must fail.

*   **Task: [Identity-1.3] Add UI/API to Join an Existing Tenant**
    *   **Objective:** Enable users to request access to join an existing tenant organization.
    *   **Acceptance Criteria:**
        1.  A new option on the signup or dashboard page allows users to "Join a Tenant".
        2.  User can search for a tenant (by name or ID) and submit a request.
        3.  Tenant administrators can approve or deny join requests from a new management UI.
    *   **Dependencies:** None.
    *   **Impacted Areas:**
        *   `frontend/src/pages/Signup.jsx`
        *   `frontend/src/components/TenantJoinForm.jsx` (New)
        *   `backend/app/api/v1/tenants.py` (New endpoints)
    *   **Labels:** Backend, Frontend
    *   **Test Scenarios:**
        1.  **Request:** A user successfully submits a request to join an existing tenant. The tenant admin sees a notification or a new item in a "Pending Requests" list.
        2.  **Approval:** The tenant admin approves the request. The user is added to the tenant and can now log in and access that tenant's resources.
        3.  **Denial:** The tenant admin denies the request. The user is not added to the tenant, and the pending request is removed.
        4.  **Duplicate Request:** A user who already has a pending request tries to submit another request to the same tenant. The UI should prevent this and indicate a request is already pending.

## EPIC: Agent Architecture & Network Discovery

### Sprint 2: Agent Management Foundation

#### Sprint Analysis
*   **Impact:** This sprint introduces a foundational piece of the Tenantra platform: the agent management system. It will create a new major UI section and require new, secure backend endpoints for agent communication. The Docker configuration changes will affect how the application is deployed and how it interacts with the host system's network.
*   **Needs:**
    *   **Agent Authentication Strategy:** A decision must be made on how agents will securely authenticate with the backend. A tenant-specific, revocable registration token is a common and secure pattern.
    *   **Agent Packaging:** Tooling and scripts will be needed to build the agent for different target operating systems (`.deb`, `.rpm`, `.msi`). This may require a separate build pipeline.
*   **Considerations:**
    *   **Security:** The agent-to-backend communication channel must be encrypted (HTTPS). The agent registration process must be secure to prevent unauthorized agents from connecting. Granting agents host network access is a security-sensitive operation and should be disabled by default and only enabled when explicitly needed for network discovery.
    *   **Scalability:** The agent management API should be designed to handle thousands of agents checking in. The agent status (online/offline) will likely require a caching layer (like Redis) or a heartbeat mechanism to avoid overwhelming the database.
    *   **Documentation:** The agent setup guide must be extremely clear, as it will be followed by system administrators on a variety of systems.
*   **Preferable to Have (Nice-to-Haves):**
    *   **One-Click Install Scripts:** Provide a copy-paste shell or PowerShell script that includes the tenant's registration token to automate the download and installation process.
    *   **Agent Groups:** Allow users to group agents (e.g., by location, environment) for easier management and task assignment.
    *   **Bulk Actions:** In the UI, allow for approving or deleting multiple agents at once.

---

*   **Task: [Agent-2.1] Create Agent Installation Documentation & Download Page**
    *   **Objective:** Provide clear instructions and a mechanism for users to install agents.
    *   **Acceptance Criteria:**
        1.  A new page in the frontend UI is created for agent management.
        2.  This page provides download links for agent packages (e.g., `.deb`, `.rpm`, `.msi`).
        3.  A clear, step-by-step guide for installation and configuration on different OSes is available.
    *   **Dependencies:** None.
    *   **Impacted Areas:**
        *   `frontend/src/pages/Agents.jsx` (New)
        *   `docs/AGENT_SETUP.md` (New)
    *   **Labels:** Frontend, DevOps, Documentation
    *   **Test Scenarios:**
        1.  **UI Navigation:** A user can navigate to the "Agent Management" page from the main dashboard.
        2.  **Content Verification:** The page correctly displays download links and a summary of the installation instructions.
        3.  **Documentation Review:** A team member reviews the `AGENT_SETUP.md` file for clarity, accuracy, and completeness for both Windows and Linux instructions.

*   **Task: [Agent-2.2] Implement Agent Management UI/API**
    *   **Objective:** Allow users to view, manage, and task agents.
    *   **Acceptance Criteria:**
        1.  The new "Agents" page lists all registered agents for the tenant.
        2.  The list shows agent status (online/offline), OS, version, and last check-in time.
        3.  Users can approve new agent registrations.
        4.  Users can assign tasks or discovery scans to specific agents (initial design).
    *   **Dependencies:** [Agent-2.1]
    *   **Impacted Areas:**
        *   `frontend/src/pages/Agents.jsx`
        *   `backend/app/api/v1/agents.py` (New)
        *   `backend/app/models/agent.py` (New or expanded)
    *   **Labels:** Backend, Frontend
    *   **Test Scenarios:**
        1.  **Agent Registration:** A newly installed agent using a valid tenant token appears in the UI with a "Pending Approval" status.
        2.  **Agent Approval:** An admin approves the agent, and its status changes to "Online". The agent can now receive tasks.
        3.  **Agent Rejection:** An admin rejects a pending agent. The agent is removed from the list and cannot communicate with the backend.
        4.  **Agent Heartbeat:** An online agent is shut down. After a configured timeout period, its status in the UI changes to "Offline".
        5.  **Cross-Tenant View:** Log in as a user in Tenant A and verify you cannot see any agents registered to Tenant B.

*   **Task: [Agent-2.3] Configure Agent for Host Network Discovery**
    *   **Objective:** Allow the agent's discovery module to scan the host's local network, not just the container network.
    *   **Acceptance Criteria:**
        1.  The Docker configuration for the agent service is updated to allow host network access.
        2.  The network discovery module can successfully identify other devices on the same physical LAN as the host machine.
    *   **Dependencies:** None.
    *   **Impacted Areas:**
        *   `docker/docker-compose.yml` (Or relevant agent compose file)
    *   **Labels:** DevOps, Networking
    *   **Test Scenarios:**
        1.  **Host Network Enabled:** Deploy an agent with host networking enabled. Run a network discovery scan. Verify the results include other physical devices on the host's LAN.
        2.  **Host Network Disabled:** Deploy an agent with default bridge networking. Run a network discovery scan. Verify the results only include other containers on the same Docker network, not devices on the physical LAN.

## EPIC: Asset Inventory & Module Catalog

### Sprint 3: Data Visibility & Integrity

#### Sprint Analysis
*   **Impact:** This sprint delivers the first major return on investment for the agent deployment: a visible inventory of discovered assets. It also involves a critical refactoring of the module system, which is central to the platform's scanning capabilities. This will impact how scans are defined, executed, and updated.
*   **Needs:**
    *   **Functional Agents:** Agents must be capable of running basic discovery scans and reporting their findings to the backend.
    *   **Finalized DB Schema:** The database schemas for `assets`, `modules`, and `module_versions` must be finalized and migrated before development begins.
*   **Considerations:**
    *   **Performance:** The Asset Inventory page could potentially display thousands of items. The backend API must be highly performant, using efficient pagination. The frontend must use virtualized lists or other techniques to avoid rendering lag.
    *   **Data Normalization:** Asset data coming from different agents and OS types may be inconsistent. A normalization layer in the backend is needed to ensure data is stored and displayed uniformly.
    *   **Refactoring Risk:** The module catalog refactoring is a high-risk change. It must be developed with a full suite of regression tests to ensure that existing scanning capabilities are not broken. The database seeding script must be idempotent.
*   **Preferable to Have (Nice-to-Haves):**
    *   **Asset Tagging:** Allow users to apply custom tags to assets for better organization and filtering.
    *   **Export to CSV:** Add a button to the Asset Inventory page to export the current view as a CSV file.
    *   **Module Versioning UI:** A simple UI to view different versions of a module and their changelogs.

---

*   **Task: [Asset-3.1] Create UI to View and Manage Discovered Assets**
    *   **Objective:** Provide a user interface for viewing all assets discovered by agents.
    *   **Acceptance Criteria:**
        1.  A new "Asset Inventory" page is created in the frontend.
        2.  The page displays a filterable, sortable table of all discovered assets (e.g., servers, endpoints).
        3.  Columns include hostname, IP address, OS, MAC address, and discovery source (agent name).
        4.  Clicking an asset shows a detailed view with all collected information.
    *   **Dependencies:** Agent discovery tasks must be functional.
    *   **Impacted Areas:**
        *   `frontend/src/pages/AssetInventory.jsx` (New)
        *   `frontend/src/components/AssetTable.jsx` (New)
        *   `backend/app/api/v1/assets.py` (New)
    *   **Labels:** Backend, Frontend
    *   **Test Scenarios:**
        1.  **Display Assets:** An agent discovers 5 assets. The Asset Inventory page correctly loads and displays these 5 assets in the table.
        2.  **Filtering:** The user types "Windows" into a filter box for the OS column. The table updates to show only assets with "Windows" as their OS.
        3.  **Sorting:** The user clicks the header for the "Hostname" column. The table sorts the assets alphabetically by hostname. Clicking again sorts in reverse order.
        4.  **Pagination:** With 50 discovered assets and a page size of 20, verify that the table shows 3 pages and the navigation controls work correctly.
        5.  **Detailed View:** Clicking on a specific asset opens a side panel or a new page showing all data collected for that asset.

*   **Task: [Module-3.1] Refactor Module Catalog to Load from Database**
    *   **Objective:** Ensure the module catalog is dynamic and sourced from the database, not hardcoded or from files.
    *   **Acceptance Criteria:**
        1.  The backend service responsible for providing the module catalog reads directly from the `modules` and `module_versions` tables.
        2.  Any file-based module loading (`.csv`, `.json`) is removed from the runtime application code.
        3.  A database seeding script is created or updated to populate the initial module catalog.
    *   **Dependencies:** Database schema for modules must exist.
    *   **Impacted Areas:**
        *   `backend/app/services/module_catalog.py` (Refactor)
        *   `backend/app/api/v1/modules.py` (Refactor)
        *   `scripts/db_seed.py`
    *   **Labels:** Backend, Refactor
    *   **Test Scenarios:**
        1.  **DB Loading:** The application starts, and the `/api/v1/modules` endpoint returns the exact list of modules populated by the `db_seed.py` script.
        2.  **Dynamic Update:** Manually add a new module row to the database. Calling the API endpoint again should immediately reflect this new module without an application restart.
        3.  **Regression Test:** A core function that relies on the module catalog (e.g., assigning a scan to an agent) continues to work correctly after the refactoring.
        4.  **Empty Catalog:** If the modules table is empty, the API should return an empty list `[]` and not crash.

*   **Task: [Module-3.2] Investigate and Define Persistence & Integrity Logic**
    *   **Objective:** Clarify and document the sources and logic for process monitoring and file integrity drift detection.
    *   **Acceptance Criteria:**
        1.  A technical document is produced defining the "golden sources" for integrity checks.
        2.  The logic for detecting drift (e.g., hashing, timestamp comparison) is clearly specified.
        3.  An API endpoint is designed to provide agents with the necessary tenant-specific configuration for these checks.
    *   **Dependencies:** None.
    *   **Impacted Areas:**
        *   `docs/modules/INTEGRITY_MONITORING.md` (New)
        *   `backend/app/api/v1/agents.py`
    *   **Labels:** Backend, Architecture, Documentation
    *   **Test Scenarios:**
        1.  **Document Review:** A senior developer or architect reviews the created `INTEGRITY_MONITORING.md` document for technical soundness, clarity, and completeness.
        2.  **API Spec:** The OpenAPI/Swagger documentation is updated with the new proposed API endpoint for agent configuration, and it is reviewed for correctness.

## EPIC: Grafana & Observability

### Sprint 4: Dashboarding & Monitoring

#### Sprint Analysis
*   **Impact:** This sprint directly affects the operations and monitoring capabilities of the platform. A functional Grafana dashboard is key for visualizing system health and performance metrics, which is crucial for both developers and administrators.
*   **Needs:**
    *   **Access:** Developer access to the Grafana instance, its logs, and its configuration files is required.
    *   **Data Knowledge:** A clear understanding of the metrics being collected in Prometheus and the data structure Grafana expects is necessary.
*   **Considerations:**
    *   **Root Cause Analysis:** The `HTTP 422 Unprocessable Entity` error in Grafana often points to a mismatch between what the Grafana query editor sends and what the data source backend can process. This could be a syntax error in a PromQL query, a problem with a dashboard variable, or a bug in the Grafana-Prometheus plugin. The investigation should start by inspecting the network requests in the browser's developer tools and checking the Grafana server logs for more detailed error messages.
    *   **Provisioning:** The fix should ideally be applied to the provisioned dashboard files (`docker/grafana-provisioning/dashboards/`) so that it persists across deployments.
*   **Preferable to Have (Nice-to-Haves):**
    *   **Health Check Dashboard:** Create a new, simple Grafana dashboard that visualizes the health and status of all Tenantra microservices (backend, frontend, database, etc.).
    *   **Alerting Rules:** Configure basic alerting rules in Prometheus/Grafana for critical events, such as a service being down or high API error rates.
    *   **Runbook Update:** Extensively document the cause and solution for the 422 error in `docs/RUNBOOK.md` to speed up future troubleshooting.

---

*   **Task: [Grafana-4.1] Investigate and Fix Grafana Dashboard 422 Error**
    *   **Objective:** Resolve the `HTTP 422 loadDashboardScene` error in Grafana.
    *   **Acceptance Criteria:**
        1.  Root cause of the 422 error is identified (e.g., malformed query, data source issue, provisioning error).
        2.  The issue is fixed, and the Grafana dashboard loads correctly with data.
        3.  The fix is documented.
    *   **Dependencies:** None.
    *   **Impacted Areas:**
        *   `docker/grafana-provisioning/dashboards/`
        *   `docker/prometheus/prometheus.yml`
        *   `docs/RUNBOOK.md` (Add troubleshooting section)
    *   **Labels:** DevOps, Observability
    *   **Test Scenarios:**
        1.  **Dashboard Loading:** Navigate to the primary Grafana dashboard. Verify it loads within 10 seconds and shows no 422 errors or panel-specific errors.
        2.  **Data Presence:** Verify that at least one panel on the dashboard is populated with current data from Prometheus (i.e., not showing "N/A" or "No Data").
        3.  **Persistence:** Run `docker-compose down` and `docker-compose up` to completely restart the stack. Verify that the Grafana dashboard fix persists and the dashboard still loads correctly.
        4.  **Cross-Browser Check:** Load the dashboard in two different browsers (e.g., Chrome and Firefox) to ensure the fix is not browser-specific.
