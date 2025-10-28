from __future__ import annotations

from datetime import datetime
from time import time
from typing import Dict, List

from .schemas import *


class InsufficientFundsError(Exception):
    """Exception raised when attempting to withdraw more than the available balance."""

    pass


class LedgerService:
    """In-memory ledger service for managing account transactions and balances.


    Public Methods:
        process_transaction: Process deposit or withdrawal.
                Accounts are auto-created on first transaction.
                Withdrawals require the account to already exist and sufficient funds in it.
        get_balance: Get current account balance (raises ValueError if not found).
        list_transactions: Get transaction history (raises ValueError if not found).
    """

    def __init__(self) -> None:
        self._transactions: Dict[str, List[Transaction]] = {}
        self._balances: Dict[str, float] = {}

    def process_transaction(
        self,
        account_id: str,
        transaction_type: TransactionType,
        amount: float,
        description: str | None = None,
    ) -> None:
        # Parsing
        current_timestamp = datetime.fromtimestamp(time())
        transaction = self._parse_transaction_request(
            account_id, transaction_type, amount, current_timestamp, description
        )

        # Validation
        self._validate_transaction_amount(transaction.amount)
        if transaction.type == TransactionType.WITHDRAWAL:
            self._validate_withdrawal_is_possible(transaction)

        # Record transaction
        self._setup_account_if_not_exists(transaction.account_id)
        self._record_transaction(transaction)

    def get_balance(self, account_id: str) -> float:
        if account_id not in self._balances:
            raise ValueError(f"Account {account_id} does not exist.")
        return self._balances[account_id]

    def list_transactions(self, account_id: str) -> List[Transaction]:
        if account_id not in self._transactions:
            raise ValueError(f"Account {account_id} does not exist.")
        return self._transactions[account_id]

    def _parse_transaction_request(
        self,
        account_id: str,
        transaction_type: TransactionType,
        amount: float,
        transaction_timestamp: datetime,
        description: str | None = None,
    ) -> Transaction:
        return Transaction(
            id=self._generate_transaction_id(account_id),
            account_id=account_id,
            type=transaction_type,
            amount=amount,
            description=description,
            timestamp=transaction_timestamp,
        )

    def _generate_transaction_id(self, account_id: str) -> str:
        transaction_number = len(self._transactions.get(account_id, [])) + 1
        return f"{hash(account_id)}_{transaction_number}"

    def _setup_account_if_not_exists(self, account_id: str) -> None:
        if not account_id in self._transactions:
            self._transactions[account_id] = []
        # In practice if one doesn't exist, the other also won't, but this is more sturdy
        if not account_id in self._balances:
            self._balances[account_id] = 0.0

    def _record_transaction(self, transaction: Transaction) -> None:
        self._transactions[transaction.account_id].append(transaction)

        if transaction.type == TransactionType.DEPOSIT:
            self._balances[transaction.account_id] += transaction.amount
        elif transaction.type == TransactionType.WITHDRAWAL:
            self._balances[transaction.account_id] -= transaction.amount
        else:
            raise ValueError(f"Unknown transaction type: {transaction.type}")

    def _validate_transaction_amount(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError(f"Transaction amount must be positive: {amount}")

    def _validate_withdrawal_is_possible(self, transaction: Transaction) -> None:
        if not transaction.account_id in self._balances:
            raise ValueError(f"Account {transaction.account_id} does not exist.")
        if self._balances[transaction.account_id] < transaction.amount:
            raise InsufficientFundsError(
                f"""Insufficient funds for withdrawal: 
                    Account ID: {transaction.account_id}, 
                    Withdrawal Amount: {transaction.amount}
                """
            )
