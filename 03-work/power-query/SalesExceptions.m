let
    Source = SalesPrepared,
    ExceptionRows = Table.SelectRows(Source, each [quality_status] <> "OK")
in
    ExceptionRows
