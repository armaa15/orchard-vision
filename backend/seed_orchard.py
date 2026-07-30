from database import SessionLocal
import models

db = SessionLocal()

orchard = models.Orchard(name="Home orchard")
db.add(orchard)
db.commit()
db.refresh(orchard)

print(f"Created orchard with id {orchard.id}")

db.close()