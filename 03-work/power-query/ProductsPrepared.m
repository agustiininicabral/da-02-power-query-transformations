let
    // Replace this path with the absolute path to this repository's raw CSV.
    ProductsFilePath = "C:\REPLACE\PATH\TO\02-data\raw\products.csv",
    Source = Csv.Document(
        File.Contents(ProductsFilePath),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    TrimmedText = Table.TransformColumns(
        PromotedHeaders,
        {
            {"product_id", each if _ = null then null else Text.Trim(Text.From(_)), type nullable text},
            {"product_name", each if _ = null then null else Text.Trim(Text.From(_)), type nullable text},
            {"category", each if _ = null then null else Text.Trim(Text.From(_)), type nullable text},
            {"brand", each if _ = null then null else Text.Trim(Text.From(_)), type nullable text},
            {"active", each if _ = null then null else Text.Proper(Text.Trim(Text.From(_))), type nullable text}
        }
    ),
    RequiredFields = {"product_id", "product_name", "category", "brand", "active"},
    AddedQualityStatus = Table.AddColumn(
        TrimmedText,
        "quality_status",
        each
            let
                currentRow = _,
                missing = List.AnyTrue(
                    List.Transform(
                        RequiredFields,
                        (fieldName) =>
                            let value = Record.Field(currentRow, fieldName)
                            in value = null or (Value.Is(value, type text) and Text.Trim(value) = "")
                    )
                )
            in
                if missing then "Missing required fields"
                else if not List.Contains({"Yes", "No"}, [active]) then "active must be Yes or No"
                else "OK",
        type text
    )
in
    AddedQualityStatus
