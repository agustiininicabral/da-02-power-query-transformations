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
    GroupedProductIds = Table.Group(
        TrimmedText,
        {"product_id"},
        {{"product_count", each Table.RowCount(_), Int64.Type}}
    ),
    DuplicateProductIds = Table.SelectRows(GroupedProductIds, each [product_count] > 1),
    MergedDuplicateProducts = Table.NestedJoin(
        TrimmedText, {"product_id"}, DuplicateProductIds, {"product_id"},
        "duplicate_product", JoinKind.LeftOuter
    ),
    AddedDuplicateFlag = Table.AddColumn(
        MergedDuplicateProducts,
        "is_duplicate_product_id",
        each Table.RowCount([duplicate_product]) > 0,
        type logical
    ),
    RemovedDuplicateDetails = Table.RemoveColumns(AddedDuplicateFlag, {"duplicate_product"}),
    RequiredFields = {"product_id", "product_name", "category", "brand", "active"},
    AddedQualityStatus = Table.AddColumn(
        RemovedDuplicateDetails,
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
                else if [is_duplicate_product_id] then "Duplicate product_id"
                else if not List.Contains({"Yes", "No"}, [active]) then "active must be Yes or No"
                else "OK",
        type text
    )
in
    AddedQualityStatus
