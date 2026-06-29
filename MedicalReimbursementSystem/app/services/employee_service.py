from app.repositories.employee_repository import EmployeeRepository


class EmployeeService:
    @staticmethod
    def list_employees():
        return EmployeeRepository.get_all()

    @staticmethod
    def create_employee(form_data):
        employee_code = form_data.get("employee_code", "").strip()
        full_name = form_data.get("full_name", "").strip()

        if not employee_code:
            return False, "Employee code is required."

        if not full_name:
            return False, "Full name is required."

        existing = EmployeeRepository.get_by_code(employee_code)
        if existing:
            return False, "Employee code already exists."

        EmployeeRepository.create(
            employee_code=employee_code,
            full_name=full_name
        )

        return True, "Employee created successfully."