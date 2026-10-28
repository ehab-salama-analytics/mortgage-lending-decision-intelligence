"""Run staging build and independent validation in dependency order."""
import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('action', choices=['build', 'validate', 'report', 'all'])
args = parser.parse_args()
scripts = []
if args.action in ('build', 'all'):
    scripts.append('transformation/build_staging.py')
    scripts.append('validation/validate_staging.py')
    scripts.append('transformation/build_lender_reference.py')
    scripts.append('validation/validate_source_reference.py')
    scripts.append('transformation/build_outcome_counts.py')
    scripts.append('validation/validate_outcome_counts.py')
    scripts.append('transformation/build_outcome_rates.py')
if args.action in ('validate', 'all'):
    scripts.append('validation/validate_staging.py')
    scripts.append('validation/validate_source_reference.py')
    scripts.append('validation/validate_outcome_counts.py')
    scripts.append('validation/validate_outcome_rates.py')
if args.action in ('report','all'):
    scripts.append('export_management_report.py')
    scripts.append('export_power_bi.py')
for script in scripts:
    subprocess.run([sys.executable, '-X', 'utf8', str(ROOT / 'src' / script)], cwd=ROOT, check=True)
