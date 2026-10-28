# Outcome reporting milestone

The outcome tables use the previously defined property/product cohort. Each rate stores its numerator, denominator and display status. Denominator zero returns `no_population`; 1–29 returns `small_population`; both have a null display rate. Counts are retained. This is a project presentation rule, not a confidentiality mechanism or proof of statistical significance.

| Metric | Numerator | Denominator |
|---|---|---|
| denial_rate | Action 3 | Actions 1+2+3 |
| approval_rate | Actions 1+2 | Actions 1+2+3 |
| origination_share | Action 1 | Actions 1–5 |
| withdrawal_share | Action 4 | Actions 1–5 |
| incomplete_share | Action 5 | Actions 1–5 |
| approved_not_accepted_share | Action 2 | Actions 1+2 |

There are 3,792 rate rows across statewide, statewide-product and lender-product scopes. These scopes overlap. Never aggregate across scope values. The lender-product view describes observed outcomes without ranking lenders or adjusting for applicant composition. Join the lender dimension on year and LEI only for lender-product rows; ALL marks aggregate rows.

`outcome_populations.parquet` supplies action counts and population totals. Aggregate counts within one scope first, then compute a rate and reapply the minimum denominator. Do not average rates, or add denominators across metrics. No county filter should be applied to the rates table, which has no county grain; use the county-grain outcome count table to derive new measures instead.

`origination_field_coverage.parquet` has 35 rows: seven fields × five statuses (numeric, blank, not applicable, exempt, invalid), among 10,623 cohort originations. Every field's status counts sum to that population. Coverage is numeric availability, not a reporting-compliance or economic-validity judgment. Blank discount points or lender credits are not automatically zero. No pricing comparison is published yet.

## Executed controls — 27 October 2026

All 3,792 rate rows and 35 coverage rows passed independent reconstruction directly from the raw CSV. Checks cover exact keys, numerator, denominator, null/display status, action counts and status shares. Display results: 549 reported rates, 2,903 small-population rates withheld and 340 no-population cases. Details: `docs/evidence/outcome_rates_validation.json`.

## Generated exports

Run `python src/run_pipeline.py report` using the project environment after a successful build, or use `all` to build, validate and export. The report command freshly validates source/reference, outcome counts and outcome rates before exporting. It writes:

- `reports/generated/management_brief.md`
- Four CSVs: outcome_rates, outcome_populations, origination_field_coverage and dim_lender
- `reports/generated/export_manifest.json` with source fingerprint and output hashes

Exports are local generated artifacts, excluded from Git. Preserve source and validation code in the future repository. This delivers repeatable local report generation; it does not schedule reports, refresh Power BI or distribute messages.

Completed: the Power BI semantic model and three dashboard pages use these validated denominators; see [dashboard guide](../power_bi/README.md). Future pricing and denial-reason reporting need their own field-specific controls. LTV remains excluded pending semantic confirmation.
