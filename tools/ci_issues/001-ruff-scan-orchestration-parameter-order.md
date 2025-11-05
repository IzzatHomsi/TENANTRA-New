Ruff lint failure: invalid-syntax in `app/routes/scan_orchestration.py`

Summary:
- Error: "Parameter without a default cannot follow a parameter with a default"
- File: `app/routes/scan_orchestration.py`, line ~102
- CI run: 18754724333

Details:
Ruff reported a function signature where a parameter with no default (`payload: ScanResultCreate`) follows a parameter with a default (`job_id: int = Path(...)`). In Python, non-default parameters must come before parameters with defaults. This likely happened because framework-annotated dependencies (FastAPI `Path`, `Query`, `Depends`) were mixed in a way that violates normal parameter ordering.

Suggested fixes:
- Move required parameters (without default) before parameters with defaults.
- Reorder the signature to follow FastAPI patterns, or annotate optional parameters as Optional[...] with a default.

Next steps:
- Edit `app/routes/scan_orchestration.py` to reorder parameters in the `add_result` function so non-default parameters precede defaults.
- Add a unit test if possible to cover the route signature.
