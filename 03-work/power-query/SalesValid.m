let
    Source = SalesPrepared,
    ValidRows = Table.SelectRows(Source, each [quality_status] = "OK"),
    RemovedHelperColumns = Table.RemoveColumns(
        ValidRows,
        {"expected_net_revenue", "revenue_check", "quality_status", "is_duplicate_order_id"}
    )
in
    RemovedHelperColumns
