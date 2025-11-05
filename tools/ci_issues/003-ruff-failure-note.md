Ruff prevented subsequent checks from running

Summary:
- The Ruff step failed with one error (invalid function parameter ordering) and caused the job to exit before Mypy, Bandit, and Pytest steps could run.
- File: `app/routes/scan_orchestration.py` -- the `add_result` route function signature needs reordering.

Suggested next steps:
- Fix the function signature.
- Re-run CI to surface any further issues in mypy/bandit/pytest.
