from app.extensions import db
from app.models.institution import Institution


class InstitutionRepository:
    @staticmethod
    def get_all():
        return Institution.query.order_by(Institution.created_at.desc()).all()

    @staticmethod
    def get_by_name(name):
        return Institution.query.filter_by(name=name).first()

    @staticmethod
    def create(name, institution_type, address=None, phone=None):
        institution = Institution(
            name=name,
            institution_type=institution_type,
            address=address,
            phone=phone,
        )

        db.session.add(institution)
        db.session.commit()

        return institution