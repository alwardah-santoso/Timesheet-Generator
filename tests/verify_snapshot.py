import sys
import json
import os

sys.path.insert(0, '/home/homelinux/file_exchange/timesheet-cleaner-spreadsheet-dev')
import core
import sheets_adapter

def main():
    data = sheets_adapter.build_dataframes(sheets_adapter.TIMESHEET_SS_ID)
    names = data["names_list"]
    if not names:
        print("No names found!")
        sys.exit(1)

    target_name = names[0]
    name_data = sheets_adapter.get_shifts_for_name(data, target_name)
    _, output = core.process_from_sheets_data(name_data, target_name)

    ref_path = '/home/homelinux/file_exchange/timesheet-cleaner-spreadsheet-dev/tests/snapshot_reference.json'
    with open(ref_path, 'r', encoding='utf-8') as f:
        ref = json.load(f)

    # Compare json representation
    output_json = json.loads(json.dumps(output, default=str))
    ref_json = json.loads(json.dumps(ref, default=str))

    if output_json == ref_json:
        print("SUCCESS: ZERO REGRESSION! Refactored output matches snapshot 100%.")
    else:
        print("FAILURE: Output differs from snapshot!")
        # Print differences
        for k in output_json:
            if k not in ref_json:
                print(f"Key {k} not in reference")
            elif output_json[k] != ref_json[k]:
                print(f"Diff in key: {k}")
                print(f"  Output: {output_json[k]!r}")
                print(f"  Ref   : {ref_json[k]!r}")
        sys.exit(1)

if __name__ == '__main__':
    main()
