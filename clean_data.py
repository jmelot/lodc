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
                        ("AVE", "Ave"),
                        (" st ", " St "),
                        ("N Capitol St", "North Capitol St"),
                        ("Circke", "Circle"),
                        ("Condos", "Condominiums"),
                        ("Bldg", "Building"),
                        ("Thurgood Marshall or 400 North Capitol", "Thurgood Marshall Building"),
                        ("MLK Jr", "MLK"),
                        ("Collumbus", "Columbus"),
                        ("Nationals Park Stadium", "Nationals Stadium"),
                        ("Convention Center SE", "Convention Center"),
                        ("Building E facing window", "building"),
                        ("Mass Ave", "Massachusetts Ave"),
                        ("Middle of sidewalk in front of Metropolitan News", ""),
                        (" in the corner with CVS entrance", ""),
                        (" east side at corner", ""),
                        (" Giant", ""),
                        (" DC 20002", ""),
                        (" on the MBT trail", ""),
                        (" North side", ""),
                        (" In nook of the building on the 21st St side", ""),
                        (" in front of pool window", ""),
                        (" in front of parking garage entrance", ""),
                        ("Thurgod Marshall Building", "Thurgood Marshall Building"),
                        ("MLK library", "MLK Library")
                       ]
ADDRESS_ENDINGS = ["Condominiums", "Library"]
BIRD_REPLACEMENTS = [("?", ""), ("sp.", "species"),
                     ("Dove/Pigeon", "Dove"),
                     ("Rock Pigeon", "Rock Dove"),
                     ("Pigeon/Rock Dove", "Rock Dove"),
                     (" Breasted", "-Breasted"),
                     (" Feathers Only)", ""),
                     ("Empidonax", "Empidonax Flycatcher Species"),
                     ("Empid. Flycatcher", "Empidonax Flycatcher Species"),
                     ("Sp.", "Species"),
                     ("Grey", "Gray"),
                     ("Needs Id See Photo", "Unknown")
                    ]
DIRECTIONS = ["NE", "NW", "SE", "SW"]
CHINATOWN_COL = "Chinatown Route: Closest Address"
UNION_COL = "Union Station  Route: Closest Address"
OTHER_STREET_COLS = ["Street Address", "Location Found", "Street Address Where Found"]
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
        clean = re.sub(rf"(?i)(\b){direct}(\b)", rf"\1{direct}\2", clean)
    if "&" not in clean:
        clean = re.sub(rf"(\b)({'|'.join(DIRECTIONS)})(\b)", r"\1\2", clean).strip()
    for sep in [" - ", ",", "("]:
        clean = clean.split(sep)[0]
    for s_from, s_to in ADDRESS_REPLACEMENTS:
        clean = clean.replace(s_from, s_to)
    clean = re.sub(r"(?i)\s+noma(\b|$)", "", clean)
    clean = re.sub(r"Condominium(\b)", r"Condominiums\1", clean)
    for needs_nw in ["Massachusetts Ave", "I St", "Palmer Alley", "New York Ave", "New Jersey Ave", "Wisconsin Ave", "901 4th St"]:
        clean = re.sub(rf"{needs_nw}\s*$", f"{needs_nw} NW", clean)
    clean = re.sub(r"NW\s*/.*", "NW", clean)
    clean = " ".join(clean.strip().split())
    for ending in ADDRESS_ENDINGS:
        clean = re.sub(rf"({ending}).*", r"\1", clean)
    clean = re.sub(r" to the right.*", "", clean)
    clean = re.sub("-+", "-", clean)
    clean = clean.replace("Thurgood Marshall Building NW", "Thurgood Marshall Building")
    return clean if clean else "No address"


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
    bird = bird.split("(")[0].split(",")[0].title().replace("'S", "'s")
    for from_s, to_s in BIRD_REPLACEMENTS:
        bird = bird.replace(from_s, to_s)
    return bird.strip()


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
                    for col in OTHER_STREET_COLS:
                        if col in line:
                            address_col = col
            cleaned_addr = clean_address(line[address_col])
            line["Clean Address"] = cleaned_addr
            line[DEFAULT_ADDR_COL] = line[address_col]
            if not line[BIRD_COL]:
                continue
            if not "Sex, if known" in line:
                line["Sex, if known"] = get_bird_gender(line[BIRD_COL])
            cleaned_bird = clean_bird(line[BIRD_COL])
            if cleaned_bird.lower() == "deleted":
                continue
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
    return int(re.search(r"\d\d\d\d", filename).group(0))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_fi", default="2021 Lights Out Inventory FINAL.csv")
    parser.add_argument("--output_dir", default="LODC_clean")
    args = parser.parse_args()

    year = get_year(args.input_fi)
    output_stub = Path(args.output_dir) / str(year)
    main(args.input_fi, year, output_stub)
