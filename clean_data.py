import argparse
import csv
import re

from pathlib import Path


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
                        ("Avenue", "Ave")
                       ]
BIRD_REPLACEMENTS = [("?", ""), ("sp.", "species"), ("Rose breasted ", "Rose-breasted ")]
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
    clean = addr.replace(".", "")
    for direct in DIRECTIONS:
        clean = clean.replace(f", {direct}", f" {direct}")
    clean = re.sub(rf"({'|'.join(DIRECTIONS)}).*", r"\1", clean).strip()
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
    return clean.strip()


def clean_bird(bird: str) -> str:
    """
    Normalize name of bird
    :param bird: Original name of the bird
    :return: Normalized name of the bird
    """
    bird = bird.split("(")[0].split(",")[0]
    for from_s, to_s in BIRD_REPLACEMENTS:
        bird = bird.replace(from_s, to_s)
    return bird.strip()


def main(input_fi: str, cleaned_fi: str, count_fi: str) -> None:
    """
    Cleans data and writes outputs
    :param input_fi: Raw input sheet
    :param cleaned_fi: Cleaned version of input_fi
    :param count_fi: Building-bird count data
    :return: None
    """
    cleaned_fi_fields = ["Date", "Bird Species, if known", "Clean Bird Species", "Sex, if known",
                                     "Address where found", "Clean Address", "CW Number", "Disposition",
                                     "Status: Released-- Nearest address/landmark", "Last Name", "What route?",
                                     "Status", "Approx. time you found the bird"]
    out = csv.DictWriter(open(cleaned_fi, mode="w"), fieldnames=cleaned_fi_fields)
    out.writeheader()

    address_to_bird = {}

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
            out.writerow({k: v for k, v in line.items() if k in cleaned_fi_fields})
            if cleaned_addr not in address_to_bird:
                address_to_bird[cleaned_addr] = {}
            address_to_bird[cleaned_addr][cleaned_bird] = address_to_bird[cleaned_addr].get(cleaned_bird, 0)+1

    with open(count_fi, mode="w") as f:
        writer = csv.DictWriter(f, fieldnames=["Building", "Bird", "Count"])
        writer.writeheader()
        for address in sorted(address_to_bird.keys()):
            for bird in sorted(address_to_bird[address].keys()):
                writer.writerow({"Building": address, "Bird": bird, "Count": address_to_bird[address][bird]})


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_fi", default="2021 Lights Out Inventory FINAL.csv")
    parser.add_argument("--output_dir", default="LODC_clean")
    args = parser.parse_args()

    year = re.search(r"\d\d\d\d", args.input_fi)
    output_stub = Path(args.output_dir) / year.group(0)
    main(args.input_fi, f"{output_stub}_clean.csv", f"{output_stub}_bldg_counts.csv")
