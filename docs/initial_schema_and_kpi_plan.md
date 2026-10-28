# Initial schema and KPI plan

Based on the actual 99-column downloaded header, the [official public schema](https://ffiec.cfpb.gov/documentation/publications/loan-level-datasets/public-lar-schema), [field dictionary](https://ffiec.cfpb.gov/documentation/publications/loan-level-datasets/lar-data-fields) and [modified LAR specifications](https://ffiec.cfpb.gov/documentation/publications/modified-lar/modified-lar-schema). The complete observed header and token counts are in [raw_profile.json](evidence/raw_profile.json).

## Fields and mapping

| Use | Actual CSV fields |
|---|---|
| Grain and geography | `activity_year`, `lei`, `state_code`, `county_code`, `census_tract`, `derived_msa-md` |
| Outcomes | `action_taken`, `preapproval`, `denial_reason-1` through `denial_reason-4` |
| Cohort and product | `loan_purpose`, `loan_type`, `lien_status`, `occupancy_type`, `construction_method`, `total_units`, `reverse_mortgage`, `open-end_line_of_credit`, `business_or_commercial_purpose` |
| Underwriting characteristics | `loan_amount`, `income`, `property_value`, `loan_to_value_ratio`, `debt_to_income_ratio`, `loan_term`, `conforming_loan_limit` |
| Pricing | `interest_rate`, `rate_spread`, `total_loan_costs`, `total_points_and_fees`, `origination_charges`, `discount_points`, `lender_credits`, `hoepa_status` |
| Descriptive demographic coverage | `derived_race`, `derived_ethnicity`, `derived_sex`, `applicant_age`, observed/reported indicators and underlying applicant/co-applicant categories |
| Additional context | `submission_of_application`, `initially_payable_to_institution`, `aus-1` through `aus-5`, tract characteristics |

Map hyphens explicitly to underscores and check for collisions. The CSV's `loan_to_value_ratio` differs from the published schema's `combined_loan_to_value_ratio`: preserve it under its source name until the official export alias is confirmed. Do not infer combined leverage from loan amount/property value. Credit-score **type** is present; actual credit scores are not.

Use strings on initial read so sentinels and leading-zero geography codes survive. Add source hash and source row number as a technical key; neither is a universal loan/applicant identifier. Store raw value, parsed value and value-status separately where needed. Income is in thousands of dollars; loan amounts/property values/costs are dollars; loan term is months; rates and ratios use their documented percent units.

## Missingness and privacy

Blank, `NA`, `Exempt` and numeric codes have field-specific meanings. `1111` is an exemption in relevant categorical fields; age uses special codes such as `8888`/`9999`. Do not apply a universal missing-code rule or replace missing values with zero. Empty secondary race/reason slots can be structural. Preserve unknown, not applicable, exempt and invalid as distinct statuses.

DTI combines exact values and bands (`<20%`, `20%-<30%`, `30%-<36%`, `50%-60%`, `>60%`); preserve ordered categories rather than taking a numeric mean. Age is grouped. Loan amount and property value are privacy-modified interval midpoints; their sums are approximate disclosed amounts. Total units and affordable-unit fields also have disclosure modifications. Public records exclude direct identifiers, actual credit scores and application/action dates; timing, turnaround and borrower-level linkage are unavailable. Identical public records must not be automatically deduplicated.

## Populations

Let C be records with `loan_purpose=1`, `lien_status=1`, `occupancy_type=1`, `construction_method=1`, `total_units` in 1–4, `reverse_mortgage=2`, `open-end_line_of_credit=2`, `business_or_commercial_purpose=2`, within DE/2025. Exempt/unknown values on required cohort flags are excluded from C, retained in raw/staging and counted in an exclusion waterfall. No complete-case exclusion on income, DTI, pricing or demographics.

Within C, let N1…N8 be counts by action. A = N1+N2+N3+N4+N5 (applications with these reported annual outcomes). D = N1+N2+N3 (decision population). O = N1 (originations). Purchased loans (6) and standalone preapproval outcomes (7–8) remain separate. Preapproval-originated loans already coded 1 remain in O; codes 7–8 alone cannot measure the full preapproval funnel.

## Proposed KPIs

| Metric | Numerator / denominator or population |
|---|---|
| Application volume | A; count, no denominator |
| Denial rate among decisions | N3 / D |
| Approval outcome rate | (N1+N2) / D; includes approved but not accepted |
| Origination share of applications | N1 / A; not a longitudinal conversion probability |
| Withdrawal / incomplete shares | N4 / A; N5 / A |
| Approved-not-accepted share among approvals | N2 / (N1+N2) |
| Origination volume and disclosed amount | O and sum of valid loan amounts in O; show amount coverage |
| Lender origination share | Lender O / statewide O in the same cohort and product filters |
| Denial reasons | Distinct denied records with reason r in any slot / N3; separately report reason coverage; multiple reasons may sum above 100% |
| Pricing medians | Valid, non-exempt values among O, individually per metric; show valid n / O and applicability statuses |
| DTI distribution | Each valid DTI band / O with usable DTI; show usable n / O alongside it |
| Field quality | Each status count / specified eligible population; distinguish exemption from unexpected missingness |

All zero denominators return unavailable. Persist numerator and denominator, not just a percentage. Product splits are required for lender comparisons; unadjusted differences can reflect applicant/product mix. Proposed display rule: suppress rates where denominator <30 and avoid lender league tables; this is a project reporting rule, not a statistical or legal guarantee. Demographic comparisons use the same D definition, retain unknown categories, show group n and remain descriptive.

## First validation controls

Fail on malformed rows, unexpected schema, wrong year/state, illegal action codes, technical-key collisions or row-multiplying joins. Reconcile all action counts and the source total independently; test C inclusion/exclusion totals and A/D identities. Report identical public rows without deletion. Profile tokens by field/outcome/lender, numeric parsing failures, outliers, missing county and unavailable demographic fields. Do not cap outliers silently. Independently recompute aggregates from saved staging, validate pricing applicability, then test Power BI filter denominators against those aggregates.
