"""Reconstruct every count cell directly from raw CSV, without staging flags."""
import csv
import json
from collections import Counter
from pathlib import Path
import polars as pl

ROOT=Path(__file__).resolve().parents[2]
c=json.loads((ROOT/'config/source_contract.json').read_text())
counts=Counter()
keys=['activity_year','state_code','county_code','lei','loan_type','action_taken']
with (ROOT/c['source_file']).open(encoding='utf-8-sig',newline='') as stream:
    for r in csv.DictReader(stream):
        if (r['loan_purpose']=='1' and r['lien_status']=='1' and r['occupancy_type']=='1'
            and r['construction_method']=='1' and r['total_units'] in {'1','2','3','4'}
            and r['reverse_mortgage']=='2' and r['open-end_line_of_credit']=='2'
            and r['business_or_commercial_purpose']=='2'):
            counts[tuple(r[k] for k in keys)]+=1
df=pl.read_parquet(ROOT/'data/analytical/outcome_counts.parquet')
actual={tuple(r[k] for k in keys):r['record_count'] for r in df.iter_rows(named=True)}
passed=actual==dict(counts) and len(actual)==df.height
report={'result':'PASS' if passed else 'FAIL','cells_compared':len(counts),
        'cohort_records':sum(counts.values()),'validation':'Every cell reconstructed independently from raw CSV'}
(ROOT/'docs/evidence/outcome_counts_validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
if not passed: raise SystemExit(1)
