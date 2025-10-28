# Tiny Ledger API

This is a small ledger web API implemented in Python using FastAPI. It supports recording deposits and withdrawals, viewing the current balance, and fetching the transaction history. Data is kept in-memory for simplicity.

# Assumptions
- Withdrawals that would make the balance negative are rejected (insufficient funds). This results in an exception. Returning and ok status with a rejected operation message and handling in the front end would also be a valid design choice
- The ledger should support multiple accounts (this was unclear from the project description, I opted for the more comprehensive option)

# Out of scope
- Transaction filtering on getTransactions - e.q. based on date, or transaction type
- Thread safety - the implementation of this would depend on how we are going run the service and the real datastore we use for handling the transaction
- Atomic operations/recovery if something goes wrong halfway
- Logging
- Integration testing and fastAPI calls tests
- Dockerisation and making sure it works on other machines. Testing has been done on a windows machine and not verified in other environments


# API usage

Run locally
Install dependencies:

```
python -m pip install -r requirements.txt
```

Start the app (uvicorn):

```
python -m uvicorn app.handler:app --reload --host 127.0.0.1 --port 8000
```

Open the docs: http://127.0.0.1:8000/docs

## Endpoints

1) Create transaction

- Method/URL: POST `/transactions/{account_id}`
- Body (JSON):
	```json
	{
		"type": "deposit" | "withdrawal",
		"amount": 100.0,
		"description": "optional description"
	}
	```
- Success (201):
	```json
	{ "message": "Transaction successfully recorded." }
	```
- Errors:
	- 400: Insufficient funds (for withdrawals)
	- 404: Account not found (for withdrawals on unknown account)

 - cli example:
    - curl (macOS/Linux)
```
curl -X POST "http://127.0.0.1:8000/transactions/acc1" -H 'Content-Type: application/json' -d '{"type":"deposit","amount":100,"description":"Initial deposit"}'
```
-
    - powershell (windows)

```
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/transactions/acc1" `
  -Method Post `
  -Headers @{ "Content-Type" = "application/json" } `
  -Body '{"type":"deposit","amount":100,"description":"Initial deposit"}'
```

2) Get balance

- Method/URL: GET `/balance/{account_id}`
- Success (200):
	```json
	{ "balance": 100.0 }
	```
- Errors:
	- 404: Account not found

- cli example:


```
curl "http://127.0.0.1:8000/balance/acc1"
```

3) List transactions

- Method/URL: GET `/transactions/{account_id}`
- Success (200): returns a list of transactions, each like:
	```json
	{
		"id": "<string>",
		"account_id": "acc1",
		"type": "deposit",
		"amount": 100.0,
		"description": "Initial deposit",
		"timestamp": "2025-10-28T12:34:56.789Z"
	}
	```
- Errors:
	- 404: Account not found

- cli example:

```
curl "http://127.0.0.1:8000/transactions/acc1"
```

Tests

Run tests with:

```
pytest -q
```

## Code formatting (with black)

- In your virtual environment:

```
black .
```