from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware

import models
import schemas
from database import SessionLocal
from database import engine
models.Base.metadata.create_all(bind=engine)

# main app object (fast api class objectg)
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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