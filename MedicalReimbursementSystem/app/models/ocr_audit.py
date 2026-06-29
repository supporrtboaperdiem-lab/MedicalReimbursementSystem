from app.extensions import db
from app.models.base import BaseModel


class OCRAudit(BaseModel):
    __tablename__ = "ocr_audits"

    document_id = db.Column(
        db.Integer,
        db.ForeignKey("documents.id"),
        nullable=False
    )

    page_number = db.Column(
        db.Integer,
        nullable=False
    )

    extracted_line_count = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )

    processing_seconds = db.Column(
        db.Numeric(10, 3),
        nullable=True
    )

    confidence_score = db.Column(
        db.Numeric(5, 2),
        nullable=True
    )

    error_message = db.Column(
        db.Text,
        nullable=True
    )

    document = db.relationship(
        "Document",
        back_populates="ocr_audits"
    )

    def __repr__(self):
        return f"<OCRAudit document={self.document_id} page={self.page_number}>"