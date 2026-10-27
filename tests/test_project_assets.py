from pathlib import Path

from scripts.validate_project import M_QUERY_DEPENDENCIES, validate_project


def test_committed_datasets_and_power_query_assets_are_consistent() -> None:
    result = validate_project()

    assert result["sales_rows"] == 3500
    assert result["product_rows"] == 500
    assert result["errors"] == []


def test_all_expected_m_queries_have_declared_dependencies() -> None:
    root = Path(__file__).resolve().parents[1]
    query_dir = root / "03-work" / "power-query"

    assert len(M_QUERY_DEPENDENCIES) == 6
    for filename, dependencies in M_QUERY_DEPENDENCIES.items():
        content = (query_dir / filename).read_text(encoding="utf-8")
        assert content.lstrip().startswith("let")
        assert "\nin" in content
        for dependency in dependencies:
            assert dependency in content
