# Data source decision

Current status update: [source reconciliation](source_reconciliation.md) confirms all action counts/amounts and snapshot TS coverage for all 558 LEIs. Earlier pending acquisition checks below describe the Phase 0 checkpoint.

Verified 27 October 2026. Selected: **2025 HMDA public LAR, Delaware, all lenders and actions 1–8**, exported through the official [Data Browser](https://ffiec.cfpb.gov/data-browser/data/2025?category=states&items=DE&actions_taken=1,2,3,4,5,6,7,8).

## Version and availability

The Data Browser visibly identifies its 2025 source as the Snapshot. The [snapshot publication page](https://ffiec.cfpb.gov/data-publication/snapshot-national-loan-level-dataset/2025) displays freeze date **June 2, 2026** and file update date **June 23, 2026**. The [FFIEC release announcement](https://www.ffiec.gov/news/press-releases/2026/an-06-23) instead describes data as of June 1. Retain this discrepancy; use the dataset page's June 2 label without claiming the dates are identical.

The [static dataset FAQ](https://ffiec.cfpb.gov/documentation/faq/static-dataset-faq) says Data Browser uses the latest static vintage for each year. A later repeat of the same URL may therefore use a different vintage. The local source hash is essential.

Official download links observed on the publication page:

- [National LAR CSV ZIP](https://files.ffiec.cfpb.gov/static-data/snapshot/2025/2025_public_lar_csv.zip)
- [Transmittal Sheet CSV ZIP](https://files.ffiec.cfpb.gov/static-data/snapshot/2025/2025_public_ts_csv.zip)

The national LAR is marked as a large file. Its byte size was not obtained, and it was not downloaded. The page says the Reporter Panel is no longer produced; do not assume a 2025 panel is available. Obtain lender names from the same-vintage TS or official filer lookup, checking one row per year/LEI before joining.

## Cohort choice and cost

| Option | Assessment |
|---|---|
| Delaware, all lenders | Selected: bounded statewide coverage, lender diversity and a small verified local file; supports complete reported state populations without lender selection bias. |
| Rhode Island or Maryland | Valid geographic alternatives, but their counts and completeness were not verified. No numerical cost comparison is claimed. |
| One lender nationwide | Narrower institution story; weak initial basis for within-market lender comparison. |
| Entire US | Unnecessary initial transfer/storage cost; official large-file warning. |

Received file: `data/raw/hmda_2025/actions_taken_1-2-3-4-5-6-7-8_state_DE.csv`.
Confirmed **55,183 rows, 99 columns, 558 distinct LEIs, 20,985,669 bytes (20.01 MiB)**. All rows are DE/2025. This is a full-population extraction intention, not yet independently proven complete against the official summary count. HMDA reporting coverage itself is not the entire mortgage market.

SHA-256: `c7bc1365d5e76ffb7937093385acb7d044a647d62d853832cf2f6a3347f13dcc`.

## Acquisition procedure

1. Record year, source vintage and exact filters before download. Select DE, all institutions, all eight actions, no additional filters.
2. Retrieve the official summary by action and preserve its response/date. Use the [documented aggregation API](https://ffiec.cfpb.gov/documentation/api/data-browser/) with `states=DE&years=2025&actions_taken=1,2,3,4,5,6,7,8`; use `/view/csv` for the corresponding CSV.
3. Save the original download unchanged. Record URL, UTC receipt time, download method, bytes, SHA-256 and schema. Write new vintages to new paths; never overwrite raw inputs.
4. Check CSV structure, year, state, action counts and row total against the independent source summary. A valid header alone is insufficient.
5. Acquire the small TS reference when available; preserve it separately and validate LEI join coverage. Then stage locally using Polars/Parquet.

This acquisition was user-assisted on 27 October 2026 after automated API requests and file HEAD requests returned access errors/HTTP 403. The original server response headers and exact download time were not captured. The file's filesystem time is not a server publication timestamp. Raw contents are preserved; current evidence is in [raw_profile.json](evidence/raw_profile.json).
