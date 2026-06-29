from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.services.employee_service import EmployeeService

employee_bp = Blueprint(
    "employee",
    __name__,
    url_prefix="/employees"
)


@employee_bp.route("/")
def index():
    employees = EmployeeService.list_employees()
    return render_template("employee/index.html", employees=employees)


@employee_bp.route("/create", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        success, message = EmployeeService.create_employee(request.form)

        if success:
            flash(message, "success")
            return redirect(url_for("employee.index"))

        flash(message, "error")

    return render_template("employee/create.html")