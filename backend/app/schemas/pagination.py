from pydantic import BaseModel, Field
from typing import List, TypeVar, Generic
from math import ceil

T = TypeVar('T')

class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1, description="Page number (starts from 1)")
    page_size: int = Field(default=20, ge=1, le=100, description="Number of items per page")

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total_count: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_previous: bool

    @classmethod
    def create(cls, items: List[T], total_count: int, pagination: PaginationParams):
        total_pages = ceil(total_count / pagination.page_size) if total_count > 0 else 1

        return cls(
            items=items,
            total_count=total_count,
            page=pagination.page,
            page_size=pagination.page_size,
            total_pages=total_pages,
            has_next=pagination.page < total_pages,
            has_previous=pagination.page > 1
        )