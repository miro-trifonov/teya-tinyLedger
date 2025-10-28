from __future__ import annotations
from typing import List

from fastapi import FastAPI, HTTPException, APIRouter, status
from pydantic import BaseModel

from .schemas import Transaction, TransactionType
from .tinyLedger import InsufficientFundsError, LedgerService


class TransactionRequest(BaseModel):
    amount: float
    type: TransactionType  # "deposit"/"withdrawal"
    description: str | None = None


class TransactionResponse(BaseModel):
    message: str


class BalanceResponse(BaseModel):
    balance: float


class LedgerHandler:
    """Public facing API handler to provide access to ledger operations.
    Provides endpoints to create transactions, view balance, and list transactions.
    """

    def __init__(self):
        self.ledgerService = LedgerService()
        self.router = APIRouter()

        # TODO validation of transaction type -> test with different things in transaction type and check that it fails as it should
        @self.router.post(
            "/transactions/{account_id}",
            response_model=TransactionResponse,
            status_code=status.HTTP_201_CREATED,
        )
        def create_transaction(
            account_id: str, request: TransactionRequest
        ) -> TransactionResponse:
            """Create a deposit or withdrawal transaction."""
            try:
                self.ledgerService.process_transaction(
                    account_id, request.type, request.amount, request.description
                )
                return TransactionResponse(message="Transaction successfully recorded.")
            except ValueError as err:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail=str(err)
                )
            except InsufficientFundsError as err:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail=str(err)
                )

        @self.router.get("/balance/{account_id}", response_model=BalanceResponse)
        def get_balance(account_id: str) -> BalanceResponse:
            """Return the current account balance."""
            try:
                balance = self.ledgerService.get_balance(account_id)
                return BalanceResponse(balance=balance)
            except ValueError as err:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail=str(err)
                )

        @self.router.get("/transactions/{account_id}", response_model=List[Transaction])
        def list_transactions(account_id: str) -> List[Transaction]:
            """Return the transaction history."""
            try:
                return self.ledgerService.list_transactions(account_id)
            except ValueError as err:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail=str(err)
                )


# Instantiate handler and mount its router onto the app.
app = FastAPI(title="Tiny Ledger API")
handler = LedgerHandler()
app.include_router(handler.router)
