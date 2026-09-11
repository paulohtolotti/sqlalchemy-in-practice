from csv import DictReader

with open('./data/leads-100.csv', 'r', encoding='utf-8') as f:
    reader = DictReader(f)
    records = []
    for data in reader:
        records.append(data)

    print(len(records))