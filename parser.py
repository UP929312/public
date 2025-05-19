import json

from pandas import *

SORT_BY_VALUE = True

# ---- Load and parse
xls = ExcelFile('FOI 18483511 Data v2.xlsx')
df = xls.parse(xls.sheet_names[0])
raw = df.to_dict()
combined_fields = list(zip(raw["Type"].values(), raw["Street Name"].values(), raw["Number of PCNs"].values()))
# types_of_tickets = set([x[0] for x in combined_fields])  # 'Car Park', 'On Street', 'CCTV', 'Bus'
parking_tickets_only = [x for x in combined_fields if x[0] == "On Street"]
# Zip and combine
broken_data = dict([(x[1], x[2]) for x in parking_tickets_only])
# ---- Fix and clean data
data = {}
# Fix certain street names' formatting (e.g. ` -> ')
for key in broken_data.keys():
    if isinstance(key, str):
        new_key = key.strip().replace("`", "'")
        for replacement_from, replacement_to in {"Rd": "Road", "St": "Street", "Ave": "Avenue", "Cres": "Crescent", "Dr": "Drive", "Ln": "Lane", "Pl": "Place"}.items():
            if new_key.endswith(replacement_from):
                new_key = new_key.removesuffix(replacement_from) + replacement_to
        data[new_key] = broken_data[key]
    else:
        data[key] = broken_data[key]
# ---- Delete the total (now gets removed from the type)
# del data["Total PCNs"]
# ---- Save
with open("pre_parsed.py", "w") as f:
    f.write("# Path: pre_parsed.py\n")
    f.write("# This file is auto-generated. Do not edit manually.\n")
    f.write(f"DATA = {json.dumps(dict(sorted(data.items(), key=lambda x: x[1 if SORT_BY_VALUE else 0], reverse=True if SORT_BY_VALUE else False)), indent=4)}\n")
# print(data)
# print(max(data.values()), min(data.values()))
print(max(data.items(), key=lambda x: x[1]), min(data.items(), key=lambda x: x[1]))
