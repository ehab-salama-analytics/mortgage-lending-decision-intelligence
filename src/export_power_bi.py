"""Prepare a single-grain star schema and independent reconciliation evidence."""
from pathlib import Path
import json
import polars as pl

ROOT=Path(__file__).resolve().parents[1]
out=ROOT/'reports/generated/power_bi'
out.mkdir(parents=True,exist_ok=True)
fact=pl.read_parquet(ROOT/'data/analytical/outcome_populations.parquet').filter(
    pl.col('scope')=='lender_product').drop('scope')
fact=fact.with_columns((pl.col('activity_year')+'|'+pl.col('lei')).alias('lender_key'))
dim=pl.read_parquet(ROOT/'data/staging/dim_lender.parquet').with_columns(
    (pl.col('activity_year')+'|'+pl.col('lei')).alias('lender_key'))
product=pl.DataFrame({'loan_type':['1','2','3','4'],
    'product_name':['Conventional','FHA','VA','USDA RHS/FSA']})
assert fact.height==fact.select('activity_year','state_code','lei','loan_type').unique().height
assert dim.height==dim['lender_key'].n_unique()
joined=fact.join(dim,on='lender_key',how='left',validate='m:1')
assert joined.height==fact.height and joined['respondent_name'].null_count()==0
assert set(fact['loan_type'])<=set(product['loan_type'])
state=pl.read_parquet(ROOT/'data/analytical/outcome_populations.parquet').filter(pl.col('scope')=='state').row(0,named=True)
totals={f:int(fact[f].sum()) for f in [*[f'n{i}' for i in range(1,9)],'applications','decisions','approvals']}
assert all(v==state[f] for f,v in totals.items())
for name,df in [('FactOutcomes',fact),('DimLender',dim),('DimProduct',product),
                ('StatewideCoverage',pl.read_parquet(ROOT/'data/analytical/origination_field_coverage.parquet'))]:
    df.write_csv(out/f'{name}.csv')
report={'result':'PASS','fact_rows':fact.height,'lender_dimension_rows':dim.height,
        'join_multiplied_rows':0,'unmatched_lenders':0,'statewide_totals':totals,
        'note':'Python data-model preparation checks only; DAX execution and Desktop interaction tests pending.'}
(ROOT/'docs/evidence/power_bi_preparation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
