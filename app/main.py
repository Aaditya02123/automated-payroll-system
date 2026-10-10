
import csv
import io
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

from fastapi import FastAPI, Depends, File, Form, UploadFile, HTTPException
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.models import PayrollResult

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Simple Payroll API")


def calculate_salary(row):
    salary = Decimal(row["monthly_salary"])
    bonus = Decimal(row["bonus"])
    working_days = int(row["working_days"])
    present_days = int(row["present_days"])

    if salary < 0 or bonus < 0 or working_days <= 0:
        raise ValueError("Invalid salary, bonus, or working days")
    if present_days < 0 or present_days > working_days:
        raise ValueError("Invalid present days")

    salary = salary * present_days / working_days + bonus
    return salary.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


@app.post("/payroll/process")
async def process_payroll(
    file: UploadFile = File(...),
    payroll_month: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        datetime.strptime(payroll_month, "%Y-%m")
    except ValueError:
        raise HTTPException(400, "Month must be YYYY-MM")

    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(400, "Upload a CSV file")

    content = await file.read()
    try:
        reader = csv.DictReader(
            io.StringIO(content.decode("utf-8-sig"))
        )
    except UnicodeDecodeError:
        raise HTTPException(400, "CSV must use UTF-8 encoding")

    required = ["employee_id", "name", "monthly_salary",
                "working_days", "present_days", "bonus"]
    if not reader.fieldnames or not all(c in reader.fieldnames for c in required):
        raise HTTPException(400, "CSV is missing required columns")

    results, errors = [], []
    try:
        for number, row in enumerate(reader, start=2):
            try:
                employee_id = (row.get("employee_id") or "").strip()
                name = (row.get("name") or "").strip()
                if not employee_id or not name:
                    raise ValueError("Employee ID and name are required")

                salary = calculate_salary(row)
                db.add(PayrollResult(
                    payroll_month=payroll_month,
                    employee_id=employee_id,
                    name=name,
                    net_salary=float(salary)
                ))
                results.append({
                    "employee_id": employee_id,
                    "name": name,
                    "net_salary": float(salary)
                })
            except (ValueError, KeyError, TypeError) as error:
                errors.append({"row_number": number, "error": str(error)})

        db.commit()
    except Exception as error:
        db.rollback()
        print("Database error:", error)
        raise HTTPException(500, "Could not save payroll results")

    return {"payroll_month": payroll_month, "successful_count": len(results),
            "failed_count": len(errors), "results": results, "errors": errors}


@app.get("/payroll/results")
def get_payroll_results(db: Session = Depends(get_db)):
    rows = db.query(PayrollResult).all()
    return [
        {"payroll_month": r.payroll_month, "employee_id": r.employee_id,
         "name": r.name, "net_salary": r.net_salary}
        for r in rows
    ]
