#main.py

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

import crud, models, schemas
from database import SessionLocal, engine
import os

if not os.path.exists('.\sqlitedb'):
    os.makedirs('.\sqlitedb')

# create tables in database 'sqlitedata.db' (check datapase.py database-URL)
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency (to create a new database session for each request)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create user with email
@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    # Als user al bestaat, geef foutmelding
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    # Geef user terug
    return crud.create_user(db=db, user=user)

# GET alle users en hun info
@app.get("/users/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

# GET user by id opvragen
@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

# Create item (with user id)
@app.post("/users/{user_id}/items/", response_model=schemas.Item)
def create_item_for_user(user_id: int, item: schemas.ItemCreate, db: Session = Depends(get_db)):
    all_items = crud.get_items(db)
    for existing_item in all_items:
        if existing_item.title == item.title:
            raise HTTPException(status_code=400, detail="Item already exists")

    return crud.create_user_item(db=db, item=item, user_id=user_id)

# GET all items zonder users
@app.get("/items/", response_model=list[schemas.Item])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_items(db, skip=skip, limit=limit)
    return items