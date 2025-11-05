Seed step: success

Summary:
- CI run 18754724333 ran `python scripts/db_seed.py` and printed "Seed complete.".
- The Verify step confirmed `roles` table exists prior to seeding.

Notes:
- The seed step executed after alembic migrations succeeded (T_012 applied).
- db_seed.py was updated in the repo to attempt `alembic upgrade head` before seeding and to raise clearer errors if DB queries fail.

Action items (optional):
- Consider adding a CI test that validates the seed process in a disposable DB instance.
