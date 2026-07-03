from app.extensions import db
from app.models.claim import MedicalClaim, MedicalClaimItem


class ClaimRepository:
    @staticmethod
    def get_all():
        return MedicalClaim.query.order_by(
            MedicalClaim.created_at.desc()
        ).all()

    @staticmethod
    def get_by_id(claim_id):
        return MedicalClaim.query.get(claim_id)

    @staticmethod
    def create_claim(
        institution_id,
        patient_name,
        receipt_file_path,
        employee_id=None
    ):
        claim = MedicalClaim(
            employee_id=employee_id,
            institution_id=institution_id,
            patient_name=patient_name,
            receipt_file_path=receipt_file_path,
            status="PENDING_REVIEW"
        )

        db.session.add(claim)
        db.session.commit()

        return claim

    @staticmethod
    def create_item(
        claim_id,
        service_name,
        receipt_price,
        approved_price=None,
        difference=None,
        validation_status="NEEDS_REVIEW"
    ):
        item = MedicalClaimItem(
            claim_id=claim_id,
            service_name=service_name,
            receipt_price=receipt_price,
            approved_price=approved_price,
            difference=difference,
            validation_status=validation_status
        )

        db.session.add(item)
        db.session.commit()

        return item

    @staticmethod
    def approve_claim(claim):
        claim.status = "APPROVED"
        db.session.commit()
        return claim

    @staticmethod
    def reject_claim(claim):
        claim.status = "REJECTED"
        db.session.commit()
        return claim