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

def clean_bird(bird):
    bird = bird.split("(")[0].split(",")[0].replace("?",
            "").replace("sp.", "species").replace("Rose breasted ", "Rose-breasted ").strip()
    return bird

if __name__ == "__main__":
    out = csv.DictWriter(open("clean.csv", mode="w"), fieldnames=["Date", "Bird Species, if known", "Clean Bird Species", "Sex, if known", "Address where found", "Clean Address", "CW Number", "Disposition", "Status: Released-- Nearest address/landmark", "Last Name", "What route?", "Status", "Approx. time you found the bird"])
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
        writer = csv.DictWriter(f, fieldnames = ["Building", "Bird", "Count"])
        writer.writeheader()
        for address in sorted(address_to_bird.keys()):
            for bird in sorted(address_to_bird[address].keys()):
                writer.writerow({"Building": address, "Bird": bird, "Count": address_to_bird[address][bird]})


