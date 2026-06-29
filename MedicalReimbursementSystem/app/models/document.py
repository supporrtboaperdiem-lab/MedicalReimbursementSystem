from app.extensions import db
from app.models.base import BaseModel


class Document(BaseModel):
    __tablename__ = "documents"

    original_filename = db.Column(db.String(255), nullable=False)
    stored_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(20), nullable=False)

    status = db.Column(
        db.String(50),
        default="UPLOADED",
        nullable=False
    )

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

    employee = db.relationship(
        "Employee",
        back_populates="documents"
    )

    institution = db.relationship(
        "Institution",
        back_populates="documents"
    )

    expenses = db.relationship(
        "Expense",
        back_populates="document",
        lazy=True
    )

    ocr_audits = db.relationship(
        "OCRAudit",
        back_populates="document",
        lazy=True
    )

    def __repr__(self):
        return f"<Document {self.original_filename} - {self.status}>"