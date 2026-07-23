import os
import re
from decimal import Decimal, InvalidOperation
from pathlib import Path
from uuid import uuid4

from werkzeug.utils import secure_filename

from app.models.institution import Institution
from app.repositories.price_list_batch_repository import (
    PriceListBatchRepository,
)
from app.repositories.price_list_repository import (
    PriceListRepository,
)
from app.services.ocr import extract_numeric_lines
from app.services.price_list_extraction_service import (
    PriceListExtractionService,
)
from app.services.excel_price_list_service import (
    ExcelPriceListService,
)


PRICE_LIST_SERVICE_VERSION = "2026-07-22-v3"


class PriceListService:
    ALLOWED_EXTENSIONS = {
        ".pdf",
        ".jpg",
        ".jpeg",
        ".png",
        ".xlsx",
    }

    @staticmethod
    def list_batches():
        return PriceListBatchRepository.get_all()

    @staticmethod
    def list_institutions():
        return Institution.query.order_by(
            Institution.name.asc()
        ).all()

    @staticmethod
    def get_batch(batch_id):
        return PriceListBatchRepository.get_by_id(
            batch_id
        )

    @staticmethod
    def get_batch_items(batch_id):
        return PriceListRepository.get_by_batch(
            batch_id
        )

    @staticmethod
    def get_item(item_id):
        return PriceListRepository.get_by_id(
            item_id
        )

    @staticmethod
    def _normalize_service_name(value):
        if value is None:
            return ""

        text = str(value)
        text = text.replace("\u00a0", " ")
        text = text.replace("\u202f", " ")
        text = text.replace("\r", " ")
        text = text.replace("\n", " ")
        text = text.replace("\t", " ")

        return re.sub(
            r"\s+",
            " ",
            text,
        ).strip()

    @staticmethod
    def _to_decimal(value):
        """
        Convert a stored or extracted price into Decimal without
        changing the value.
        """

        if value is None:
            return None

        if isinstance(value, bool):
            return None

        if isinstance(value, Decimal):
            return value

        if isinstance(value, int):
            return Decimal(value)

        if isinstance(value, float):
            try:
                return Decimal(str(value))
            except (
                InvalidOperation,
                ValueError,
            ):
                return None

        try:
            cleaned = str(value).strip()

            if not cleaned:
                return None

            cleaned = cleaned.replace(
                "\u00a0",
                "",
            )
            cleaned = cleaned.replace(
                "\u202f",
                "",
            )
            cleaned = cleaned.replace(
                ",",
                "",
            )
            cleaned = cleaned.replace(
                " ",
                "",
            )

            cleaned = re.sub(
                r"(?i)(ETB|BIRR|BR|USD)",
                "",
                cleaned,
            )

            cleaned = cleaned.replace(
                "(",
                "-",
            )
            cleaned = cleaned.replace(
                ")",
                "",
            )

            cleaned = re.sub(
                r"[^0-9.\-]",
                "",
                cleaned,
            )

            if cleaned in {
                "",
                "-",
                ".",
                "-.",
            }:
                return None

            if cleaned.count(".") > 1:
                return None

            return Decimal(cleaned)

        except (
            InvalidOperation,
            AttributeError,
            TypeError,
            ValueError,
        ):
            return None

    @staticmethod
    def _is_editable_batch(batch):
        if not batch:
            return (
                False,
                "Price list batch not found.",
            )

        if batch.status == "APPROVED":
            return (
                False,
                "Approved price lists cannot be changed.",
            )

        if batch.status == "REJECTED":
            return (
                False,
                "Rejected price lists cannot be changed.",
            )

        return True, None

    @staticmethod
    def upload_price_list(
        form_data,
        file,
        upload_folder,
    ):
        print(
            f"[PRICE LIST] Service version: "
            f"{PRICE_LIST_SERVICE_VERSION}",
            flush=True,
        )

        institution_id = str(
            form_data.get(
                "institution_id",
                "",
            )
        ).strip()

        batch_name = str(
            form_data.get(
                "batch_name",
                "",
            )
        ).strip()

        if not institution_id:
            return (
                False,
                "Institution is required.",
                None,
            )

        institution = Institution.query.get(
            institution_id
        )

        if not institution:
            return (
                False,
                "Selected institution was not found.",
                None,
            )

        if not batch_name:
            return (
                False,
                "Price list name is required.",
                None,
            )

        if not file or not file.filename:
            return (
                False,
                "Price list file is required.",
                None,
            )

        original_name = secure_filename(
            file.filename
        )

        if not original_name:
            return (
                False,
                "Invalid uploaded filename.",
                None,
            )

        extension = Path(
            original_name
        ).suffix.lower()

        if (
            extension
            not in PriceListService.ALLOWED_EXTENSIONS
        ):
            return (
                False,
                (
                    "Only PDF, JPG, JPEG, PNG, "
                    "and XLSX files are allowed."
                ),
                None,
            )

        os.makedirs(
            upload_folder,
            exist_ok=True,
        )

        stored_name = (
            f"{uuid4().hex}_{original_name}"
        )

        file_path = os.path.join(
            upload_folder,
            stored_name,
        )

        extracted_items = []
        conflicts = []
        batch = None

        try:
            print(
                f"[PRICE LIST] Saving uploaded file: "
                f"{original_name}",
                flush=True,
            )

            file.save(file_path)

            if extension == ".xlsx":
                print(
                    f"[PRICE LIST] Starting Excel "
                    f"extraction: {original_name}",
                    flush=True,
                )

                excel_result = (
                    ExcelPriceListService
                    .extract_price_list(
                        file_path
                    )
                )

                extracted_items = (
                    excel_result.get(
                        "items",
                        [],
                    )
                )

                conflicts = (
                    excel_result.get(
                        "conflicts",
                        [],
                    )
                )

                sheet_reports = (
                    excel_result.get(
                        "sheets",
                        excel_result.get(
                            "sheet_reports",
                            [],
                        ),
                    )
                )

                worksheet_count = (
                    excel_result.get(
                        "worksheet_count",
                        0,
                    )
                )

                processed_sheet_count = (
                    excel_result.get(
                        "processed_sheet_count",
                        0,
                    )
                )

                print(
                    f"[PRICE LIST] Excel extraction "
                    f"completed. "
                    f"Items={len(extracted_items)}, "
                    f"Sheets={worksheet_count}, "
                    f"Processed="
                    f"{processed_sheet_count}.",
                    flush=True,
                )

                for report in sheet_reports:
                    print(
                        f"[PRICE LIST] Sheet report: "
                        f"{report}",
                        flush=True,
                    )

                # Show exactly what the Excel extractor returned.
                print(
                    "[PRICE LIST] First extracted "
                    "Excel records:",
                    flush=True,
                )

                for index, item in enumerate(
                    extracted_items[:20],
                    start=1,
                ):
                    print(
                        f"[PRICE LIST][EXTRACTED "
                        f"{index}] "
                        f"Service="
                        f"{item.get('service_name')!r}, "
                        f"Price="
                        f"{item.get('approved_price')!r}, "
                        f"RawPrice="
                        f"{item.get('raw_price')!r}, "
                        f"Sheet="
                        f"{item.get('source_sheet')!r}, "
                        f"Row="
                        f"{item.get('source_row')!r}, "
                        f"PriceCell="
                        f"{item.get('source_price_cell')!r}, "
                        f"PriceHeader="
                        f"{item.get('price_header')!r}, "
                        f"PriceColumn="
                        f"{item.get('price_column')!r}",
                        flush=True,
                    )

            else:
                print(
                    f"[PRICE LIST] Starting OCR "
                    f"extraction: {original_name}",
                    flush=True,
                )

                ocr_records = extract_numeric_lines(
                    file_path,
                    save_debug_pages=False,
                )

                print(
                    f"[PRICE LIST] OCR records "
                    f"extracted: "
                    f"{len(ocr_records)}",
                    flush=True,
                )

                (
                    extracted_items,
                    conflicts,
                ) = (
                    PriceListExtractionService
                    .extract_items(
                        ocr_records
                    )
                )

                print(
                    f"[PRICE LIST] OCR processing "
                    f"completed. "
                    f"Items="
                    f"{len(extracted_items)}",
                    flush=True,
                )

            if not extracted_items:
                source_name = (
                    "Excel file"
                    if extension == ".xlsx"
                    else "document"
                )

                return (
                    False,
                    (
                        "No valid service and price "
                        f"rows were found in the "
                        f"{source_name}."
                    ),
                    None,
                )

            valid_items = []
            seen_services = set()
            duplicates = 0
            invalid_rows = 0

            for source_index, item in enumerate(
                extracted_items,
                start=1,
            ):
                service_name = (
                    PriceListService
                    ._normalize_service_name(
                        item.get(
                            "service_name",
                            "",
                        )
                    )
                )

                raw_approved_price = item.get(
                    "approved_price"
                )

                approved_price = (
                    PriceListService
                    ._to_decimal(
                        raw_approved_price
                    )
                )

                if not service_name:
                    invalid_rows += 1

                    print(
                        f"[PRICE LIST][REJECTED] "
                        f"ExtractedIndex="
                        f"{source_index}, "
                        f"Reason=missing service, "
                        f"Item={item!r}",
                        flush=True,
                    )

                    continue

                if approved_price is None:
                    invalid_rows += 1

                    print(
                        f"[PRICE LIST][REJECTED] "
                        f"ExtractedIndex="
                        f"{source_index}, "
                        f"Service="
                        f"{service_name!r}, "
                        f"Reason=invalid price, "
                        f"RawApprovedPrice="
                        f"{raw_approved_price!r}, "
                        f"Item={item!r}",
                        flush=True,
                    )

                    continue

                if approved_price <= 0:
                    invalid_rows += 1

                    print(
                        f"[PRICE LIST][REJECTED] "
                        f"ExtractedIndex="
                        f"{source_index}, "
                        f"Service="
                        f"{service_name!r}, "
                        f"Reason=non-positive price, "
                        f"Price={approved_price}",
                        flush=True,
                    )

                    continue

                normalized_service = (
                    service_name.casefold()
                )

                if (
                    normalized_service
                    in seen_services
                ):
                    duplicates += 1

                    print(
                        f"[PRICE LIST][DUPLICATE] "
                        f"ExtractedIndex="
                        f"{source_index}, "
                        f"Service="
                        f"{service_name!r}, "
                        f"Price={approved_price}",
                        flush=True,
                    )

                    continue

                seen_services.add(
                    normalized_service
                )

                valid_item = {
                    "service_name": service_name,
                    "approved_price": (
                        approved_price
                    ),
                    "source_sheet": item.get(
                        "source_sheet"
                    ),
                    "source_row": item.get(
                        "source_row"
                    ),
                    "source_price_cell": (
                        item.get(
                            "source_price_cell"
                        )
                    ),
                    "raw_price": item.get(
                        "raw_price"
                    ),
                }

                valid_items.append(
                    valid_item
                )

                # This confirms no calculation occurs here.
                print(
                    f"[PRICE LIST][VALIDATED] "
                    f"Service={service_name!r}, "
                    f"ExtractorPrice="
                    f"{raw_approved_price!r}, "
                    f"ValidatedPrice="
                    f"{approved_price}, "
                    f"Sheet="
                    f"{valid_item['source_sheet']!r}, "
                    f"Row="
                    f"{valid_item['source_row']!r}, "
                    f"Cell="
                    f"{valid_item['source_price_cell']!r}",
                    flush=True,
                )

            if not valid_items:
                return (
                    False,
                    (
                        "The file was read, but no "
                        "valid service with a positive "
                        "price was found."
                    ),
                    None,
                )

            print(
                f"[PRICE LIST] Creating pending "
                f"batch. "
                f"Valid items="
                f"{len(valid_items)}",
                flush=True,
            )

            batch = (
                PriceListBatchRepository.create(
                    institution_id=(
                        institution_id
                    ),
                    name=batch_name,
                )
            )

            inserted = 0

            for valid_index, item in enumerate(
                valid_items,
                start=1,
            ):
                existing = (
                    PriceListRepository
                    .get_by_batch_and_service(
                        batch_id=batch.id,
                        service_name=(
                            item[
                                "service_name"
                            ]
                        ),
                    )
                )

                if existing:
                    duplicates += 1

                    print(
                        f"[PRICE LIST][DATABASE "
                        f"DUPLICATE] "
                        f"Service="
                        f"{item['service_name']!r}",
                        flush=True,
                    )

                    continue

                print(
                    f"[PRICE LIST][INSERTING] "
                    f"Index={valid_index}, "
                    f"Batch={batch.id}, "
                    f"Service="
                    f"{item['service_name']!r}, "
                    f"Price="
                    f"{item['approved_price']}, "
                    f"ExcelSheet="
                    f"{item.get('source_sheet')!r}, "
                    f"ExcelRow="
                    f"{item.get('source_row')!r}, "
                    f"ExcelCell="
                    f"{item.get('source_price_cell')!r}, "
                    f"ExcelRawPrice="
                    f"{item.get('raw_price')!r}",
                    flush=True,
                )

                PriceListRepository.create(
                    batch_id=batch.id,
                    institution_id=(
                        institution_id
                    ),
                    service_name=(
                        item["service_name"]
                    ),
                    approved_price=(
                        item["approved_price"]
                    ),
                )

                inserted += 1

            if inserted == 0:
                return (
                    False,
                    (
                        "No unique service and price "
                        "rows could be saved."
                    ),
                    batch.id,
                )

            source_type = (
                "Excel price list"
                if extension == ".xlsx"
                else "OCR price list"
            )

            message = (
                f"{source_type} uploaded "
                f"successfully. "
                f"{inserted} unique services "
                f"extracted."
            )

            if duplicates:
                message += (
                    f" {duplicates} duplicate "
                    f"services were skipped."
                )

            if invalid_rows:
                message += (
                    f" {invalid_rows} invalid rows "
                    f"were skipped."
                )

            if conflicts:
                message += (
                    f" {len(conflicts)} conflicting "
                    f"duplicate services require "
                    f"review."
                )

            print(
                f"[PRICE LIST] Import finished. "
                f"Batch ID={batch.id}, "
                f"inserted={inserted}",
                flush=True,
            )

            return (
                True,
                message,
                batch.id,
            )

        except Exception as error:
            print(
                f"[PRICE LIST] Processing failed: "
                f"{type(error).__name__}: "
                f"{error}",
                flush=True,
            )

            return (
                False,
                (
                    "Could not process the uploaded "
                    "price list: "
                    f"{type(error).__name__}: "
                    f"{error}"
                ),
                batch.id if batch else None,
            )

        finally:
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)

                    print(
                        f"[PRICE LIST] Temporary "
                        f"file removed: "
                        f"{stored_name}",
                        flush=True,
                    )

                except OSError as cleanup_error:
                    print(
                        f"[PRICE LIST] Could not "
                        f"remove temporary file: "
                        f"{cleanup_error}",
                        flush=True,
                    )

    @staticmethod
    def update_item(
        item_id,
        form_data,
    ):
        item = PriceListRepository.get_by_id(
            item_id
        )

        if not item:
            return (
                False,
                "Price list item not found.",
            )

        editable, error_message = (
            PriceListService
            ._is_editable_batch(
                item.batch
            )
        )

        if not editable:
            return (
                False,
                error_message,
            )

        service_name = (
            PriceListService
            ._normalize_service_name(
                form_data.get(
                    "service_name",
                    "",
                )
            )
        )

        approved_price = (
            PriceListService
            ._to_decimal(
                form_data.get(
                    "approved_price"
                )
            )
        )

        if not service_name:
            return (
                False,
                "Service name is required.",
            )

        if approved_price is None:
            return (
                False,
                (
                    "Approved price is required "
                    "and must be numeric."
                ),
            )

        if approved_price <= 0:
            return (
                False,
                (
                    "Approved price must be "
                    "greater than zero."
                ),
            )

        duplicate = (
            PriceListRepository
            .get_by_batch_and_service(
                batch_id=item.batch_id,
                service_name=service_name,
            )
        )

        if (
            duplicate
            and duplicate.id != item.id
        ):
            return (
                False,
                (
                    "This service already exists "
                    "in this price list."
                ),
            )

        PriceListRepository.update(
            item=item,
            service_name=service_name,
            approved_price=approved_price,
        )

        return (
            True,
            "Service price updated.",
        )

    @staticmethod
    def delete_item(item_id):
        item = PriceListRepository.get_by_id(
            item_id
        )

        if not item:
            return (
                False,
                "Price list item not found.",
                None,
            )

        editable, error_message = (
            PriceListService
            ._is_editable_batch(
                item.batch
            )
        )

        if not editable:
            return (
                False,
                error_message,
                item.batch_id,
            )

        batch_id = item.batch_id

        PriceListRepository.delete(
            item
        )

        return (
            True,
            "Service removed from price list.",
            batch_id,
        )

    @staticmethod
    def approve_batch(batch_id):
        batch = (
            PriceListBatchRepository
            .get_by_id(
                batch_id
            )
        )

        if not batch:
            return (
                False,
                "Price list batch not found.",
            )

        if batch.status == "APPROVED":
            return (
                False,
                (
                    "This price list is already "
                    "approved."
                ),
            )

        if batch.status == "REJECTED":
            return (
                False,
                (
                    "A rejected price list "
                    "cannot be approved."
                ),
            )

        items = (
            PriceListRepository
            .get_by_batch(
                batch_id
            )
        )

        if not items:
            return (
                False,
                (
                    "Cannot approve an empty "
                    "price list."
                ),
            )

        PriceListBatchRepository.approve(
            batch
        )

        return (
            True,
            "Price list approved and activated.",
        )

    @staticmethod
    def reject_batch(batch_id):
        batch = (
            PriceListBatchRepository
            .get_by_id(
                batch_id
            )
        )

        if not batch:
            return (
                False,
                "Price list batch not found.",
            )

        if batch.status == "APPROVED":
            return (
                False,
                (
                    "An approved price list "
                    "cannot be rejected."
                ),
            )

        if batch.status == "REJECTED":
            return (
                False,
                (
                    "This price list is already "
                    "rejected."
                ),
            )

        PriceListBatchRepository.reject(
            batch
        )

        return (
            True,
            "Price list rejected.",
        )

    @staticmethod
    def add_item_to_batch(
        batch_id,
        form_data,
    ):
        batch = (
            PriceListBatchRepository
            .get_by_id(
                batch_id
            )
        )

        editable, error_message = (
            PriceListService
            ._is_editable_batch(
                batch
            )
        )

        if not editable:
            return (
                False,
                error_message,
            )

        service_name = (
            PriceListService
            ._normalize_service_name(
                form_data.get(
                    "service_name",
                    "",
                )
            )
        )

        approved_price = (
            PriceListService
            ._to_decimal(
                form_data.get(
                    "approved_price"
                )
            )
        )

        if not service_name:
            return (
                False,
                "Service name is required.",
            )

        if approved_price is None:
            return (
                False,
                (
                    "Approved price is required "
                    "and must be numeric."
                ),
            )

        if approved_price <= 0:
            return (
                False,
                (
                    "Approved price must be "
                    "greater than zero."
                ),
            )

        existing = (
            PriceListRepository
            .get_by_batch_and_service(
                batch_id=batch.id,
                service_name=service_name,
            )
        )

        if existing:
            return (
                False,
                (
                    "This service already exists "
                    "in this price list."
                ),
            )

        PriceListRepository.create(
            batch_id=batch.id,
            institution_id=(
                batch.institution_id
            ),
            service_name=service_name,
            approved_price=approved_price,
        )

        return (
            True,
            "Service added successfully.",
        )