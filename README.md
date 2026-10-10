# Automated Payroll Processing System

## Overview

A payroll processing API built using FastAPI, SQLite, and SQLAlchemy. The application accepts a CSV file containing employee salary and attendance information, calculates net salaries, stores successful results, records invalid rows, and provides a downloadable CSV report.

## Features

- Upload a payroll CSV with a payroll month.
- Create a payroll job with an initial `PENDING` status.
- Process payroll using FastAPI background tasks.
- Calculate salary using attendance and bonus.

## Technology Stack

- Python
- FastAPI
- SQLite
- SQLAlchemy
- Pydantic
- Python CSV and Decimal modules

## Setup

Create and activate a virtual environment, then install dependencies.

```bash
python -m venv venv
```

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

Install packages:

```bash
pip install -r requirements.txt
```

Run the application from the project root:

```bash
python -m uvicorn app.main:app --reload
```

Open the API documentation at:

`http://127.0.0.1:8000/docs`

## API Endpoints

POST - /payroll/process - Process Payroll
GET - /payroll/results - Get Payroll Results
