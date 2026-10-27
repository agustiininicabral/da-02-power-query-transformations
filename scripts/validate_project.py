from __future__ import annotations

import csv
import math
from datetime import date
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SALES_HEADERS = {
    "order_id",
    "customer_id",
    "order_date",
    "category",
    "channel",
    "country",
    "city",
    "quantity",
    "unit_price",
    "discount_rate",
    "net_revenue",
    "cost",
    "payment_method",
    "device",
}
PRODUCT_HEADERS = {"product_id", "product_name", "category", "brand", "active"}
M_QUERY_DEPENDENCIES = {
    "SalesPrepared.m": (),
    "SalesValid.m": ("SalesPrepared",),
    "SalesExceptions.m": ("SalesPrepared",),
    "ProductsPrepared.m": (),
    "ProductsValid.m": ("ProductsPrepared",),
    "ProductsExceptions.m": ("ProductsPrepared",),
}
M_QUERY_RULES = {
    "SalesPrepared.m": ("DuplicateOrderIds", "is_duplicate_order_id", "quality_status"),
    "ProductsPrepared.m": ("DuplicateProductIds", "is_duplicate_product_id", "quality_status"),
    "SalesValid.m": ("is_duplicate_order_id",),
    "ProductsValid.m": ("is_duplicate_product_id",),
}


def _read_csv(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        if not reader.fieldnames:
            return [], []
        return list(reader), [field.strip() for field in reader.fieldnames]


def validate_project(
    root: Path = ROOT,
    expected_sales_rows: int = 3500,
    expected_product_rows: int = 500,
) -> dict[str, Any]:
    errors: list[str] = []
    sales_path = root / "02-data" / "raw" / "sales.csv"
    products_path = root / "02-data" / "raw" / "products.csv"
    sales, sales_headers = _read_csv(sales_path)
    products, product_headers = _read_csv(products_path)

    if len(sales) != expected_sales_rows:
        errors.append(f"Expected {expected_sales_rows} sales rows, found {len(sales)}")
    if len(products) != expected_product_rows:
        errors.append(f"Expected {expected_product_rows} product rows, found {len(products)}")
    for missing in sorted(SALES_HEADERS - set(sales_headers)):
        errors.append(f"Sales CSV missing required column: {missing}")
    for missing in sorted(PRODUCT_HEADERS - set(product_headers)):
        errors.append(f"Products CSV missing required column: {missing}")

    if SALES_HEADERS.issubset(sales_headers):
        if any(
            not (row.get(field) or "").strip()
            for row in sales
            for field in SALES_HEADERS
        ):
            errors.append("Sales CSV contains blank required values")
        order_ids = [row["order_id"] for row in sales]
        if len(order_ids) != len(set(order_ids)):
            errors.append("Sales CSV contains duplicate order_id values")

        for row_number, row in enumerate(sales, start=2):
            try:
                date.fromisoformat(row["order_date"])
            except (TypeError, ValueError):
                errors.append(f"Sales row {row_number} has invalid order_date")
                continue
            try:
                quantity = int(row["quantity"])
                unit_price = float(row["unit_price"])
                discount_rate = float(row["discount_rate"])
                net_revenue = float(row["net_revenue"])
                cost = float(row["cost"])
            except (TypeError, ValueError):
                errors.append(f"Sales row {row_number} has invalid numeric data")
                continue
            if not all(
                math.isfinite(value)
                for value in (unit_price, discount_rate, net_revenue, cost)
            ):
                errors.append(f"Sales row {row_number} has non-finite numeric data")
                continue
            if quantity <= 0:
                errors.append(f"Sales row {row_number} quantity must be positive")
            if unit_price < 0 or net_revenue < 0 or cost < 0:
                errors.append(f"Sales row {row_number} has a negative amount")
            if not 0 <= discount_rate <= 0.20:
                errors.append(f"Sales row {row_number} discount outside 0..0.20")
            if (
                abs(net_revenue - round(quantity * unit_price * (1 - discount_rate), 2))
                > 0.011
            ):
                errors.append(f"Sales row {row_number} has inconsistent net_revenue")

    if PRODUCT_HEADERS.issubset(product_headers):
        product_ids = [row["product_id"] for row in products]
        if len(product_ids) != len(set(product_ids)):
            errors.append("Products CSV contains duplicate product_id values")
        if any(
            not (row.get(field) or "").strip()
            for row in products
            for field in PRODUCT_HEADERS
        ):
            errors.append("Products CSV contains blank required values")
        if any(row["active"].strip().lower() not in {"yes", "no"} for row in products):
            errors.append("Products CSV has active values other than Yes/No")
        if SALES_HEADERS.issubset(sales_headers):
            sales_categories = {row["category"] for row in sales}
            product_categories = {row["category"] for row in products}
            missing_categories = sorted(sales_categories - product_categories)
            if missing_categories:
                errors.append(
                    "Sales categories missing from product catalog: "
                    + ", ".join(missing_categories)
                )

    for filename, dependencies in M_QUERY_DEPENDENCIES.items():
        path = root / "03-work" / "power-query" / filename
        if not path.is_file():
            errors.append(f"Missing Power Query file: {path.relative_to(root)}")
            continue
        content = path.read_text(encoding="utf-8")
        if not content.lstrip().startswith("let") or "\nin" not in content:
            errors.append(f"Power Query file lacks a let/in structure: {filename}")
        for dependency in dependencies:
            if dependency not in content:
                errors.append(f"{filename} must reference query {dependency}")
        for required_rule in M_QUERY_RULES.get(filename, ()):
            if required_rule not in content:
                errors.append(f"{filename} missing required rule: {required_rule}")
    sales_prepared = (root / "03-work" / "power-query" / "SalesPrepared.m").read_text(
        encoding="utf-8"
    )
    for required_step in ("expected_net_revenue", "revenue_check", "quality_status"):
        if required_step not in sales_prepared:
            errors.append(f"SalesPrepared.m missing validation step: {required_step}")

    return {
        "sales_rows": len(sales),
        "product_rows": len(products),
        "errors": errors,
    }


def main() -> int:
    result = validate_project()
    print(f"Sales rows: {result['sales_rows']}")
    print(f"Product rows: {result['product_rows']}")
    if result["errors"]:
        for error in result["errors"]:
            print(f"ERROR: {error}")
        return 1
    print("PASS - CSV datasets and Power Query asset contracts are consistent.")
    print("Note: this static check does not execute Power Query M.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
