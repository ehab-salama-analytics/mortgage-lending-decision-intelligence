"""Independently compare saved Parquet with csv/Decimal parsing of source."""
import csv
import hashlib
import json
from collections import Counter
from decimal import Decimal, InvalidOperation
from pathlib import Path
import polars as pl

ROOT = Path(__file__).resolve().parents[2]

def main():
    c = json.loads((ROOT / 'config/source_contract.json').read_text())
    source = ROOT / c['source_file']
    with source.open('rb') as stream:
        digest = hashlib.file_digest(stream, 'sha256').hexdigest()
    with source.open(encoding='utf-8-sig', newline='') as stream:
        reader = csv.DictReader(stream)
        header = reader.fieldnames
        raw = list(reader)
    df = pl.read_parquet(ROOT / 'data/staging/hmda_2025_de.parquet')
    errors = Counter()
    exclusions = Counter()
    statuses = {f: Counter() for f in c['numeric_fields']}
    def check(ok, label):
        if not ok:
            errors[label] += 1
    check(digest == c['sha256'], 'source_hash')
    check(header == list(c['field_map']), 'header')
    check(len(raw) == df.height == c['expected_rows'], 'row_count')
    check(df['source_row_number'].n_unique() == df.height, 'unique_source_row')
    for i, (r, s) in enumerate(zip(raw, df.iter_rows(named=True)), 1):
        check(None not in r and None not in r.values(), 'malformed_source')
        check(all(r[f] == s[dest] for f, dest in c['field_map'].items()), 'lossless_values')
        check(s['source_row_number'] == i and s['source_sha256'] == digest, 'lineage')
        check(r['activity_year'] == '2025' and r['state_code'] == 'DE', 'year_state')
        check(r['action_taken'] in set('12345678'), 'action_domain')
        # Deliberately reconstruct the agreed cohort independently of builder expressions.
        rules = [('loan_purpose', {'1'}), ('lien_status', {'1'}), ('occupancy_type', {'1'}),
                 ('construction_method', {'1'}), ('total_units', {'1','2','3','4'}),
                 ('reverse_mortgage', {'2'}), ('open-end_line_of_credit', {'2'}),
                 ('business_or_commercial_purpose', {'2'})]
        reason = next((f.replace('-', '_') for f, allowed in rules if r[f] not in allowed), 'included')
        exclusions[reason] += 1
        included = reason == 'included'
        check(s['first_exclusion_reason'] == reason and s['in_property_product_cohort'] == included, 'cohort')
        for name, actions in [('application','12345'), ('decision','123'), ('origination','1')]:
            check(s['in_' + name + '_population'] == (included and r['action_taken'] in actions), 'population_' + name)
        for f in c['numeric_fields']:
            token = r[f]
            value = None
            if token in {'', 'NA', 'Exempt'}:
                status = {'':'blank', 'NA':'not_applicable', 'Exempt':'exempt'}[token]
            else:
                try:
                    d = Decimal(token)
                    status = 'numeric' if d.is_finite() else 'invalid'
                    if status == 'numeric':
                        value = float(d)
                except InvalidOperation:
                    status = 'invalid'
            statuses[f][status] += 1
            check(s[f + '_status'] == status and s[f + '_parsed'] == value, 'numeric_' + f)
    saved = pl.read_parquet(ROOT / 'data/staging/cohort_exclusions.parquet')
    check(dict(saved.iter_rows()) == dict(exclusions), 'exclusion_reconciliation')
    check(sum(exclusions.values()) == len(raw), 'exclusion_total')
    report = {'result':'FAIL' if errors else 'PASS', 'rows_compared':len(raw),
              'failures':dict(errors), 'exclusions':dict(exclusions),
              'numeric_status_counts':{f:dict(v) for f,v in statuses.items()},
              'warnings':['Official summary reconciliation is checked separately by validate_source_reference.py', 'LTV alias semantics pending',
                          'Public identical rows retained; not deduplicated',
                          'DTI/age/categorical values preserved raw; detailed typing is a later stage']}
    out = ROOT / 'docs/evidence/staging_validation.json'
    out.write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))
    if errors:
        raise SystemExit(1)

if __name__ == '__main__':
    main()
