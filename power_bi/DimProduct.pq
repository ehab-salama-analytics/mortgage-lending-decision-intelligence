let
    Source = Csv.Document(File.Contents(DataFolder & "\DimProduct.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Headers, {{"loan_type", type text}, {"product_name", type text}}, "en-US")
in
    Typed
