"""Outcome rates with explicit populations and small-denominator display rules."""
from pathlib import Path
import polars as pl

ROOT=Path(__file__).resolve().parents[2]
source=pl.read_parquet(ROOT/'data/analytical/outcome_counts.parquet')
parts=[]
for scope, group in [('state',['activity_year','state_code']),
                     ('state_product',['activity_year','state_code','loan_type']),
                     ('lender_product',['activity_year','state_code','lei','loan_type'])]:
    d=source.group_by(group).agg([
        pl.col('record_count').filter(pl.col('action_taken')==str(i)).sum().alias(f'n{i}')
        for i in range(1,9)])
    d=d.with_columns(pl.lit(scope).alias('scope'))
    for key in ['lei','loan_type']:
        if key not in group: d=d.with_columns(pl.lit('ALL').alias(key))
    parts.append(d)
base=pl.concat(parts,how='diagonal').with_columns(
    pl.sum_horizontal('n1','n2','n3','n4','n5').alias('applications'),
    pl.sum_horizontal('n1','n2','n3').alias('decisions'),
    pl.sum_horizontal('n1','n2').alias('approvals'))
spec=[('denial_rate',pl.col('n3'),pl.col('decisions')),
      ('approval_rate',pl.col('approvals'),pl.col('decisions')),
      ('origination_share',pl.col('n1'),pl.col('applications')),
      ('withdrawal_share',pl.col('n4'),pl.col('applications')),
      ('incomplete_share',pl.col('n5'),pl.col('applications')),
      ('approved_not_accepted_share',pl.col('n2'),pl.col('approvals'))]
rates=[]
for name,num,den in spec:
    rates.append(base.select('scope','activity_year','state_code','lei','loan_type',
        pl.lit(name).alias('metric'),num.alias('numerator'),den.alias('denominator')))
out=pl.concat(rates).with_columns(
    pl.when(pl.col('denominator')==0).then(pl.lit('no_population'))
    .when(pl.col('denominator')<30).then(pl.lit('small_population'))
    .otherwise(pl.lit('reported')).alias('display_status'),
    pl.when(pl.col('denominator')>=30).then(pl.col('numerator')/pl.col('denominator'))
    .otherwise(None).alias('display_rate')).sort(['scope','lei','loan_type','metric'])
base.sort(['scope','lei','loan_type']).write_parquet(ROOT/'data/analytical/outcome_populations.parquet')
out.write_parquet(ROOT/'data/analytical/outcome_rates.parquet')
# Coverage is usable numeric data among originations, not a claim of reporting compliance.
staging=pl.read_parquet(ROOT/'data/staging/hmda_2025_de.parquet').filter(pl.col('in_origination_population'))
coverage=[]
for field in ['income','property_value','interest_rate','rate_spread','total_loan_costs','discount_points','lender_credits']:
    for status in ['numeric','blank','not_applicable','exempt','invalid']:
        n=staging.filter(pl.col(field+'_status')==status).height
        coverage.append({'field':field,'value_status':status,'numerator':n,
                         'denominator':staging.height,'share':n/staging.height if staging.height else None})
pl.DataFrame(coverage).write_parquet(ROOT/'data/analytical/origination_field_coverage.parquet')
print(f'Built {out.height} rate rows and {len(coverage)} coverage rows')
