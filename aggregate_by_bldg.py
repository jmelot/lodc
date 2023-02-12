import csv
import re


def clean_address(addr):
    clean = addr.replace(", NW", " NW").replace(", NE", " NE").replace(", SE", " SE").replace(", SW", " SW").replace(".", "")
    clean = re.sub(r"(NE|NW|SE|SW).*", r"\1", clean).strip()
    parts = clean.split(",")
    street_parts = [p for p in parts if "NE" in p or "NW" in p or "SE" in p or "SW" in p]
    if len(street_parts) > 0:
        clean = street_parts[0]
    elif len(parts) > 0:
        clean = parts[0]
    paren_parts = [p.replace(")", "") for p in clean.split("(")]
    street_paren_parts = [p for p in paren_parts if "NE" in p or "NW" in p or "SE" in p or "SW" in p]
    if len(street_paren_parts) > 0:
        clean = street_paren_parts[0]
    elif len(paren_parts) > 0:
        clean = paren_parts[0]
    clean = clean.replace("Consitution", "Constitution").replace("Maine SW", "Maine Ave SW").replace("First", "1st").replace("Street", "St").replace("Avenue", "Ave")
    return clean.strip()


if __name__ == "__main__":
    out = csv.DictWriter(open("clean.csv", mode="w"), fieldnames=["Date", "Bird Species, if known", "Sex, if known", "Address where found", "Clean Address", "CW Number", "Disposition", "Status: Released-- Nearest address/landmark", "Last Name", "What route?", "Status", "Approx. time you found the bird"])
    out.writeheader()

    with open("2021 Lights Out Inventory FINAL.csv") as f:
        for line in csv.DictReader(f):
            line["Clean Address"] = clean_address(line["Address where found"])
            out.writerow(line)

