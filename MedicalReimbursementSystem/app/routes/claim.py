from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for

from app.services.claim_service import ClaimService

claim_bp = Blueprint(
    "claim",
    __name__,
    url_prefix="/claims"
)


@claim_bp.route("/")
def index():
    claims = ClaimService.list_claims()
    return render_template("claim/index.html", claims=claims)


@claim_bp.route("/submit", methods=["GET", "POST"])
def submit():
    institutions = ClaimService.list_institutions()

    if request.method == "POST":
        success, message, claim_id = ClaimService.submit_claim(
            form_data=request.form,
            file=request.files.get("receipt_file"),
            upload_folder=current_app.config["UPLOAD_FOLDER"]
        )

        flash(message, "success" if success else "error")

        if success:
            return redirect(url_for("claim.review", claim_id=claim_id))

    return render_template(
        "claim/submit.html",
        institutions=institutions
    )


@claim_bp.route("/<int:claim_id>/review")
def review(claim_id):
    claim = ClaimService.get_claim(claim_id)

    if not claim:
        flash("Claim not found.", "error")
        return redirect(url_for("claim.index"))

    return render_template("claim/review.html", claim=claim)


@claim_bp.route("/<int:claim_id>/approve", methods=["POST"])
def approve(claim_id):
    success, message = ClaimService.approve_claim(claim_id)

    flash(message, "success" if success else "error")

    return redirect(url_for("claim.review", claim_id=claim_id))


@claim_bp.route("/<int:claim_id>/reject", methods=["POST"])
def reject(claim_id):
    success, message = ClaimService.reject_claim(claim_id)

    flash(message, "success" if success else "error")

    return redirect(url_for("claim.review", claim_id=claim_id))