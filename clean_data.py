import argparse
import csv
import re

from pathlib import Path


CLEAN_SHEET_COLS = ["Date", "Bird Species, if known", "Clean Bird Species", "Sex, if known",
                                     "Address where found", "Clean Address", "CW Number", "Disposition",
                                     "Status: Released-- Nearest address/landmark", "Last Name", "What route?",
                                     "Status", "Approx. time you found the bird"]
ADDRESS_REPLACEMENTS = [("Consitution", "Constitution"),
                        ("Maine SW", "Maine Ave SW"),
                        ("First", "1st"),
                        ("Second", "2nd"),
                        ("Third", "3rd"),
                        ("Fourth", "4th"),
                        ("Fifth", "5th"),
                        ("Sixth", "6th"),
                        ("Seventh", "7th"),
                        ("Eighth", "8th"),
                        ("Ninth", "9th"),
                        ("Street", "St"),
                        ("Avenue", "Ave"),
                        ("Circke", "Circle"),
                        ("Condos", "Condominiums"),
                        ("Bldg", "Building"),
                        ("Thurgood Marshall or 400 North Capitol", "Thurgood Marshall Building"),
                        ("MLK Jr", "MLK"),
                        ("Collumbus", "Columbus")
                       ]
ADDRESS_ENDINGS = ["Condominiums", "Library"]
BIRD_REPLACEMENTS = [("?", ""), ("sp.", "species"),
                     ("Dove/Pigeon", "Dove"),
                     ("Rock Pigeon", "Rock Dove"),
                     ("Pigeon/Rock Dove", "Rock Dove"),
                     (" breasted", "-breasted"),
                     (" Breasted", "-breasted")
                    ]
DIRECTIONS = ["NE", "NW", "SE", "SW"]
CHINATOWN_COL = "Chinatown Route: Closest Address"
UNION_COL = "Union Station  Route: Closest Address"
STREET_COL = "Street Address"
DEFAULT_ADDR_COL = "Address where found"
BIRD_COL = "Bird Species, if known"


def clean_address(addr: str) -> str:
    """
    Normalize address string
    :param addr: address string to be normalized
    :return: normalized address
    """
    clean = addr.replace(".", "").split(";")[0]
    for direct in DIRECTIONS:
        clean = clean.replace(f", {direct}", f" {direct}")
        clean = re.sub(rf"(?i)(\b){direct}", rf"\1{direct}", clean)
    clean = re.sub(rf"(\b)({'|'.join(DIRECTIONS)}).*", r"\1\2", clean).strip()
    parts = clean.split(",")
    street_parts = [p for p in parts if any([direct in p for direct in DIRECTIONS])]
    if len(street_parts) > 0:
        clean = street_parts[0]
    elif len(parts) > 0:
        clean = parts[0]
    paren_parts = [p.replace(")", "") for p in clean.split("(")]
    street_paren_parts = [p for p in paren_parts if any([direct in p for direct in DIRECTIONS])]
    if len(street_paren_parts) > 0:
        clean = street_paren_parts[0]
    elif len(paren_parts) > 0:
        clean = paren_parts[0]
    for s_from, s_to in ADDRESS_REPLACEMENTS:
        clean = clean.replace(s_from, s_to)
    clean = re.sub(r"Condominium(\b)", r"Condominiums\1", clean)
    clean = " ".join(clean.strip().split())
    clean = re.sub(r"(?i)\s+noma(\b|$)", "", clean)
    for ending in ADDRESS_ENDINGS:
        clean = re.sub(rf"({ending}).*", r"\1", clean)
    clean = re.sub("-+", "-", clean)
    return clean if clean else "No address"


def clean_bird(bird: str) -> str:
    """
    Normalize name of bird
    :param bird: Original name of the bird
    :return: Normalized name of the bird
    """
    bird = bird.split("(")[0].split(",")[0]
    for from_s, to_s in BIRD_REPLACEMENTS:
        bird = bird.replace(from_s, to_s)
    return bird.strip().title().replace("'S", "'s")


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
            address_col = DEFAULT_ADDR_COL
            if address_col not in line:
                if (CHINATOWN_COL in line) and line[CHINATOWN_COL]:
                    address_col = CHINATOWN_COL
                elif (UNION_COL in line) and line[UNION_COL]:
                    address_col = UNION_COL
                else:
                    address_col = STREET_COL
            cleaned_addr = clean_address(line[address_col])
            line["Clean Address"] = cleaned_addr
            if not line[BIRD_COL]:
                continue
            cleaned_bird = clean_bird(line[BIRD_COL])
            line["Clean Bird Species"] = cleaned_bird
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
    Writes csv mapping addresses to years to bird counts
    :param data: Dict mapping addresses to years to bird counts
    :param output_prefix: Prefix of output file
    :return: None
    """
    with open(f"{output_prefix}_bldg_counts.csv", mode="w") as f:
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
    return int(re.search(r"\d\d\d\d", filename).group(0))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_fi", default="2021 Lights Out Inventory FINAL.csv")
    parser.add_argument("--output_dir", default="LODC_clean")
    args = parser.parse_args()

    year = get_year(args.input_fi)
    output_stub = Path(args.output_dir) / str(year)
    main(args.input_fi, year, output_stub)
