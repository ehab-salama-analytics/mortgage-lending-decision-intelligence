# Reproduce the reporting pipeline

Outcome reporting update: `all` now builds and validates rates/coverage and generates the management brief and CSVs. `report` refreshes only the exports after fresh validation of saved analytical inputs. See [outcome reporting](outcome_reporting.md) for the grain, denominator and display rules. Generated reports are excluded from Git.

Current update: the runner also builds the lender dimension and outcome count table. Obtain the official snapshot TS ZIP at `data/raw/hmda_2025/reference/2025_public_ts_csv.zip` and the official filer JSON at `data/raw/hmda_2025/reference/official_filers.json`, using the links in [source reconciliation](source_reconciliation.md). That note supersedes historical pending statuses for official totals and lender names below. The source-reference validator runs before the outcome table is built. LTV semantics remain pending only for LTV-dependent work.

## Executed validation — 27 October 2026

The build and independent validator completed successfully for all 55,183 rows with no failed checks. The validator compared all 99 original field values per row, lineage, selected numeric parses, population flags and exclusion reconciliation. No invalid numeric tokens were found in the 11 parsed fields. Source warnings remain listed in [the validation result](evidence/staging_validation.json).

A second build and validation passed. SHA-256 comparisons of both Parquet outputs before and after the rebuild were identical. The main staging file is 2,542,384 bytes; the exclusion summary is 1,166 bytes. This verifies local reproducibility with the saved input and tested environment, not future source availability or production deployment.

Use a dedicated Python environment. Do not run or modify Project #1's environment. Direct dependency: Polars 1.44.2, matching Project #1's reviewed version. Python 3.13 is used locally.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.\.venv\Scripts\python.exe -X utf8 src/run_pipeline.py all
```

Obtain the original official CSV using [the source procedure](data_source_decision.md) and place it at `data/raw/hmda_2025/actions_taken_1-2-3-4-5-6-7-8_state_DE.csv`. Data are not included in Git. `config/source_contract.json` pins the reviewed SHA-256, row count, observed header, normalized names and cohort rule order. A new hash requires investigation and a new reviewed source version; do not bypass the check.

`build` overwrites generated staging files only. `validate` reads source and staged data and writes a validation report under `docs/evidence/`; it does not alter either dataset. `all` stops at the first failed stage.

Outputs:

- `data/staging/hmda_2025_de.parquet`: one row per original source record, all original values, selected numeric/status columns and population flags.
- `data/staging/cohort_exclusions.parquet`: first failed filter per row, or included. Filter order is documented in the contract. This is a mutually exclusive exclusion summary, not separate overlapping filter failure counts.
- `data/staging/source_manifest.json`: source hash, size, environment and known acquisition limitations.
- `docs/evidence/staging_validation.json`: validation result and status counts.

The independent validator uses the standard-library CSV reader and Decimal to reconstruct raw values and numeric status, rather than importing transformation functions. It compares every source cell, row lineage, all population flags and the exclusion summary. `NA` is preserved as the source's not-applicable token; this label does not establish whether the filer used it correctly. No missing values are imputed. Outlier handling and full categorical-domain validation remain future controls.

DTI, ages, categorical special codes and the unresolved LTV field remain strings at this milestone. Numeric parses distinguish blank, NA, Exempt, valid finite numeric and invalid tokens. Original units remain unchanged. Structural zeros and negative numbers are not silently discarded; business-validity checks belong in later field-specific validation.

Official summary reconciliation and lender-reference validation are complete. Remaining gates for future metrics: confirm the LTV alias before leverage KPIs and validate field-specific domains/applicability before additional underwriting or pricing analysis. Rebuilding staging does not refresh Power BI. No scheduling, distribution or deployed service is claimed.
