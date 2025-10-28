from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class TransactionType(str, Enum):
    """Allowed transaction types."""

    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"


class Transaction(BaseModel):
    """Representation of a stored transaction."""

    id: str
    account_id: str
    type: TransactionType
    amount: float
    description: Optional[str]
    timestamp: datetime
