let
    Source = Csv.Document(File.Contents(DataFolder & "\FactOutcomes.csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    Typed = Table.TransformColumnTypes(Headers, {{"activity_year", type text}, {"state_code", type text}, {"n1", Int64.Type}, {"n2", Int64.Type}, {"n3", Int64.Type}, {"n4", Int64.Type}, {"n5", Int64.Type}, {"n6", Int64.Type}, {"n7", Int64.Type}, {"n8", Int64.Type}, {"lei", type text}, {"loan_type", type text}, {"applications", Int64.Type}, {"decisions", Int64.Type}, {"approvals", Int64.Type}, {"lender_key", type text}}, "en-US")
in
    Typed
