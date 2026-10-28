"""Preserve all public values and append typed values and population flags."""
import hashlib
import json
from pathlib import Path
import polars as pl

ROOT = Path(__file__).resolve().parents[2]

def main():
    c = json.loads((ROOT / 'config/source_contract.json').read_text())
    source = ROOT / c['source_file']
    with source.open('rb') as stream:
        digest = hashlib.file_digest(stream, 'sha256').hexdigest()
    if digest != c['sha256']:
        raise ValueError('Source hash changed; investigate and version the contract.')
    df = pl.read_csv(source, infer_schema=False, empty_string_is_null=False)
    if df.columns != list(c['field_map']) or df.height != c['expected_rows']:
        raise ValueError('Source schema or row count differs from the reviewed contract.')
    if len(set(c['field_map'].values())) != len(c['field_map']):
        raise ValueError('Field normalization collision')
    df = df.rename(c['field_map']).with_row_index('source_row_number', offset=1)
    df = df.with_columns(pl.lit(digest).alias('source_sha256'))
    for field in c['numeric_fields']:
        raw = pl.col(field)
        value = raw.cast(pl.Float64, strict=False)
        valid = value.is_not_null() & value.is_finite()
        status = (pl.when(raw == '').then(pl.lit('blank'))
                  .when(raw == 'NA').then(pl.lit('not_applicable'))
                  .when(raw == 'Exempt').then(pl.lit('exempt'))
                  .when(valid).then(pl.lit('numeric'))
                  .otherwise(pl.lit('invalid')))
        df = df.with_columns(value.alias(field + '_parsed'), status.alias(field + '_status'))
        df = df.with_columns(pl.when(pl.col(field + '_status') == 'numeric')
                             .then(pl.col(field + '_parsed')).otherwise(None).alias(field + '_parsed'))
    # Raw DTI, age, categorical sentinels and unconfirmed LTV alias remain strings.
    reason = pl.lit('included')
    for field, allowed in reversed(list(c['cohort_rules'].items())):
        reason = pl.when(~pl.col(field).is_in(allowed)).then(pl.lit(field)).otherwise(reason)
    df = df.with_columns(reason.alias('first_exclusion_reason'))
    df = df.with_columns((pl.col('first_exclusion_reason') == 'included').alias('in_property_product_cohort'))
    for name, actions in [('application', ['1','2','3','4','5']), ('decision', ['1','2','3']), ('origination', ['1'])]:
        df = df.with_columns((pl.col('in_property_product_cohort') & pl.col('action_taken').is_in(actions)).alias('in_' + name + '_population'))
    target = ROOT / 'data/staging'
    target.mkdir(parents=True, exist_ok=True)
    df.write_parquet(target / 'hmda_2025_de.parquet', compression='zstd')
    df.group_by('first_exclusion_reason').len().sort('first_exclusion_reason').write_parquet(target / 'cohort_exclusions.parquet')
    manifest = {'source_file': c['source_file'], 'sha256': digest, 'bytes': source.stat().st_size,
                'rows': df.height, 'source_columns': len(c['field_map']), 'staged_columns': df.width,
                'polars_version': pl.__version__, 'acquisition_method': 'User-assisted official Data Browser download',
                'receipt_date': '2026-10-27', 'exact_receipt_time_utc': None,
                'official_total_reconciliation': 'checked separately by validate_source_reference.py', 'ltv_alias_semantics': 'pending; excluded from numeric parsing'}
    (target / 'source_manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    print(f'Built {df.height:,} rows; raw values preserved; no KPI marts produced.')

if __name__ == '__main__':
    main()
