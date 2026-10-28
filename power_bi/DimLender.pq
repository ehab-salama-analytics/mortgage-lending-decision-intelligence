let
    Source = Csv.Document(File.Contents(DataFolder & "\DimLender.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Headers, {{"activity_year", type text}, {"lei", type text}, {"respondent_name", type text}, {"agency_code", type text}, {"lender_key", type text}}, "en-US")
in
    Typed
