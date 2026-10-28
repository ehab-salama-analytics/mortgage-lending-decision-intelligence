# Phase 0 findings — 27 October 2026

## Checkpoint

Source selected and real CSV inspected: **2025 HMDA Snapshot via Data Browser, Delaware, all lenders and outcomes**. Published vintage and acquisition evidence: [source decision](data_source_decision.md). MVP and future scope: [charter](../PROJECT_CHARTER.md).

| Raw-file check | Result |
|---|---:|
| Records / fields | 55,183 / 99 |
| Bytes | 20,985,669 |
| Distinct lender LEIs | 558 |
| Rows marked DE and 2025 | 55,183 |
| Malformed CSV rows | 0 |
| County `NA` | 429 |
| Repeated identical public-row occurrences beyond first | 104; retained |

| Action | State extract | Proposed property/product cohort C |
|---|---:|---:|
| 1 Originated | 27,033 | 10,623 |
| 2 Approved, not accepted | 1,161 | 236 |
| 3 Denied | 8,294 | 1,010 |
| 4 Withdrawn | 6,159 | 1,970 |
| 5 Incomplete | 3,025 | 237 |
| 6 Purchased | 9,226 | 5,840 |
| 7 Preapproval denied | 35 | 32 |
| 8 Preapproval approved, not accepted | 250 | 227 |

C contains 20,175 rows including purchases/preapprovals. Its application population A is **14,076**; decision population D is **11,869**. These are feasibility/profile counts, not a lender benchmark or completed analytical mart. See [the KPI plan](initial_schema_and_kpi_plan.md) for exact filters and denominators.

## Practices reused from Project #1

Read its README, reproduction guide and validation evidence. Reuse preserved official sources, explicit grain and mappings, Parquet outputs, separate read-only validation, visible warnings, reproducible builds and truthful limits on automation. Do not copy institution-level risk ratios, peer rules or time-series assumptions into application outcomes. No Project #1 files or Git settings were modified.

## Risks and open checks

- Local file passes basic structure/population checks, but completeness still needs independent reconciliation to the official DE summary by action. Automated source access returned 403 and the browser connection became unavailable; user-assisted download resolved file acquisition only.
- Export header differs from the bulk schema, notably `loan_to_value_ratio`; confirm its combined-LTV semantics before using that metric. Header normalization must be explicit.
- Lender names/reference join are pending. The current 558 count refers to LEIs, not independently reconciled corporate groups.
- Missing/exempt reporting, privacy modifications and lender/product composition limit comparability. Default/performance, causal fairness and Luxembourg-market claims remain outside scope.
- Python is available, but Polars is absent from the current default interpreter. Create a separate project environment; do not modify Project #1's environment.

## First implementation task

Update: the initial lossless staging milestone is now implemented and independently validated. See [reproduction and executed checks](reproduction.md). The remaining source/semantic gates below still apply; analytical marts and Power BI have not started.

Build the lossless staging contract: an isolated Python/Polars environment, a source manifest, explicit observed-header map and per-field value-status parsing. In parallel with that independent work, reconcile the official source totals and resolve the LTV alias. Write Parquet with source row IDs and a fully reconciled exclusion waterfall. Start KPI aggregation only after those controls pass; begin Power BI after independent KPI validation.

The initial profiler uses only Python's standard library and reads raw data without modifying it. Reproduce from the project root with `python src/validation/profile_raw.py`; its detailed output is [raw_profile.json](evidence/raw_profile.json). Independent source reconciliation and transformation validation are still pending; no completed automation or external certification is claimed.
