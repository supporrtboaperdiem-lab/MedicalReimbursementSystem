from flask import Blueprint, flash, redirect, render_template, request, url_for

from app.services.price_list_service import PriceListService

price_list_bp = Blueprint(
    "price_list",
    __name__,
    url_prefix="/price-list"
)


@price_list_bp.route("/")
def index():
    items = PriceListService.list_items()
    return render_template(
        "price_list/index.html",
        items=items
    )


@price_list_bp.route("/create", methods=["GET", "POST"])
def create():
    institutions = PriceListService.list_institutions()

    if request.method == "POST":
        success, message = PriceListService.create_item(request.form)

        if success:
            flash(message, "success")
            return redirect(url_for("price_list.index"))

        flash(message, "error")

    return render_template(
        "price_list/create.html",
        institutions=institutions
    )