"""Independent raw-CSV reconstruction of rate and coverage tables."""
import csv
import json
from collections import Counter,defaultdict
from decimal import Decimal,InvalidOperation
from pathlib import Path
import polars as pl

ROOT=Path(__file__).resolve().parents[2]
c=json.loads((ROOT/'config/source_contract.json').read_text())
counts=defaultdict(Counter)
cover=defaultdict(Counter)
originations=0
fields=['income','property_value','interest_rate','rate_spread','total_loan_costs','discount_points','lender_credits']
with (ROOT/c['source_file']).open(encoding='utf-8-sig',newline='') as stream:
    for r in csv.DictReader(stream):
        if not (r['loan_purpose']=='1' and r['lien_status']=='1' and r['occupancy_type']=='1'
                and r['construction_method']=='1' and r['total_units'] in {'1','2','3','4'}
                and r['reverse_mortgage']=='2' and r['open-end_line_of_credit']=='2'
                and r['business_or_commercial_purpose']=='2'): continue
        for key in [('state','ALL','ALL'),('state_product','ALL',r['loan_type']),
                    ('lender_product',r['lei'],r['loan_type'])]: counts[key][int(r['action_taken'])]+=1
        if r['action_taken']=='1':
            originations+=1
            for f in fields:
                v=r[f]
                status={'':'blank','NA':'not_applicable','Exempt':'exempt'}.get(v)
                if status is None:
                    try: status='numeric' if Decimal(v).is_finite() else 'invalid'
                    except InvalidOperation: status='invalid'
                cover[f][status]+=1
expected={}
for key,n in counts.items():
    apps=sum(n[i] for i in range(1,6)); dec=sum(n[i] for i in [1,2,3]); app=n[1]+n[2]
    vals={'denial_rate':(n[3],dec),'approval_rate':(app,dec),'origination_share':(n[1],apps),
          'withdrawal_share':(n[4],apps),'incomplete_share':(n[5],apps),
          'approved_not_accepted_share':(n[2],app)}
    for m,pair in vals.items(): expected[key+(m,)]=pair
errors=[]
df=pl.read_parquet(ROOT/'data/analytical/outcome_rates.parquet')
seen=set(); statuses=Counter()
for r in df.iter_rows(named=True):
    key=(r['scope'],r['lei'],r['loan_type'],r['metric'])
    if key in seen: errors.append('duplicate key')
    seen.add(key)
    pair=expected.get(key)
    if pair is None or pair!=(r['numerator'],r['denominator']): errors.append('numerator/denominator')
    if pair is None: continue
    num,den=pair
    status='no_population' if den==0 else 'small_population' if den<30 else 'reported'
    rate=num/den if den>=30 else None
    if r['display_status']!=status or r['display_rate']!=rate: errors.append('display policy')
    if r['activity_year']!='2025' or r['state_code']!='DE': errors.append('geography/year')
    statuses[status]+=1
if seen!=set(expected): errors.append('key coverage')
cov=pl.read_parquet(ROOT/'data/analytical/origination_field_coverage.parquet')
expected_cov={(f,s) for f in fields for s in ['numeric','blank','not_applicable','exempt','invalid']}
if cov.height!=len(expected_cov) or set(zip(cov['field'],cov['value_status']))!=expected_cov: errors.append('coverage keys')
for r in cov.iter_rows(named=True):
    n=cover[r['field']][r['value_status']]
    if (r['numerator'],r['denominator'],r['share'])!=(n,originations,n/originations if originations else None): errors.append('field coverage')
pop=pl.read_parquet(ROOT/'data/analytical/outcome_populations.parquet')
if pop.height!=len(counts): errors.append('population rows')
for r in pop.iter_rows(named=True):
    n=counts[(r['scope'],r['lei'],r['loan_type'])]
    if any(r[f'n{i}']!=n[i] for i in range(1,9)): errors.append('action counts')
    if (r['applications'],r['decisions'],r['approvals'])!=(sum(n[i] for i in range(1,6)),sum(n[i] for i in [1,2,3]),n[1]+n[2]): errors.append('population totals')
report={'result':'FAIL' if errors else 'PASS','rate_rows':df.height,'coverage_rows':cov.height,
        'display_status_counts':dict(statuses),'failures':dict(Counter(errors)),
        'method':'Independent CSV reconstruction; every saved rate numerator, denominator, display status and coverage row checked'}
(ROOT/'docs/evidence/outcome_rates_validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
if errors: raise SystemExit(1)
