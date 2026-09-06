"""
Common Pydantic v2 Schemas & Base DTOs.
Provides shared types, epistemic tier enums, base request/response configurations,
standardized error envelopes, and pagination models.
"""
from __future__ import annotations

from enum import Enum
from typing import Any, Dict, Generic, List, Literal, Optional, TypeVar
import uuid

from pydantic import BaseModel, ConfigDict, Field


class EpistemicTier(str, Enum):
    """
    The 6-Tier Epistemic Hierarchy governing DecisionSphere data artifacts.
    Enforces strict distinction between historical fact, model inference,
    operational bridge, accounting calculation, and strategic advisory.
    """
    OBSERVED = "OBSERVED"        # Historical ground truth from source datasets
    PREDICTED = "PREDICTED"      # Machine learning conditional inferences P(Y|X)
    ASSUMED = "ASSUMED"          # User-specified scenario shock parameters & policy constants
    PROPAGATED = "PROPAGATED"    # Algorithmic cross-domain bridges (overtime mapping, volume scaling)
    CALCULATED = "CALCULATED"    # Deterministic mathematical accounting equations
    RECOMMENDED = "RECOMMENDED"  # Prioritized rule-grounded strategic actions


class BaseSchema(BaseModel):
    """
    Base response schema configured for SQLAlchemy ORM compatibility.
    Allows seamless transformation from ORM models via model_validate().
    """
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )


class BaseRequest(BaseModel):
    """
    Base request schema enforcing Gate E: API Schema Validation.
    Rejects any extraneous/rogue attributes via extra="forbid".
    """
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )


class APIErrorDetail(BaseModel):
    """Field-level error descriptor."""
    model_config = ConfigDict(extra="forbid")

    loc: List[str] = Field(default_factory=list, description="Error location path")
    msg: str = Field(..., description="Error message")
    type: str = Field(..., description="Error classification type")


class ErrorResponse(BaseModel):
    """
    Standardized application error contract matching Gate 9.0.h.
    Guaranteed structure for all 4xx/5xx responses.
    """
    model_config = ConfigDict(extra="forbid")

    error_code: str = Field(..., description="Machine-readable snake_case or SCREAMING_SNAKE error code")
    message: str = Field(..., description="Human-readable explanation of failure")
    details: Optional[Any] = Field(None, description="Optional diagnostic details or validation errors")
    request_id: Optional[str] = Field(None, description="Correlation identifier for traceability")


T = TypeVar("T")


class PaginatedResponse(BaseSchema, Generic[T]):
    """Generic pagination wrapper for list endpoints."""
    items: List[T] = Field(..., description="List of items for current page")
    total: int = Field(..., ge=0, description="Total count of items across all pages")
    page: int = Field(default=1, ge=1, description="Current page number (1-indexed)")
    page_size: int = Field(default=20, ge=1, description="Items per page")
    total_pages: int = Field(default=1, ge=0, description="Total number of pages")
    skip: Optional[int] = Field(default=None, description="Offset for pagination")
    limit: Optional[int] = Field(default=None, description="Page limit")

    @classmethod
    def create(
        cls,
        items: List[T],
        total: int,
        skip: int = 0,
        limit: int = 50,
    ) -> "PaginatedResponse[T]":
        page_size = max(limit, 1)
        page = (skip // page_size) + 1
        total_pages = (total + page_size - 1) // page_size if total > 0 else 0
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            skip=skip,
            limit=limit,
        )
