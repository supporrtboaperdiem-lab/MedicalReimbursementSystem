from app.extensions import db
from app.models.employee import Employee


class EmployeeRepository:
    @staticmethod
    def get_all():
        return Employee.query.order_by(Employee.created_at.desc()).all()

    @staticmethod
    def get_by_code(employee_code):
        return Employee.query.filter_by(employee_code=employee_code).first()

    @staticmethod
    def create(employee_code, full_name):
        employee = Employee(
            employee_code=employee_code,
            full_name=full_name
        )

        db.session.add(employee)
        db.session.commit()

        return employee