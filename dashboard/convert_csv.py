import csv
import json

def convert_csv_to_json(csv_path, json_path):
    data = []
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data.append(row)
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

if __name__ == "__main__":
    convert_csv_to_json('ALLIANCE_nation_data_formatted.csv', 'ALLIANCE_nation_data_formatted.json')
