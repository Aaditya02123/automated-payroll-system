from sqlalchemy import Column, Integer, String, Float

from app.database import Base


class PayrollResult(Base):
    __tablename__ = "payroll_results"

    id = Column(Integer, primary_key=True, index=True)
    payroll_month = Column(String, nullable=False)
    employee_id = Column(String, nullable=False)
    name = Column(String, nullable=False)
    net_salary = Column(Float, nullable=False)