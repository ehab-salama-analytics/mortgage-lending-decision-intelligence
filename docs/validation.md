# Validation evidence

Publication rebuild: 28 October 2026. The pipeline stops on a failed stage. Validation is internal and reproducible, not external certification.

| Control | Evidence |
|---|---|
| All 55,183 raw rows, 99 source fields, lineage, numeric parses and population flags | [Staging validation](evidence/staging_validation.json) |
| Eight action counts and disclosed amounts; 558 LEIs covered by snapshot TS | [Reference validation](evidence/source_reference_validation.json) |
| Every outcome-count cell reconstructed from raw CSV | [Count validation](evidence/outcome_counts_validation.json) |
| Rates, denominators, small populations and field coverage independently reconstructed | [Rate validation](evidence/outcome_rates_validation.json) |
| Management exports and CSV round trips | [Export validation](evidence/export_validation.json) |
| Unique lender-product model grain and matching dimensions | [Power BI preparation](evidence/power_bi_preparation.json) |
| Desktop totals and visual filters | [Desktop validation](evidence/power_bi_desktop_validation.json) |

The preparation evidence describes Python checks only; its historical pending-Desktop note is superseded by the separate Desktop validation record. Source warnings remain visible: 429 missing county codes, 104 identical public-row excess retained, and unresolved LTV alias semantics. No invalid numeric tokens were found in the 11 parsed staging fields; this does not establish business validity.

The official filer lookup omits nine LEIs covering 44 source records. The snapshot Transmittal Sheet supplies all 558 names and is the reference used. Broad categorical-domain and applicability checks, adjusted comparisons and LTV-dependent metrics remain outside the delivered MVP.
