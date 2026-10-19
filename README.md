# FastTag & Toll Transaction Microservice

A Python REST API that simulates vehicle toll payments, validates account balances, records transaction logs, and provides revenue analytics.

## Features

- Register vehicles with unique license plates.
- Store vehicle account balances in SQLite.
- Process toll transactions and deduct fees when sufficient funds are available.
- Record successful and insufficient-funds transaction attempts.
- Retrieve vehicle and transaction records.
- Generate transaction and revenue summaries.
- Interactive API documentation using FastAPI and Swagger UI.
- Automated tests using pytest and FastAPI's test client.

## Tech Stack

- **Programming Language:** Python
- **Backend Framework:** FastAPI
- **Database:** SQLite
- **ORM:** SQLAlchemy
- **Data Validation:** Pydantic
- **Testing:** pytest, HTTPX
- **API Documentation:** Swagger UI / OpenAPI

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Display the service home page |
| POST | `/vehicles` | Register a new vehicle |
| GET | `/vehicles` | Retrieve registered vehicles |
| POST | `/transaction/process` | Process a toll transaction |
| GET | `/transactions` | Retrieve transaction logs |
| GET | `/analytics/summary` | Retrieve transaction and revenue analytics |

## Project Structure

```text
fasttag-toll-service/
├── main.py
├── test_main.py
├── conftest.py
├── requirements.txt
├── README.md
└── .gitignore
```

## Prerequisites

- Python 3.10 or newer
- pip
- Git (for cloning the repository)

## Installation and Setup

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd fasttag-toll-service
```

Replace `YOUR_GITHUB_REPOSITORY_URL` with your actual GitHub repository URL.

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Install dependencies

On Windows PowerShell:

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 4. Start the application

```powershell
.\venv\Scripts\python.exe -m uvicorn main:app --reload
```

The API will be available at:

`http://127.0.0.1:8000`

### 5. Explore the API

Open the interactive Swagger documentation:

`http://127.0.0.1:8000/docs`

Use Swagger UI to register vehicles, process toll transactions, and inspect analytics.

## Running Automated Tests

Run the test suite using:

```powershell
.\venv\Scripts\python.exe -m pytest -v
```

The test suite currently covers:

- Home page response
- Vehicle registration
- Duplicate license plate validation
- Unknown vehicle handling
- Successful toll transactions
- Insufficient-funds transactions
- Transaction analytics and revenue calculations

## Database

The application uses SQLite for persistent storage. SQLAlchemy manages database interactions, and the application creates its tables automatically.

Automated tests use a separate in-memory SQLite database to avoid modifying the normal application database through test requests.

## Future Improvements

- Add authentication and authorization.
- Improve concurrency-safe balance updates and transaction handling.
- Add pagination and date-based analytics.
- Build a dashboard for toll transaction monitoring.
- Add deployment configuration and CI/CD.
- Expand automated test coverage.

## Project Status

The core API endpoints and seven automated tests have been implemented. This project is an educational prototype and is not intended for processing real toll payments without additional security, reliability, and financial transaction safeguards.

## Author

**Om Prakash Routray**

B.Tech Computer Science and Engineering Student