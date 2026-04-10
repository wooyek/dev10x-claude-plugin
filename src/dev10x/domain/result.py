from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar

T = TypeVar("T")


@dataclass(frozen=True)
class SuccessResult(Generic[T]):
    value: T

    def to_dict(self) -> dict[str, Any]:
        if isinstance(self.value, dict):
            return self.value
        return {"value": self.value}


@dataclass(frozen=True)
class ErrorResult:
    error: str
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {"error": self.error}
        result.update(self.details)
        return result


Result = SuccessResult[T] | ErrorResult


def ok(value: T) -> SuccessResult[T]:
    return SuccessResult(value=value)


def err(
    error: str,
    **details: Any,
) -> ErrorResult:
    return ErrorResult(error=error, details=details)
