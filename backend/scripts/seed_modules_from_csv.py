import csv
from pathlib import Path
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.module import Module


CSV_PATHS = [
    Path('docs/modules/Tenantra_Module_Backlog_PhaseLinked_v8.csv'),
    Path('docs/modules/Tenantra_Scanning_Module_Table_v2_UPDATED.csv'),
]


def seed_modules_from_csv(db: Session) -> int:
    if db.query(Module).count() > 0:
        return 0
    path = next((p for p in CSV_PATHS if p.exists()), None)
    if not path:
        return 0
    added = 0
    with path.open('r', encoding='utf-8', errors='ignore') as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = (row.get('name') or row.get('Name') or '').strip()
            if not name:
                continue
            if db.query(Module).filter(Module.name == name).first():
                continue
            m = Module(
                name=name,
                category=(row.get('category') or row.get('Category') or None),
                phase=int(row['phase']) if (row.get('phase') or '').isdigit() else None,
                description=row.get('description') or None,
                external_id=row.get('external_id') or None,
                impact_level=row.get('impact_level') or None,
                path=row.get('path') or None,
                status=row.get('status') or None,
            )
            db.add(m)
            added += 1
        db.commit()
    return added


def main():
    db = SessionLocal()
    try:
        n = seed_modules_from_csv(db)
        print(f"Seeded {n} modules from CSV")
    finally:
        db.close()


if __name__ == '__main__':
    main()

