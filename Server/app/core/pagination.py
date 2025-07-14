from typing import Generic, TypeVar, List, Optional
from pydantic import BaseModel, field_validator
from math import ceil

T = TypeVar('T')


class PaginationParams(BaseModel):
    """Parameters for pagination requests with strict validation."""
    
    page: int = 1
    size: int = 10

    @classmethod
    def validate_page(cls, v: int) -> int:
        if v < 1:
            raise ValueError("page must be >= 1")
        return v

    @classmethod
    def validate_size(cls, v: int) -> int:
        if v < 1:
            raise ValueError("size must be >= 1")
        if v > 100:
            raise ValueError("size must be <= 100")
        return v

    # Pydantic v2 field validators
    model_config = {"validate_default": True}

    # Use pydantic v2 field_validator decorator
    @field_validator("page", mode="before")
    @classmethod
    def _page_validator(cls, v):
        return cls.validate_page(v)

    @field_validator("size", mode="before")
    @classmethod
    def _size_validator(cls, v):
        return cls.validate_size(v)
    
    @property
    def offset(self) -> int:
        return (self.page - 1) * self.size
    
    @property
    def limit(self) -> int:
        return self.size


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response model."""
    
    items: List[T]
    total: int
    page: int
    size: int
    pages: int
    has_next: bool
    has_prev: bool
    
    @classmethod
    def create(
        cls,
        items: List[T],
        total: int,
        page: int,
        size: int
    ) -> "PaginatedResponse[T]":
        """Create a paginated response."""
        pages = ceil(total / size) if size > 0 else 0
        
        return cls(
            items=items,
            total=total,
            page=page,
            size=size,
            pages=pages,
            has_next=page < pages,
            has_prev=page > 1
        )

    # Compatibility alias used by some tests
    @property
    def has_previous(self) -> bool:  # pragma: no cover
        return self.has_prev


def paginate_query(query, params: "PaginationParams") -> PaginatedResponse:
    """Paginate a SQLAlchemy query and return a PaginatedResponse instance."""

    offset = params.offset
    limit = params.limit

    total = query.count()
    items = query.offset(offset).limit(limit).all()
    
    return PaginatedResponse.create(
        items=items,
        total=total,
        page=params.page,
        size=params.size,
    )