"""Compatibility entry point: prepare compact cards, never bundle every wiki."""
import runpy,sys
from pathlib import Path
sys.argv=[str(Path(__file__).with_name('refresh-catalog.py')), 'check' if '--check' in sys.argv else 'refresh']
runpy.run_path(sys.argv[0],run_name='__main__')
