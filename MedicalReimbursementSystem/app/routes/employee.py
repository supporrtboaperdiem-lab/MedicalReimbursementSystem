from flask import Blueprint, render_template

employee_bp = Blueprint(
    "employee",
    __name__,
    url_prefix="/employees"
)


@employee_bp.route("/")
def index():
    return render_template("employee/index.html")


@employee_bp.route("/create")
def create():
    return render_template("employee/create.html")