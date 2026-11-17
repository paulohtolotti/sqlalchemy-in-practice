from csv import DictReader

with open("./data/leads-100.csv", "r", encoding="utf-8") as f:
    reader = DictReader(f)
    records = [reader]

    print(len(records))
