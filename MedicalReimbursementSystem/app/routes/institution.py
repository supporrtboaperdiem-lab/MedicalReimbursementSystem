from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.services.institution_service import InstitutionService

institution_bp = Blueprint(
    "institution",
    __name__,
    url_prefix="/institutions"
)


@institution_bp.route("/")
def index():
    institutions = InstitutionService.list_institutions()
    return render_template(
        "institution/index.html",
        institutions=institutions
    )


@institution_bp.route("/create", methods=["GET", "POST"])
def create():
    institution_types = InstitutionService.get_institution_types()

    if request.method == "POST":
        success, message = InstitutionService.create_institution(request.form)

        if success:
            flash(message, "success")
            return redirect(url_for("institution.index"))

        flash(message, "error")

    return render_template(
        "institution/create.html",
        institution_types=institution_types
    )