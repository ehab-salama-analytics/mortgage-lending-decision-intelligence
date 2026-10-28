# Mortgage Lending Decision Intelligence & Automated Reporting

QuantRisk Analytics — Project #2. Delivered MVP: 28 October 2026.

Build a reproducible management-reporting case around observed mortgage applications and originations. Intended users are mortgage operations managers, lending analysts and reporting teams. This complements Project #1's institution-level bank monitoring with application-level populations, outcome reporting and data-quality controls.

## MVP

- ANALYSE: 2025 HMDA Delaware records across all reporting lenders; documented application, decision and origination populations; outcome summaries, underwriting/pricing field-availability controls and descriptive lender views with explicit denominators. Pricing levels and adjusted comparisons are future work.
- AUTOMATE: preserved source, Python/Polars transformations to Parquet, independently checked aggregates, repeatable report-ready exports and a generated management summary with run metadata. Power BI refresh must be tested separately.
- TRAIN: concise reproduction guide and a worked explanation of populations, exclusions and interpretation.
- Deliver three compact Power BI views: management overview, lending outcomes/lender comparison, and data quality. Publish a professional GitHub case study only after validation and review.

Primary analytical cohort: Delaware property location; home purchase; first lien; principal residence; site-built; 1–4 units; explicitly non-reverse, closed-end and non-business purpose. Retain all loan types and show their composition. Preserve the full state extract for reconciliation. Definitions and exceptions are in [the schema/KPI plan](docs/initial_schema_and_kpi_plan.md).

## Boundaries

HMDA records applications and lending outcomes, not subsequent defaults or repayment. No default prediction, individual approval recommendation or applicant scoring. Demographic comparisons are descriptive; they do not establish causation or discrimination. US evidence does not establish Luxembourg market conditions. Applications are not unique people, and annual outcomes are not a dated application funnel.

## Delivery gates

1. Source and raw inspection: file received and profiled; official totals and snapshot lender names reconciled. Ratio-field alias confirmation remains open for LTV-dependent work. See [current reconciliation](docs/source_reconciliation.md).
2. Implement isolated environment, explicit field mapping, lossless staging and population flags. Independently reconcile rows and exclusions before producing KPIs.
3. Validate aggregate marts and automated management summary; then build and test Power BI.
4. Rebuild from raw inputs, review report filters and claims, and prepare publication.

Acceptance: no unexplained lost or multiplied rows; every rate carries numerator, denominator and coverage; zero denominator returns unavailable; warnings are visible; a second run reproduces outputs from the same source hash.

Future enhancements: pricing and denial-reason summaries, more states/years, lender-type enrichment, composition-standardized comparisons, deployment/scheduling and report distribution. DuckDB is optional if useful for independent reconciliation. No predictive modelling is required.

## Project layout

The user supplied data in the existing `Project_02_Mortgage_Analytics` folder; this is the working project home. Do not create a second competing `Project_02_Mortgage_Lending` tree. Project #1 and its Git repository remain outside this project's write scope.

```text
PROJECT_CHARTER.md
docs/                         # source decision, KPI plan, findings
docs/evidence/                # profiles, manifests, validation results
data/raw/hmda_2025/           # immutable downloaded CSV and reference files
data/staging/                # lossless typed Parquet, quality flags
data/analytical/             # population and aggregate reporting tables
src/acquisition/             # bounded download and provenance recording
src/transformation/          # reproducible build
src/validation/              # separate read-only checks
reports/                     # generated management summary
power_bi/                    # report project and measures
```

Only directories needed now are created. Raw and generated datasets should remain outside the eventual public Git history.
