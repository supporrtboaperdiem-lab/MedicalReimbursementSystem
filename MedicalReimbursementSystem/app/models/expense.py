from app.extensions import db
from app.models.base import BaseModel


class Expense(BaseModel):
    __tablename__ = "expenses"

    employee_id = db.Column(
        db.Integer,
        db.ForeignKey("employees.id"),
        nullable=True
    )

    institution_id = db.Column(
        db.Integer,
        db.ForeignKey("institutions.id"),
        nullable=True
    )

    document_id = db.Column(
        db.Integer,
        db.ForeignKey("documents.id"),
        nullable=True
    )

    item_name = db.Column(db.String(255), nullable=False)

    cash_price = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    discount = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    final_price = db.Column(db.Numeric(12, 2), nullable=False, default=0)

    expense_category = db.Column(db.String(100), nullable=True)

    source = db.Column(
        db.String(50),
        nullable=False,
        default="OCR"
    )

    review_status = db.Column(
        db.String(50),
        nullable=False,
        default="PENDING_REVIEW"
    )

    employee = db.relationship(
        "Employee",
        back_populates="expenses"
    )

    institution = db.relationship(
        "Institution",
        back_populates="expenses"
    )

    document = db.relationship(
        "Document",
        back_populates="expenses"
    )

    def __repr__(self):
        return f"<Expense {self.item_name} - {self.final_price}>"