"""Build a state lender dimension from the matching annual snapshot TS."""
import csv
import hashlib
import io
import json
import zipfile
from pathlib import Path
import polars as pl

ROOT = Path(__file__).resolve().parents[2]
archive = ROOT / 'data/raw/hmda_2025/reference/2025_public_ts_csv.zip'
contract = json.loads((ROOT / 'config/lender_reference_contract.json').read_text())
with archive.open('rb') as stream:
    if hashlib.file_digest(stream, 'sha256').hexdigest() != contract['sha256']:
        raise ValueError('Snapshot TS hash changed; review source version')
with zipfile.ZipFile(archive) as z:
    with z.open('2025_public_ts_csv.csv') as stream:
        rows = list(csv.DictReader(io.TextIOWrapper(stream, encoding='utf-8-sig')))
ts = pl.DataFrame(rows)
if len(rows) != contract['national_ts_rows']:
    raise ValueError('Unexpected TS record count')
if ts.height != ts.select(['activity_year', 'lei']).unique().height:
    raise ValueError('TS year/LEI is not unique')
if ts['activity_year'].unique().to_list() != ['2025']:
    raise ValueError('Wrong TS year')
lar = pl.read_parquet(ROOT / 'data/staging/hmda_2025_de.parquet')
dim = lar.select(['activity_year', 'lei']).unique().join(
    ts.select(['activity_year','lei','respondent_name','agency_code']),
    on=['activity_year','lei'], how='left', validate='1:1').sort('lei')
if dim['respondent_name'].null_count():
    raise ValueError('Unmatched TS lender')
out = ROOT / 'data/staging/dim_lender.parquet'
dim.write_parquet(out, compression='zstd')
with archive.open('rb') as stream:
    digest = hashlib.file_digest(stream,'sha256').hexdigest()
manifest = {'source_url':'https://files.ffiec.cfpb.gov/static-data/snapshot/2025/2025_public_ts_csv.zip',
            'retrieval_date':'2026-10-27', 'sha256':digest, 'bytes':archive.stat().st_size,
            'national_ts_rows':len(rows), 'delaware_lenders':dim.height,
            'note':'lar_count is national institution volume, not Delaware volume; excluded from dimension.'}
(ROOT / 'docs/evidence/lender_reference_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(f'Built lender dimension: {dim.height} matched LEIs')
