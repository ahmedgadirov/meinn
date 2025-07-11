import csv

csv_file = "/home/ahmd/Desktop/menu pizza inn/menu_items_export.csv"

with open(csv_file, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    headers = next(reader)
    
    print(f"Total headers: {len(headers)}")
    for i, header in enumerate(headers):
        print(f"{i+1:2d}: {repr(header)}")
    
    print("\n" + "="*60)
    print("First 3 data rows:")
    
    for row_num in range(3):
        try:
            row = next(reader)
            print(f"\nRow {row_num + 1}: {len(row)} values")
            if len(row) != len(headers):
                print(f"ERROR: Expected {len(headers)} columns, got {len(row)}")
                print("Row content:")
                for i, value in enumerate(row):
                    print(f"  {i+1:2d}: {repr(value)}")
                break
            else:
                # Show first 10 values
                for i in range(min(10, len(row))):
                    print(f"  {i+1:2d}: {repr(row[i])}")
                print("  ...")
        except StopIteration:
            print(f"No more rows after {row_num}")
            break
