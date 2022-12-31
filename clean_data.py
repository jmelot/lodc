import csv
import re

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


if __name__ == "__main__":
    out = csv.DictWriter(open("clean.csv", mode="w"),
                         fieldnames=["Date", "Bird Species, if known", "Clean Bird Species", "Sex, if known",
                                     "Address where found", "Clean Address", "CW Number", "Disposition",
                                     "Status: Released-- Nearest address/landmark", "Last Name", "What route?",
                                     "Status", "Approx. time you found the bird"])
    out.writeheader()

    address_to_bird = {}

    with open("2021 Lights Out Inventory FINAL.csv") as f:
        for line in csv.DictReader(f):
            cleaned_addr = clean_address(line["Address where found"])
            line["Clean Address"] = cleaned_addr
            cleaned_bird = clean_bird(line["Bird Species, if known"])
            line["Clean Bird Species"] = cleaned_bird
            out.writerow(line)
            if cleaned_addr not in address_to_bird:
                address_to_bird[cleaned_addr] = {}
            address_to_bird[cleaned_addr][cleaned_bird] = address_to_bird[cleaned_addr].get(cleaned_bird, 0)+1

    with open("bldg_counts.csv", mode="w") as f:
        writer = csv.DictWriter(f, fieldnames=["Building", "Bird", "Count"])
        writer.writeheader()
        for address in sorted(address_to_bird.keys()):
            for bird in sorted(address_to_bird[address].keys()):
                writer.writerow({"Building": address, "Bird": bird, "Count": address_to_bird[address][bird]})


