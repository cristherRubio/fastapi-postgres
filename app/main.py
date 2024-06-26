from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from . import models, schemas  # Import SQLAlchemy models


DATABASE_URL = "postgresql://admin:something1@db:5432/booksdb"

# SQLAlchemy setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# API Endpoints
@app.post("/books/", response_model=schemas.Book)
def create_book(book: schemas.BookCreate, db: Session = Depends(get_db)):

    db_author = db.query(models.Author).filter(models.Author.name == book.author.name).first()
    if not db_author:
        author_create = schemas.AuthorCreate(name=book.author.name)
        db_author = models.Author(**author_create.model_dump())
        db.add(db_author)
        db.commit()
        db.refresh(db_author)

    db_book = db.query(models.Book).filter(models.Book.title == book.title, models.Book.author_id == db_author.id).first()
    if db_book:
        raise HTTPException(status_code=400, detail="Book already exists")
    
    new_book = models.Book(title=book.title, author_id=db_author.id)
    db.add(new_book)
    db.commit()
    db.refresh(new_book)

    return new_book


@app.get("/books/", response_model=list[schemas.Book])
def read_books(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    books = db.query(models.Book).offset(skip).limit(limit).all()
    return books


@app.get("/authors/", response_model=list[schemas.Author])
def read_authors(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    authors = db.query(models.Author).offset(skip).limit(limit).all()
    return authors