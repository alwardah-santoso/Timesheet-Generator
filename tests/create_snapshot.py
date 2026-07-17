import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import core
import sheets_adapter

def main():
    print("Building dataframes from Google Sheets...")
    data = sheets_adapter.build_dataframes(sheets_adapter.TIMESHEET_SS_ID)
    names = data["names_list"]
    print("Found names:", names)
    if not names:
        print("No names found!")
        return

    target_name = names[0]
    print(f"Processing target name: {target_name}")
    name_data = sheets_adapter.get_shifts_for_name(data, target_name)
    _, output = core.process_from_sheets_data(name_data, target_name)

    snapshot_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "snapshot_reference.json")
    with open(snapshot_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, default=str)
    print(f"Saved snapshot to {snapshot_path}")

if __name__ == "__main__":
    main()
