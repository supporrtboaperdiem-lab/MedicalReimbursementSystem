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
    return render_template("price_list/index.html", items=items)


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


@price_list_bp.route("/<int:item_id>/edit", methods=["GET", "POST"])
def edit(item_id):
    item = PriceListService.get_item(item_id)

    if not item:
        flash("Price list item not found.", "error")
        return redirect(url_for("price_list.index"))

    if request.method == "POST":
        success, message = PriceListService.update_item(item_id, request.form)

        if success:
            flash(message, "success")
            return redirect(url_for("price_list.index"))

        flash(message, "error")

    return render_template("price_list/edit.html", item=item)


@price_list_bp.route("/<int:item_id>/delete", methods=["POST"])
def delete(item_id):
    success, message = PriceListService.delete_item(item_id)

    if success:
        flash(message, "success")
    else:
        flash(message, "error")

    return redirect(url_for("price_list.index"))