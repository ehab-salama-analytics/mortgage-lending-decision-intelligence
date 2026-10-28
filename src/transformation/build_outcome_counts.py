"""Additive counts for the verified property/product cohort; no rankings."""
from pathlib import Path
import polars as pl

ROOT=Path(__file__).resolve().parents[2]
df=pl.read_parquet(ROOT/'data/staging/hmda_2025_de.parquet')
keys=['activity_year','state_code','county_code','lei','loan_type','action_taken']
out=df.filter(pl.col('in_property_product_cohort')).group_by(keys).len(name='record_count').sort(keys)
target=ROOT/'data/analytical'
target.mkdir(parents=True,exist_ok=True)
out.write_parquet(target/'outcome_counts.parquet',compression='zstd')
print(f'Outcome count table: {out.height} rows; {out["record_count"].sum()} source records')
