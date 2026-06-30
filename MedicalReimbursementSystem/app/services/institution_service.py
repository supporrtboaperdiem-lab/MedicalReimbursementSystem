from app.constants.enums import InstitutionType
from app.repositories.institution_repository import InstitutionRepository


class InstitutionService:
    @staticmethod
    def list_institutions():
        return InstitutionRepository.get_all()

    @staticmethod
    def get_institution_types():
        return [item.value for item in InstitutionType]

    @staticmethod
    def create_institution(form_data):
        name = form_data.get("name", "").strip()
        institution_type = form_data.get("institution_type", "").strip()
        address = form_data.get("address", "").strip()
        phone = form_data.get("phone", "").strip()

        if not name:
            return False, "Institution name is required."

        if not institution_type:
            return False, "Institution type is required."

        allowed_types = InstitutionService.get_institution_types()
        if institution_type not in allowed_types:
            return False, "Invalid institution type."

        existing = InstitutionRepository.get_by_name(name)
        if existing:
            return False, "Institution already exists."

        InstitutionRepository.create(
            name=name,
            institution_type=institution_type,
            address=address,
            phone=phone,
        )

        return True, "Institution created successfully."