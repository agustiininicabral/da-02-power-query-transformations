let
    // Replace this path with the absolute path to this repository's raw CSV.
    SalesFilePath = "C:\\REPLACE\\PATH\\TO\\02-data\\raw\\sales.csv",
    Source = Csv.Document(
        File.Contents(SalesFilePath),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),
    PromotedHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    TrimmedText = Table.TransformColumns(
        PromotedHeaders,
        {
            {"order_id", each if _ = null then null else Text.Trim(Text.From(_)), type nullable text},
            {"customer_id", each if _ = null then null else Text.Trim(Text.From(_)), type nullable text},
            {"category", each if _ = null then null else Text.Trim(Text.From(_)), type nullable text},
            {"channel", each if _ = null then null else Text.Trim(Text.From(_)), type nullable text},
            {"country", each if _ = null then null else Text.Trim(Text.From(_)), type nullable text},
            {"city", each if _ = null then null else Text.Trim(Text.From(_)), type nullable text},
            {"payment_method", each if _ = null then null else Text.Trim(Text.From(_)), type nullable text},
            {"device", each if _ = null then null else Text.Trim(Text.From(_)), type nullable text}
        }
    ),
    Typed = Table.TransformColumns(
        TrimmedText,
        {
            {"order_date", each try Date.FromText(Text.From(_), [Format = "yyyy-MM-dd", Culture = "en-US"]) otherwise null, type nullable date},
            {"quantity", each try Int64.From(Number.FromText(Text.From(_), "en-US")) otherwise null, Int64.Type},
            {"unit_price", each try Number.FromText(Text.From(_), "en-US") otherwise null, type nullable number},
            {"discount_rate", each try Number.FromText(Text.From(_), "en-US") otherwise null, type nullable number},
            {"net_revenue", each try Number.FromText(Text.From(_), "en-US") otherwise null, type nullable number},
            {"cost", each try Number.FromText(Text.From(_), "en-US") otherwise null, type nullable number}
        }
    ),
    AddedExpectedRevenue = Table.AddColumn(
        Typed,
        "expected_net_revenue",
        each if [quantity] = null or [unit_price] = null or [discount_rate] = null
             then null
             else Number.Round([quantity] * [unit_price] * (1 - [discount_rate]), 2),
        type nullable number
    ),
    AddedRevenueCheck = Table.AddColumn(
        AddedExpectedRevenue,
        "revenue_check",
        each [net_revenue] <> null and [expected_net_revenue] <> null
             and Number.Abs([net_revenue] - [expected_net_revenue]) <= 0.01,
        type logical
    ),
    RequiredFields = {
        "order_id", "customer_id", "order_date", "category", "channel",
        "quantity", "unit_price", "discount_rate", "net_revenue", "cost"
    },
    AddedQualityStatus = Table.AddColumn(
        AddedRevenueCheck,
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
                else if [quantity] <= 0 then "Quantity must be positive"
                else if [unit_price] < 0 or [cost] < 0 or [net_revenue] < 0 then "Negative amount"
                else if [discount_rate] < 0 or [discount_rate] > 0.20 then "Discount outside 0-20%"
                else if not [revenue_check] then "Net revenue mismatch"
                else "OK",
        type text
    )
in
    AddedQualityStatus
