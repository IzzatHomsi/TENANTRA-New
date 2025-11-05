<!-- PR template for Tenantra Platform -->
# Summary

Describe the change and why it was made.

# Checklist

Use this checklist to help reviewers verify important repo conventions. The full reviewer checklist is in `.github/PR_REVIEW_CHECKLIST.md`.

- [ ] Alembic/migrations checked (see `tools/verify_alembic_single_head.py`)
- [ ] Seeds added/updated and idempotent (`backend/scripts/db_seed.py` pattern)
- [ ] Tenant-awareness verified (use `tenant_id` query or `X-Tenant-Slug` header)
- [ ] Tests added/updated (unit/integration + e2e if needed)
- [ ] No secrets committed; env vars documented in `DEPLOY.md`

## Notes for reviewers

Link to extended Copilot guidance: `.github/copilot-instructions.md`.
