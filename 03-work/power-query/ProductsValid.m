let
    Source = ProductsPrepared,
    ValidRows = Table.SelectRows(Source, each [quality_status] = "OK"),
    RemovedHelperColumns = Table.RemoveColumns(ValidRows, {"quality_status", "is_duplicate_product_id"})
in
    RemovedHelperColumns
