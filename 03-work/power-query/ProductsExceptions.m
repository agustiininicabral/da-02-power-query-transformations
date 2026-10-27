let
    Source = ProductsPrepared,
    ExceptionRows = Table.SelectRows(Source, each [quality_status] <> "OK")
in
    ExceptionRows
