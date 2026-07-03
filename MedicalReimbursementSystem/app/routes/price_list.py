from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for

from app.services.price_list_service import PriceListService

price_list_bp = Blueprint(
    "price_list",
    __name__,
    url_prefix="/price-list"
)


@price_list_bp.route("/")
def index():
    batches = PriceListService.list_batches()
    return render_template(
        "price_list/index.html",
        batches=batches
    )


@price_list_bp.route("/upload", methods=["GET", "POST"])
def upload():
    institutions = PriceListService.list_institutions()

    if request.method == "POST":
        success, message, batch_id = PriceListService.upload_price_list(
            form_data=request.form,
            file=request.files.get("price_list_file"),
            upload_folder=current_app.config["UPLOAD_FOLDER"]
        )

        flash(message, "success" if success else "error")

        if success:
            return redirect(url_for("price_list.review", batch_id=batch_id))

    return render_template(
        "price_list/upload.html",
        institutions=institutions
    )


@price_list_bp.route("/<int:batch_id>/review")
def review(batch_id):
    batch = PriceListService.get_batch(batch_id)

    if not batch:
        flash("Price list batch not found.", "error")
        return redirect(url_for("price_list.index"))

    items = PriceListService.get_batch_items(batch_id)

    return render_template(
        "price_list/review.html",
        batch=batch,
        items=items
    )


@price_list_bp.route("/item/<int:item_id>/edit", methods=["GET", "POST"])
def edit_item(item_id):
    item = PriceListService.get_item(item_id)

    if not item:
        flash("Price list item not found.", "error")
        return redirect(url_for("price_list.index"))

    if request.method == "POST":
        success, message = PriceListService.update_item(
            item_id,
            request.form
        )

        flash(message, "success" if success else "error")

        return redirect(url_for(
            "price_list.review",
            batch_id=item.batch_id
        ))

    return render_template(
        "price_list/edit.html",
        item=item
    )


@price_list_bp.route("/item/<int:item_id>/delete", methods=["POST"])
def delete_item(item_id):
    success, message, batch_id = PriceListService.delete_item(item_id)

    flash(message, "success" if success else "error")

    return redirect(url_for(
        "price_list.review",
        batch_id=batch_id
    ))


@price_list_bp.route("/<int:batch_id>/approve", methods=["POST"])
def approve_batch(batch_id):
    success, message = PriceListService.approve_batch(batch_id)

    flash(message, "success" if success else "error")

    return redirect(url_for(
        "price_list.review",
        batch_id=batch_id
    ))


@price_list_bp.route("/<int:batch_id>/reject", methods=["POST"])
def reject_batch(batch_id):
    success, message = PriceListService.reject_batch(batch_id)

    flash(message, "success" if success else "error")

    return redirect(url_for("price_list.index"))

@price_list_bp.route("/<int:batch_id>/add-item", methods=["GET", "POST"])
def add_item(batch_id):
    batch = PriceListService.get_batch(batch_id)

    if not batch:
        flash("Price list batch not found.", "error")
        return redirect(url_for("price_list.index"))

    if request.method == "POST":
        success, message = PriceListService.add_item_to_batch(
            batch_id,
            request.form
        )

        flash(message, "success" if success else "error")

        return redirect(url_for(
            "price_list.review",
            batch_id=batch_id
        ))

    return render_template(
        "price_list/add_item.html",
        batch=batch
    )