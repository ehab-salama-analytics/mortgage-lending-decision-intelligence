# Source reconciliation and first reporting table

Verified 27 October 2026. This note supersedes earlier pending statuses for official totals and lender names.

The official Data Browser summary for DE/2025, all institutions and actions 1–8, matches the local CSV on all eight action counts **and all eight disclosed amount totals**. Total: 55,183 records. The visible page was saved in `docs/evidence/official_summary_browser.txt`; its transcribed controls are in `config/official_action_totals.json`. This verifies aggregate extraction completeness against that published summary, not the truth of every filed value.

The official filer API returned 549 institutions and 55,139 records. Nine source LEIs covering 44 records were absent. The matching 2025 snapshot Transmittal Sheet contains 4,782 national institutions and supplies names for **all 558 Delaware LEIs**. The cause of the filer-lookup discrepancy is not established. Use the snapshot TS for the dimension; preserve the API response as diagnostic evidence.

The dimension has one row per activity year/LEI and retains respondent name and supervisory agency code. Agency code is not a bank/nonbank classification. The TS's national `lar_count` is not Delaware activity and is excluded. The archived reference is hash-pinned in `config/lender_reference_contract.json`.

Sources: [official summary](https://ffiec.cfpb.gov/data-browser/data/2025?category=states&items=DE&actions_taken=1,2,3,4,5,6,7,8&getDetails=1), [filer lookup](https://ffiec.cfpb.gov/v2/data-browser-api/view/filers?states=DE&years=2025), [snapshot TS](https://files.ffiec.cfpb.gov/static-data/snapshot/2025/2025_public_ts_csv.zip). Browser access succeeded after direct requests returned HTTP 403. The filer JSON was saved from the rendered response; the ZIP was downloaded unchanged.

## Outcome count table

`data/analytical/outcome_counts.parquet` contains **2,371 aggregate rows representing 20,175 cohort records**. Grain: activity year × state × county × LEI × loan type × action. Missing county remains `NA`. The cohort definition is unchanged. Purchases and standalone preapprovals are retained as separate actions; filter actions 1–5 for applications, 1–3 for decisions and 1 for originations. Counts are additive; percentages must be calculated from aggregated numerators/denominators, never averaged across rows.

Every aggregate cell was independently reconstructed from the raw CSV with the standard-library reader: PASS. These are reporting inputs, not lender rankings or adjusted performance comparisons. No LTV, demographic or pricing metric is implemented here. The LTV export alias remains unresolved and is not needed for this table.

Validation evidence: `docs/evidence/source_reference_validation.json` and `docs/evidence/outcome_counts_validation.json`. Completed subsequently: validated outcome rates, coverage, management exports and Power BI pages; see [reporting methodology](outcome_reporting.md).
