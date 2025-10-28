from __future__ import annotations

from datetime import datetime
from time import time
from typing import List

import pytest

from app.schemas import Transaction, TransactionType
from app.tinyLedger import LedgerService, InsufficientFundsError


@pytest.fixture
def ledger_service() -> LedgerService:
    """Create a fresh LedgerService for each test."""
    return LedgerService()


class TestLedgerService:
    """Test suite for LedgerService class."""

    def test_process_transactions_saves_data(
        self, ledger_service: LedgerService
    ) -> None:
        ledger_service.process_transaction("acc1", TransactionType.DEPOSIT, 100.0)
        ledger_service.process_transaction("acc2", TransactionType.DEPOSIT, 100.0)

        assert ledger_service.list_transactions("acc1") is not None
        assert ledger_service.list_transactions("acc2") is not None
        assert ledger_service.get_balance("acc1") is not None

    def test_process_transaction_creates_correct_transactions_ledger(
        self, ledger_service: LedgerService
    ) -> None:
        ledger_service.process_transaction(
            "acc1", TransactionType.DEPOSIT, 150.0, "Test deposit 1"
        )
        ledger_service.process_transaction(
            "acc1", TransactionType.WITHDRAWAL, 100.0, "Test deposit 2"
        )
        ledger_service.process_transaction(
            "acc1", TransactionType.DEPOSIT, 100.0, "Test deposit 3"
        )
        ledger_service.process_transaction(
            "acc2", TransactionType.DEPOSIT, 100.0, "Test deposit 3"
        ) # should not be in acc1's ledger as it is a different account

        transactions: List[Transaction] = ledger_service.list_transactions("acc1")
        transaction1: Transaction = transactions[0]
        transaction2: Transaction = transactions[1]

        assert len(transactions) == 3
        assert transaction1.amount == 150.0
        assert transaction1.description == "Test deposit 1"
        assert transaction1.type == TransactionType.DEPOSIT
        assert transaction1.id == f"{hash('acc1')}_1"
        assert transaction1.account_id == "acc1"
        # id
        assert transaction2.id == f"{hash('acc1')}_2"
        assert transaction2.amount == 100.0

    def test_multiple_deposits_balance_calculated_correctly(
        self, ledger_service: LedgerService
    ) -> None:
        ledger_service.process_transaction("acc1", TransactionType.DEPOSIT, 100.0)
        ledger_service.process_transaction("acc1", TransactionType.DEPOSIT, 50.0)
        ledger_service.process_transaction("acc1", TransactionType.DEPOSIT, 25.5)

        assert ledger_service.get_balance("acc1") == 175.5

    def test_deposit_and_withdraw_balance_calculated_correctly(
        self, ledger_service: LedgerService
    ) -> None:
        ledger_service.process_transaction("acc1", TransactionType.DEPOSIT, 200.0)
        ledger_service.process_transaction("acc1", TransactionType.WITHDRAWAL, 75.0)
        ledger_service.process_transaction("acc1", TransactionType.WITHDRAWAL, 25.0)

        assert ledger_service.get_balance("acc1") == 100.0

    def test_withdrawal_with_insufficient_funds_raises_error(
        self, ledger_service: LedgerService
    ) -> None:
        ledger_service.process_transaction("acc1", TransactionType.DEPOSIT, 50.0)

        with pytest.raises(InsufficientFundsError, match="Insufficient funds"):
            ledger_service.process_transaction(
                "acc1", TransactionType.WITHDRAWAL, 100.0
            )

    def test_withdrawal_from_nonexistent_account_raises_error(
        self, ledger_service: LedgerService
    ) -> None:
        with pytest.raises(ValueError, match="Account acc1 does not exist"):
            ledger_service.process_transaction("acc1", TransactionType.WITHDRAWAL, 50.0)

    def test_transaction_with_nonpositive_amount_raises_error(
        self, ledger_service: LedgerService
    ) -> None:
        with pytest.raises(ValueError, match="Transaction amount must be positive"):
            ledger_service.process_transaction("acc1", TransactionType.DEPOSIT, -20.0)

    def test_get_balance_for_nonexistent_account_raises_error(
        self, ledger_service: LedgerService
    ) -> None:
        with pytest.raises(ValueError, match="Account acc1 does not exist"):
            ledger_service.get_balance("acc1")

    def test_list_transactions_for_nonexistent_account_raises_error(
        self, ledger_service: LedgerService
    ) -> None:
        with pytest.raises(ValueError, match="Account acc1 does not exist"):
            ledger_service.list_transactions("acc1")
