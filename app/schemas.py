from pydantic import BaseModel


class AuthorBase(BaseModel):
    name: str

class AuthorCreate(AuthorBase):
    pass

class Author(AuthorBase):
    id: int

    class Config:
        orm_mode: True

class BookBase(BaseModel):
    title: str

class BookCreate(BookBase):
    author: AuthorBase

    class Config:
        extra = 'forbid'

class Book(BookBase):
    id: int
    author: Author
    author_id: int

    class Config:
        orm_mode: True
        extra = 'forbid'
