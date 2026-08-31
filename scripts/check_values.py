import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sheets_adapter import baca_data

data = baca_data(tab_name="Summary")

if len(data) >= 47:
    print("Row 46:", data[45])
    print("Row 47:", data[46])
else:
    print(f"Only {len(data)} rows found.")
