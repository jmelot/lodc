import argparse
import csv
from collections import OrderedDict
from clean_data import clean_date_value, clean_bird, clean_address

ADDRESS_COLS = ["Chinatown Route: Closest Address", "Union Route: Closest Address", "Southwest: Closest Address",
                "NoMa: Closest Address", "Address, if not listed above", "patients.address_found (CW)", "Address (BL)"]
BIRD_COLS = ["Bird Species, if known", "Other species not on list"]
CW_COLS = ["2023 CW ID = admissions.id", "CW Number (Jotform)"]


def clean_cw_id(cwid: str) -> str:
    if not cwid.strip():
        return None
    id_parts = cwid.strip().split("-")
    if len(id_parts) == 2:
        assert id_parts[0] == "23"
    return f"23-{id_parts[-1]}"


def coalese(values: list) -> str:
    for v in values:
        if v and v != "Unknown":
            return v


def clean_row(row: OrderedDict) -> OrderedDict:
    date = clean_date_value(row["Date Jotform (MMDDYYYY)"])
    addresses = [clean_address(row[k]) for k in ADDRESS_COLS]
    birds = [clean_bird(row[k]) for k in BIRD_COLS]
    cw_ids = [clean_cw_id(row[k]) for k in CW_COLS]
    cleaned = {
        "date": date,
        "address": coalese(addresses),
        "species": coalese(birds),
        "cw_id": coalese(cw_ids)
    }
    row.update(cleaned)
    return row


def get_canonical_row(rows: list) -> dict:
    """

    :param rows:
    :return:
    """
    best_row = {}
    for row in rows:
        row_copy = {k: v for k, v in row.items()}
        for k in row:
            if not row[k]:
                row_copy.pop(k)
        best_row.update(row_copy)
    return best_row


def deduplicate(input_data: str, output_data: str) -> None:
    """

    :param input_data:
    :param output_data:
    :return:
    """
    key_to_rows = {}
    row_id = 0
    max_col_row = {}
    with open(input_data) as f:
        for row in csv.DictReader(f):
            cleaned = clean_row(row)
            cleaned["id"] = row_id
            key = f"{cleaned['date']}-{cleaned['address']}-{cleaned['bird']}"
            if key not in key_to_rows:
                key_to_rows[key] = []
            key_to_rows[key].append(cleaned)
            if len(row.keys()) > len(max_col_row.keys()):
                max_col_row = row
            row_id += 1
    with open(output_data, mode="w") as out:
        writer = csv.DictWriter(out, fieldnames=["merged_id"]+list(max_col_row.keys()))
        writer.writeheader()
        for key, rows in key_to_rows.items():
            merged_id = None
            if len(rows) > 1:
                canonical_row = get_canonical_row(rows)
                canonical_row["merged_id"] = row_id
                canonical_row["id"] = row_id
                merged_id = row_id
                writer.writerow(canonical_row)
                row_id += 1
            for row in rows:
                row["merged_id"] = merged_id if merged_id else row["id"]
                writer.writerow(row)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_data", default="2023_combo_birds-CWmatch.csv")
    parser.add_argument("--output_data", default="2023_combo_birds-CWmatch_matched.csv")
    args = parser.parse_args()

    deduplicate(args.input_data, args.output_data)
