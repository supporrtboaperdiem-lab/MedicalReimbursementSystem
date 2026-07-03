from app.extensions import db
from app.models.base import BaseModel


class MedicalClaim(BaseModel):
    __tablename__ = "medical_claims"

    employee_id = db.Column(
        db.Integer,
        db.ForeignKey("employees.id"),
        nullable=True,
        index=True
    )

    institution_id = db.Column(
        db.Integer,
        db.ForeignKey("institutions.id"),
        nullable=False,
        index=True
    )

    patient_name = db.Column(
        db.String(200),
        nullable=False
    )

    receipt_file_path = db.Column(
        db.String(500),
        nullable=False
    )

    status = db.Column(
        db.String(50),
        nullable=False,
        default="PENDING_REVIEW"
    )

    employee = db.relationship("Employee")
    institution = db.relationship("Institution")

    items = db.relationship(
        "MedicalClaimItem",
        back_populates="claim",
        lazy=True,
        cascade="all, delete-orphan"
    )


class MedicalClaimItem(BaseModel):
    __tablename__ = "medical_claim_items"

    claim_id = db.Column(
        db.Integer,
        db.ForeignKey("medical_claims.id"),
        nullable=False,
        index=True
    )

    service_name = db.Column(
        db.String(255),
        nullable=False
    )

    receipt_price = db.Column(
        db.Numeric(12, 2),
        nullable=False
    )

    approved_price = db.Column(
        db.Numeric(12, 2),
        nullable=True
    )

    difference = db.Column(
        db.Numeric(12, 2),
        nullable=True
    )

    validation_status = db.Column(
        db.String(50),
        nullable=False,
        default="NEEDS_REVIEW"
    )

    claim = db.relationship(
        "MedicalClaim",
        back_populates="items"
    )