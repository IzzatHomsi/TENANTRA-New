# Frontend State Architecture

Tenantra now centralises shared UI state via Zustand with runtime validation powered by Zod.

## Store

- `frontend/src/store/uiStore.ts` holds tenant selection, tenant lists, and feature flags.
- The store is persisted to `localStorage` under `tena-ui-store`, replacing ad-hoc key usage for `tenant_id`/`tenant_name` while keeping backward compatibility.

## Fetch Utilities

- `frontend/src/lib/apiClient.ts` wraps `fetch` with Zod validation and consistent error handling.
- `frontend/src/api/features.ts` and `frontend/src/api/tenants.ts` load feature flags and tenants, update the Zustand store, and normalise payload shapes.

## Component Changes

- `layouts/Shell.jsx` consumes the store for tenant switching and feature toggles (React Query still manages server caching).
- Admin experiences such as `FeatureFlags`, `Users`, `ScheduleModule`, and discovery schedules reuse the shared tenant list via the store instead of fetching repeatedly.

## Next Steps

- Gradually migrate other API calls to `apiFetch` + Zod schemas to ensure type-safe responses.
- When adding new global UI state (e.g., toast queues, debug flags), prefer the central Zustand store to avoid scattered `localStorage` mutations.
