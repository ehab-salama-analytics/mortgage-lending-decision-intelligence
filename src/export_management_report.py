"""Generate deterministic management brief and Power BI-ready CSV exports."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import polars as pl

ROOT=Path(__file__).resolve().parents[1]

def main():
    # Fresh checks prevent stale PASS files from authorizing changed input tables.
    for name in ['validate_source_reference','validate_outcome_counts','validate_outcome_rates']:
        subprocess.run([sys.executable,'-X','utf8',str(ROOT/'src/validation'/f'{name}.py')],check=True)
    rates=pl.read_parquet(ROOT/'data/analytical/outcome_rates.parquet')
    coverage=pl.read_parquet(ROOT/'data/analytical/origination_field_coverage.parquet')
    out=ROOT/'reports/generated'
    out.mkdir(parents=True,exist_ok=True)
    tables={'outcome_rates':rates,'origination_field_coverage':coverage,
            'outcome_populations':pl.read_parquet(ROOT/'data/analytical/outcome_populations.parquet'),
            'dim_lender':pl.read_parquet(ROOT/'data/staging/dim_lender.parquet')}
    for name,df in tables.items(): df.write_csv(out/f'{name}.csv')
    population=tables['outcome_populations'].filter(pl.col('scope')=='state').row(0,named=True)
    labels={'denial_rate':'Denial rate among decisions','approval_rate':'Approval outcome rate',
            'origination_share':'Origination share of applications','withdrawal_share':'Withdrawal share',
            'incomplete_share':'Incomplete-file share','approved_not_accepted_share':'Approved-not-accepted share among approvals'}
    lines=['# Delaware mortgage lending — management brief','',
           '2025 HMDA Snapshot | QuantRisk Analytics | Local portfolio analysis','',
           'Population: home purchase, first lien, principal residence, site-built, 1–4 units; explicitly closed-end, non-reverse and non-business. All loan types are included.','',
           '## Observed outcomes','',
           '| Measure | Numerator | Denominator | Rate |','|---|---:|---:|---:|']
    for r in rates.filter(pl.col('scope')=='state').sort('metric').iter_rows(named=True):
        rate=f"{r['display_rate']:.2%}" if r['display_rate'] is not None else r['display_status']
        lines.append(f"| {labels[r['metric']]} | {r['numerator']:,} | {r['denominator']:,} | {rate} |")
    lines+=['',f"Application population: {population['applications']:,} records; decision population: {population['decisions']:,}. Originations: {population['n1']:,}. Purchased loans and standalone preapproval outcomes are excluded from these denominators. These are annual observed outcomes, not a tracked conversion funnel.",'',
            '## Numeric-field coverage among originations','',
            'Coverage means a finite numeric value is available. It does not establish correct reporting, applicability or a valid economic range.','',
            '| Field | Numeric records | Originations | Coverage |','|---|---:|---:|---:|']
    for r in coverage.filter(pl.col('value_status')=='numeric').sort('field').iter_rows(named=True):
        lines.append(f"| {r['field']} | {r['numerator']:,} | {r['denominator']:,} | {r['share']:.2%} |")
    lines+=['','## Reading the exports','',
            'Select exactly one scope: state, state_product or lender_product. These scopes overlap and must never be summed together. Rates below denominator 30 are withheld under a project display rule; zero denominators are unavailable. This is not a disclosure-control or statistical-significance guarantee.','',
            'Join lender names by activity_year and lei only for lender_product rows. ALL identifies aggregate rows. Keep identifiers as text. County-level counts remain in the separate outcome_counts Parquet table.','',
            'Do not average rates or sum stored denominators across different metrics. Recalculate rates from the matching numerator and denominator within a single metric/scope. In Power BI use the additive population table to build measures and reapply the display threshold after filtering.','',
            '## Management interpretation and limits','',
            'Use these outputs to describe activity and identify areas for further investigation. Product and applicant mix can explain differences between lenders. No ranking, causal demographic assessment, default model or individual lending recommendation is provided. Pricing analysis requires additional applicability controls; LTV remains excluded pending alias confirmation.','',
            'Official counts and disclosed amounts reconcile for all eight outcomes. Snapshot lender names cover all 558 LEIs. The separate filer lookup omitted nine LEIs covering 44 records; no source records were dropped.','',
            'Source: https://ffiec.cfpb.gov/data-browser/data/2025 — Snapshot freeze date shown by publisher: June 2, 2026. This is US evidence, not evidence of Luxembourg market conditions.','']
    (out/'management_brief.md').write_text('\n'.join(lines),encoding='utf-8')
    contract=json.loads((ROOT/'config/source_contract.json').read_text())
    manifest={'source_sha256':contract['sha256'],'data_year':2025,'state':'DE',
              'report_status':'Validated descriptive outcome and coverage export; Power BI not implemented',
              'files':{}}
    for p in sorted(out.iterdir()):
        if p.name=='export_manifest.json' or not p.is_file(): continue
        with p.open('rb') as stream: digest=hashlib.file_digest(stream,'sha256').hexdigest()
        manifest['files'][p.name]={'bytes':p.stat().st_size,'sha256':digest}
    (out/'export_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('Management brief and four CSV exports generated.')

if __name__=='__main__': main()
