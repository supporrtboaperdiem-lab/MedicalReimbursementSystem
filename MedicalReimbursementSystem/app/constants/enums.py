from enum import Enum


class InstitutionType(Enum):
    HOSPITAL = "Hospital"
    PHARMACY = "Pharmacy"
    EYE_CARE = "Eye Care"
    HEARING_CARE = "Hearing Care"
    LABORATORY = "Laboratory"
    OTHER = "Other"


class DocumentStatus(Enum):
    UPLOADED = "UPLOADED"
    PROCESSING = "PROCESSING"
    OCR_COMPLETED = "OCR_COMPLETED"
    REVIEW_PENDING = "REVIEW_PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class ExpenseStatus(Enum):
    PENDING = "PENDING"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"


class SourceType(Enum):
    OCR = "OCR"
    EXCEL = "EXCEL"
    MANUAL = "MANUAL"