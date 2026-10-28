# Power BI dashboards

Completed and checked in Power BI Desktop on 2026-10-28. The public package includes `.pbip`, `.Report` and `.SemanticModel` folders with editable definitions. The local packaged PBIX and caches are not distributed. Set the DataFolder expression (currently `SET_DATA_FOLDER_BEFORE_REFRESH`) to the absolute path of your regenerated CSV directory before refreshing. Keep those project folders together.

## Pages

1. **Management overview**: product filter, application/decision/origination counts, seven outcome rates, application-volume chart and exact product counts.
2. **Lending outcomes**: lender and product filters, counts, denial rate and a lender-product table with denominator and rate status. Alphabetical ordering is not a performance ranking; differences in applicant and product composition remain unadjusted.
3. **Data quality — statewide**: source audit counts and field-status coverage for 10,623 cohort originations. This page deliberately stays statewide when other pages are filtered.

Large cards abbreviate counts in thousands; tables provide exact counts. Scroll tables to inspect all rows. Rates with a denominator below 30 (including zero) are blank; counts remain visible. This display rule is not a statistical or privacy guarantee. Use the slicer erasers to restore all products/lenders.

## Refresh and model

Run `python src/run_pipeline.py report` with the project interpreter to validate and regenerate the management report and CSV inputs under `reports/generated/power_bi/`. The `all` command includes this export. Then refresh the report in Desktop; running Python does not refresh an open report automatically. Update the model's DataFolder expression when moving the project.

The fact table contains 627 lender-product rows, without overlapping statewide rollups. Four tables, two single-direction relationships and 20 measures implement the model:

- DimLender lender_key → FactOutcomes lender_key (year plus LEI).
- DimProduct loan_type → FactOutcomes loan_type.
- StatewideCoverage is disconnected; no lender/product slicers appear on its page.

The saved project is the preferred editable source. `CreateModel.tmdl`, the `.pq` files and `Measures.dax` are reviewable bootstrap definitions. Apply the create-or-replace script only to a new report for this project. `src/build_dashboard_layout.py` regenerates page layouts and overwrites page definitions; preserve manual edits before using it.

Respondent names are labels, not corporate-group identifiers. The source reference has one duplicate name across two LEIs, neither present in the selected cohort. Future cohorts should disambiguate such labels with LEI.

## Validation

Independent raw-CSV checks reconcile analytical counts/rates and coverage before export. Desktop DAX checks reconciled 14,076 applications, 11,869 decisions, 10,859 approvals, 10,623 originations and 1,010 denials. Denial rate is 8.50956273%; approval rate 91.49043727%; origination share 75.46888321%.

Visual checks passed for all three pages, conventional-only filtering, conventional plus FHA selection, lender filtering, combined lender/product filtering, small groups, empty intersections, clearing filters and statewide-quality independence. See `../docs/evidence/power_bi_desktop_validation.json` and the three dashboard screenshots. Bar cross-highlighting, PDF export and Power BI Service deployment were not tested.

## Scope and future work

The report describes 2025 Delaware HMDA observed outcomes for the documented home-purchase cohort. It does not measure subsequent defaults, recommend applicant decisions, establish discrimination, or describe Luxembourg conditions. Public-data privacy modifications and missing/exempt fields constrain interpretation. LTV remains excluded pending semantic confirmation.

Pricing analysis, denial-reason reporting, adjusted comparisons, scheduled refresh are future enhancements. PBIX files and local caches are excluded from Git; publish source definitions, validation evidence and the case study only after publication review.
