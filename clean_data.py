import argparse
import csv
import re

from collections import OrderedDict
from pathlib import Path

from constants import ADDRESS_ENDINGS, ADDRESS_REPLACEMENTS, ALT_ADDR_COLS, ALT_BIRD_COLS, \
    BIRD_REPLACEMENTS, BIRD_SUBSTRING_MAPPINGS, CLEAN_SHEET_COLS, DEFAULT_ADDR_COL, \
    DEFAULT_BIRD_COL, DIRECTIONS, NEEDS_NW, PRE_CLEAN_ADDRESS_REPLACEMENTS, \
    UNKNOWN_ADDRESS, UNKNOWN_BIRD, UNKNOWN_DATE, ALWAYS_SUBS


def clean_address(addr: str) -> str:
    """
    Normalize address string
    :param addr: address string to be normalized
    :return: normalized address
    """
    if not addr:
        return UNKNOWN_ADDRESS
    clean = " ".join(addr.replace("\n", " ").replace("\r", " ").split())
    for s_from, s_to in PRE_CLEAN_ADDRESS_REPLACEMENTS:
        if clean == s_from:
            clean = s_to
    for s_search, s_to in ALWAYS_SUBS:
        if re.search(s_search, clean):
            clean = s_to
    # fix case of directions
    clean = clean.replace(".", "").split(";")[0].strip().replace("\n", " ")
    clean = clean.replace("&", "and").replace(" And ", " and ")
    for direct in DIRECTIONS:
        clean = re.sub(rf"(?i)(\b){direct}(\b)", rf"\1{direct}\2", clean)
        clean = clean.replace(f", {direct}", f" {direct}")
        clean = re.sub(rf"(?i)(\b){direct} and(\b)", rf"\1and\2", clean)
    for sep in [" - ", ",", "("]:
        clean = clean.split(sep)[0]
    for s_from, s_to in ADDRESS_REPLACEMENTS:
        clean = clean.replace(s_from, s_to)
    clean = re.sub(r"(?i)\s+noma(\b|$)", "", clean)
    clean = re.sub(r"Condominium(\b)", r"Condominiums\1", clean)
    for needs_nw in NEEDS_NW:
        clean = re.sub(rf"{needs_nw}\s*$", f"{needs_nw} NW", clean)
    clean = re.sub(r"NW\s*/.*", "NW", clean)
    clean = " ".join(clean.strip().split())
    for ending in ADDRESS_ENDINGS:
        clean = re.sub(rf"({ending}).*", r"\1", clean)
    clean = re.sub(r" to the right.*", "", clean)
    clean = re.sub("-+", "-", clean)
    clean = clean.replace("NW NW", "NW")
    return clean if clean else UNKNOWN_ADDRESS


def get_bird_gender(bird: str) -> str:
    """
    Attempt to extract bird gender
    :param bird: Unnormalized bird name
    :return: Gender ('male' or 'female'), if found
    """
    if re.search(r"(?i)\(m\.?\)", bird) or re.search(r"(?i)\bmale\b", bird):
        return "male"
    if re.search(r"(?i)\(f\.?\)", bird) or re.search(r"(?i)\bfemale\b", bird):
        return "female"


def clean_bird(bird: str) -> str:
    """
    Normalize name of bird
    :param bird: Original name of the bird
    :return: Normalized name of the bird
    """
    bird = bird.split("(")[0].split(",")[0].title().replace("'S", "'s").strip()
    bird = " ".join(bird.split())
    for from_s, to_s in BIRD_SUBSTRING_MAPPINGS:
        bird = bird.replace(from_s, to_s)
    for from_s, to_s in BIRD_REPLACEMENTS:
        if bird == from_s:
            bird = to_s
    if ("Unidentified" in bird) or ("Unknown" in bird):
        bird = UNKNOWN_BIRD
    bird = re.sub(r" Sp$", " Species", bird)
    return bird.strip()


def get_variably_named_val(column_alts: list, line: OrderedDict) -> str:
    """
    Return the value of the first address column alias that is not null
    :param column_alts: Different names for the same column
    :param line: OrderedDict representing the mapping from column names to values
    :return: The first non-null value in line of one of the `column_alts`
    """
    for alt in column_alts:
        if line.get(alt):
            return line[alt]


def clean_date(line: OrderedDict) -> str:
    """
    Normalize date to YYYY-MM-DD format
    :param line: Row of data
    :return: Normalized date
    """
    date = ""
    if line.get("Date"):
        date = line["Date"]
    elif line.get("date"):
        date = line["date"]
    if not date:
        print(f"No date column in {line}")
        return UNKNOWN_DATE
    separators = ["/", "-"]
    for separator in separators:
        if separator in date:
            date_parts = [p for p in date.strip().split(separator) if p]
    if len(date_parts) != 3:
        print(f"Unexpected date format: {line}")
        return UNKNOWN_DATE
    month = date_parts[0] if len(date_parts[0]) == 2 else "0"+date_parts[0]
    day = date_parts[1] if len(date_parts[1]) == 2 else "0"+date_parts[1]
    year = date_parts[2] if len(date_parts[2]) == 4 else "20"+date_parts[2]
    return f"{year}-{month}-{day}"


def get_cleaned_data(input_fi: str, year: int) -> tuple:
    """
    Cleans data, returning a tuple of dicts:
      * Cleaned rows
      * Dict mapping addresses to years to bird counts
      * Dict mapping birds to years counts
    :param input_fi: File containing raw data
    :param year: Year of data being cleaned
    :return: Tuple of data dicts as specified above
    """
    address_to_bird = {}
    bird_counts = {year: {}}
    cleaned_rows = []

    with open(input_fi) as f:
        for line in csv.DictReader(f):
            # clean up bird species
            raw_bird = get_variably_named_val(ALT_BIRD_COLS, line)
            if (not raw_bird) or (raw_bird == "Not used"):
                continue
            if not "Sex, if known" in line:
                line["Sex, if known"] = get_bird_gender(raw_bird)
            cleaned_bird = clean_bird(raw_bird)
            if cleaned_bird.lower() == "deleted":
                continue
            line[DEFAULT_BIRD_COL] = raw_bird
            line["Clean Bird Species"] = cleaned_bird

            # clean up address
            raw_addr = get_variably_named_val(ALT_ADDR_COLS, line)
            if not raw_addr:
                print(f"Warning, no address for line: {line}")
            cleaned_addr = clean_address(raw_addr)
            line["Clean Address"] = cleaned_addr
            line[DEFAULT_ADDR_COL] = raw_addr
            line["Date"] = clean_date(line)
            cleaned_rows.append({k: v for k, v in line.items() if k in CLEAN_SHEET_COLS})
            if cleaned_addr not in address_to_bird:
                address_to_bird[cleaned_addr] = {year: {}}
            address_to_bird[cleaned_addr][year][cleaned_bird] = address_to_bird[cleaned_addr][year].get(cleaned_bird, 0)+1
            bird_counts[year][cleaned_bird] = bird_counts[year].get(cleaned_bird, 0)+1
    return cleaned_rows, address_to_bird, bird_counts


def write_clean_sheet(data: list, output_prefix: str) -> None:
    """
    Writes cleaned version of raw input data
    :param data: Cleaned data
    :param output_prefix: Prefix of output file
    :return: None
    """
    with open(f"{output_prefix}_clean.csv", mode="w") as f:
        writer = csv.DictWriter(f, fieldnames=CLEAN_SHEET_COLS)
        writer.writeheader()
        for row in data:
            writer.writerow(row)


def write_address_counts(data: dict, output_prefix: str) -> None:
    """
    Writes csvs mapping addresses to years to bird counts and addresses to bird counts
    :param data: Dict mapping addresses to years to bird counts
    :param output_prefix: Prefix of output file
    :return: None
    """
    with open(f"{output_prefix}_bird_bldg_counts.csv", mode="w") as f:
        writer = csv.DictWriter(f, fieldnames=["Building", "Bird", "Year", "Count"])
        writer.writeheader()
        for address in sorted(data.keys()):
            for year in sorted(data[address].keys()):
                for bird in data[address][year]:
                    writer.writerow({
                        "Building": address,
                        "Bird": bird,
                        "Count": data[address][year][bird],
                        "Year": year
                    })
    with open(f"{output_prefix}_bldg_counts.csv", mode="w") as f:
        writer = csv.DictWriter(f, fieldnames=["Building", "Year", "Count"])
        writer.writeheader()
        for address in sorted(data.keys()):
            for year in sorted(data[address].keys()):
                writer.writerow({
                    "Building": address,
                    "Count": sum([data[address][year][bird] for bird in data[address][year]]),
                    "Year": year
                })


def write_bird_counts(data: dict, output_prefix: str) -> None:
    """
    Writes csv mapping birds to years to bird counts
    :param data: Dict mapping birds to years to bird counts
    :param output_prefix: Prefix of output file
    :return: None
    """
    with open(f"{output_prefix}_bird_counts.csv", mode="w") as f:
        writer = csv.DictWriter(f, fieldnames=["Bird", "Year", "Count"])
        writer.writeheader()
        for year in sorted(data.keys()):
            for bird in data[year]:
                writer.writerow({
                    "Bird": bird,
                    "Count": data[year][bird],
                    "Year": year
                })


def main(input_fi: str, year: int, output_stub: str) -> None:
    """
    Cleans data and writes outputs
    :param input_fi: Raw input sheet
    :param year: Year the data is from
    :param output_stub: Prefix for output files
    :return: None
    """
    cleaned_rows, address_to_bird, bird_counts = get_cleaned_data(input_fi, year)
    write_clean_sheet(cleaned_rows, output_stub)
    write_address_counts(address_to_bird, output_stub)
    write_bird_counts(bird_counts, output_stub)


def get_year(filename: str) -> int:
    """
    Parse year (first four-digit sequence) out of filename
    :param filename: LODC-formatted filename
    :return: Year when data was collected
    """
    return int(re.search(r"\d\d\d\d", filename).group(0))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_fi", default="2021 Lights Out Inventory FINAL.csv")
    parser.add_argument("--output_dir", default="LODC_clean")
    args = parser.parse_args()

    year = get_year(args.input_fi)
    output_stub = Path(args.output_dir) / str(year)
    main(args.input_fi, year, output_stub)
