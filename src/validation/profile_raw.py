"""Read-only Phase 0 inspection; no cleaning or analytical outputs."""
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'data/raw/hmda_2025/actions_taken_1-2-3-4-5-6-7-8_state_DE.csv'

def main():
    counts = {}
    seen = Counter()
    cohort_actions = Counter()
    malformed = 0
    rows = 0
    with SOURCE.open(encoding='utf-8-sig', newline='') as stream:
        reader = csv.DictReader(stream)
        fields = reader.fieldnames
        counts = {f: Counter() for f in fields}
        for row in reader:
            rows += 1
            if None in row or any(v is None for v in row.values()):
                malformed += 1
                continue
            for f, v in row.items():
                counts[f][v] += 1
            seen[tuple(row[f] for f in fields)] += 1
            eligible = all(row[f] == v for f, v in {
                'loan_purpose': '1', 'lien_status': '1', 'occupancy_type': '1',
                'construction_method': '1', 'reverse_mortgage': '2',
                'open-end_line_of_credit': '2', 'business_or_commercial_purpose': '2'
            }.items()) and row['total_units'] in {'1', '2', '3', '4'}
            if eligible:
                cohort_actions[row['action_taken']] += 1
    selected = ['activity_year', 'state_code', 'county_code', 'action_taken',
                'loan_purpose', 'preapproval', 'debt_to_income_ratio',
                'reverse_mortgage', 'open-end_line_of_credit', 'business_or_commercial_purpose']
    tokens = ['', 'NA', 'Exempt', '1111', '8888', '9999']
    report = {
        'source_file': str(SOURCE.relative_to(ROOT)),
        'bytes': SOURCE.stat().st_size,
        'sha256': hashlib.file_digest(SOURCE.open('rb'), 'sha256').hexdigest(),
        'row_count': rows, 'column_count': len(fields), 'fields': fields,
        'malformed_rows': malformed,
        'distinct_leis': len(counts['lei']),
        'identical_public_row_excess': sum(n - 1 for n in seen.values()),
        'frequencies': {f: dict(counts[f]) for f in selected},
        'special_tokens_by_field': {f: {t: counts[f][t] for t in tokens if counts[f][t]} for f in fields},
        'proposed_property_product_cohort_actions': dict(cohort_actions),
        'note': 'Identical public rows are not proven duplicates. Preserve all records. Token meaning is field-specific.'
    }
    target = ROOT / 'docs/evidence/raw_profile.json'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps({k: v for k, v in report.items() if k not in ['fields', 'special_tokens_by_field', 'frequencies']}, indent=2))
    print(json.dumps({f: report['frequencies'][f] for f in ['activity_year', 'state_code', 'county_code', 'action_taken']}, indent=2))

if __name__ == '__main__':
    main()
