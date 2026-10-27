import csv
import shutil
from pathlib import Path

from scripts.validate_project import (
    M_QUERY_DEPENDENCIES,
    PRODUCT_HEADERS,
    SALES_HEADERS,
    validate_project,
)

ROOT = Path(__file__).resolve().parents[1]


def test_committed_datasets_and_power_query_assets_are_consistent() -> None:
    result = validate_project()

    assert result["sales_rows"] == 3500
    assert result["product_rows"] == 500
    assert result["errors"] == []


def test_all_expected_m_queries_have_declared_dependencies() -> None:
    query_dir = ROOT / "03-work" / "power-query"

    assert len(M_QUERY_DEPENDENCIES) == 6
    for filename, dependencies in M_QUERY_DEPENDENCIES.items():
        content = (query_dir / filename).read_text(encoding="utf-8")
        assert content.lstrip().startswith("let")
        assert "\nin" in content
        for dependency in dependencies:
            assert dependency in content


def test_validator_flags_bad_dates_negative_amounts_and_duplicate_ids(
    tmp_path: Path,
) -> None:
    data_dir = tmp_path / "02-data" / "raw"
    data_dir.mkdir(parents=True)
    shutil.copytree(
        ROOT / "03-work" / "power-query",
        tmp_path / "03-work" / "power-query",
    )

    sales = [
        {
            "order_id": "O1",
            "customer_id": "C1",
            "order_date": "not-a-date",
            "category": "Higiene",
            "channel": "Email",
            "country": "AR",
            "city": "Buenos Aires",
            "quantity": "1",
            "unit_price": "10",
            "discount_rate": "0",
            "net_revenue": "10",
            "cost": "5",
            "payment_method": "Card",
            "device": "Mobile",
        },
        {
            "order_id": "O1",
            "customer_id": "C2",
            "order_date": "2025-01-02",
            "category": "Higiene",
            "channel": "Email",
            "country": "AR",
            "city": "Buenos Aires",
            "quantity": "1",
            "unit_price": "-10",
            "discount_rate": "0",
            "net_revenue": "-10",
            "cost": "5",
            "payment_method": "Card",
            "device": "Mobile",
        },
    ]
    products = [
        {
            "product_id": "P1",
            "product_name": "Demo",
            "category": "Higiene",
            "brand": "Demo",
            "active": "Yes",
        }
    ]

    with (data_dir / "sales.csv").open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=sorted(SALES_HEADERS))
        writer.writeheader()
        writer.writerows(sales)
    with (data_dir / "products.csv").open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=sorted(PRODUCT_HEADERS))
        writer.writeheader()
        writer.writerows(products)

    result = validate_project(
        tmp_path,
        expected_sales_rows=2,
        expected_product_rows=1,
    )

    assert any("duplicate order_id" in error.lower() for error in result["errors"])
    assert any("invalid order_date" in error for error in result["errors"])
    assert any("negative amount" in error for error in result["errors"])
