from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

import models
import schemas
from database import SessionLocal

# main app object (fast api class objectg)
app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# when app accessed, do the following function
@app.get("/")
def read_root():
    return {"status": "ok"}

@app.post("/trees", response_model=schemas.TreeRead)
def create_tree(tree: schemas.TreeCreate, db: Session = Depends(get_db)):
    db_tree = models.Tree(**tree.model_dump())
    db.add(db_tree)
    db.commit()
    db.refresh(db_tree)
    return db_tree


@app.get("/trees", response_model=list[schemas.TreeRead])
def list_trees(db: Session = Depends(get_db)):
    return db.query(models.Tree).all()