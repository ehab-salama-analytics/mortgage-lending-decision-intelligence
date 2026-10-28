"""Reconcile source counts/amounts and lender names independently."""
import csv
import io
import json
import zipfile
from collections import Counter, defaultdict
from decimal import Decimal
from pathlib import Path
import polars as pl

ROOT = Path(__file__).resolve().parents[2]
c = json.loads((ROOT / 'config/source_contract.json').read_text())
expected = json.loads((ROOT / 'config/official_action_totals.json').read_text())['actions']
counts, amounts, lenders = Counter(), defaultdict(Decimal), Counter()
with (ROOT / c['source_file']).open(encoding='utf-8-sig',newline='') as stream:
    for r in csv.DictReader(stream):
        counts[r['action_taken']] += 1
        amounts[r['action_taken']] += Decimal(r['loan_amount'])
        lenders[r['lei']] += 1
errors=[]
for action, e in expected.items():
    if counts[action] != e['count'] or amounts[action] != e['amount']:
        errors.append('Official action reconciliation: '+action)
with zipfile.ZipFile(ROOT / 'data/raw/hmda_2025/reference/2025_public_ts_csv.zip') as z:
    with z.open('2025_public_ts_csv.csv') as stream:
        ts=list(csv.DictReader(io.TextIOWrapper(stream,encoding='utf-8-sig')))
lookup={(r['activity_year'],r['lei']):r for r in ts}
if len(lookup)!=len(ts): errors.append('Duplicate TS key')
dim=pl.read_parquet(ROOT / 'data/staging/dim_lender.parquet')
if dim.height != len(lenders) or set(dim['lei']) != set(lenders): errors.append('Dimension coverage')
for r in dim.iter_rows(named=True):
    ref=lookup.get((r['activity_year'],r['lei']))
    if not ref or r['respondent_name']!=ref['respondent_name'] or r['agency_code']!=ref['agency_code']:
        errors.append('Lender attributes: '+r['lei'])
filers=json.loads((ROOT / 'data/raw/hmda_2025/reference/official_filers.json').read_text())['institutions']
missing=sorted(set(lenders)-{r['lei'] for r in filers})
report={'result':'FAIL' if errors else 'PASS','errors':errors,
        'official_action_counts_and_amounts_matched':not errors,
        'source_rows':sum(counts.values()),'matched_lenders':dim.height,
        'filer_lookup_missing_leis':missing,'rows_for_missing_leis':sum(lenders[k] for k in missing),
        'reference_used':'Snapshot TS; filer API is diagnostic only'}
(ROOT / 'docs/evidence/source_reference_validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
if errors: raise SystemExit(1)
