let
    Source = Csv.Document(File.Contents(DataFolder & "\StatewideCoverage.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Headers, {{"field", type text}, {"value_status", type text}, {"numerator", Int64.Type}, {"denominator", Int64.Type}, {"share", type number}}, "en-US")
in
    Typed
