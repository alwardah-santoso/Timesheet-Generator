import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sheets_adapter import baca_data

data = baca_data(tab_name="Summary")

print("Row 4:", data[3] if len(data) > 3 else None)
