import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sheets_adapter import baca_data

data = baca_data(tab_name="Summary")

print("Row 9 (Header?):", data[9] if len(data) > 9 else None)
print("Row 10:", data[10] if len(data) > 10 else None)
print("Row 11:", data[11] if len(data) > 11 else None)
print("Row 12:", data[12] if len(data) > 12 else None)
