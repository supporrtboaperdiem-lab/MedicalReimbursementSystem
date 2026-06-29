from app.extensions import db
from app.models.base import BaseModel


class Employee(BaseModel):
    __tablename__ = "employees"

    employee_code = db.Column(
        db.String(50),
        unique=True,
        nullable=False,
        index=True
    )

    full_name = db.Column(
        db.String(200),
        nullable=False
    )

    expenses = db.relationship(
        "Expense",
        back_populates="employee",
        lazy=True
    )

    documents = db.relationship(
        "Document",
        back_populates="employee",
        lazy=True
    )

    def __repr__(self):
        return f"<Employee {self.employee_code} - {self.full_name}>"