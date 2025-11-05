# backend/app/seed.py
import importlib, sys

def main() -> int:
    try:
        mod = importlib.import_module("app.scripts.db_seed")
    except ModuleNotFoundError:
        try:
            mod = importlib.import_module("scripts.db_seed")
        except ModuleNotFoundError:
            print("ERROR: Could not find seeder module app.scripts.db_seed or scripts.db_seed", file=sys.stderr)
            return 1
    for fn in ("main","run","seed"):
        if hasattr(mod, fn):
            rv = getattr(mod, fn)()
            return int(rv or 0)
    print("ERROR: Seeder module has no main()/run()/seed()", file=sys.stderr)
    return 1

if __name__ == "__main__":
    sys.exit(main())
