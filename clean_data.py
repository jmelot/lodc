import argparse
import csv
import re

from collections import OrderedDict
from pathlib import Path


CLEAN_SHEET_COLS = ["Date", "Bird Species, if known", "Clean Bird Species", "Sex, if known",
                                     "Address where found", "Clean Address", "CW Number", "Disposition",
                                     "Status: Released-- Nearest address/landmark", "Last Name", "What route?",
                                     "Status", "Approx. time you found the bird"]
UNKNOWN_ADDRESS = "Unknown"
AUDI = "100 Potomac Ave SW"
CUA = "620 Michigan Ave NE"
CITY_CENTER = "825 10th St NW"
GU_LAW = "600 New Jersey Ave NW"
GU = "3700 O St NW"
THURGOOD = "1 Columbus Circle NE"
MLK = "901 G St NW"
HART_SENATE = "120 Constitution Ave NE"
TEAMSTERS = "25 Louisiana Ave NW"
CONVENTION_CTR = "801 Mt Vernon Pl NW"
ADDRESS_REPLACEMENTS = [
    ("corner at 7th and New York Ave NW", ""),
    ("at the corner with Palmer Alley NW", ""),
    ("NE Building", ""),
    ("Consitution", "Constitution"),
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
    ("Thurgood Marshall or 400 North Capitol", THURGOOD),
    ("MLK Jr", MLK),
    ("Collumbus", "Columbus"),
    ("Nationals Park Stadium", "Nationals Stadium"),
    ("Convention Center SE", CONVENTION_CTR),
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
    ("Thurgod Marshall Building", THURGOOD),
    ("MLK library", MLK),
    ('In front of the entrance labeled "Stonebridge Carras"', "151 N St NE"),
    ("1010 10th St", "1010 10th St NW"),
    ("1050 17th St NW at L St", "1050 17th St NW"),
    ("1050 K St NW parking garage entrance", "1050 K St NW"),
    ("1090 I St NW WDC 20268", "1090 I St NW"),
    ("111 Massachusetts NW", "111 Massachusetts Ave NW"),
    ("1111 19th NW", "1111 19th St NW"),
    ("1111 20th St", "1111 20th St NW"),
    ("NY Ave ", "New York Ave "),
    (" Sts ", " St "),
    ("Dan found the bird at the DOEE building He will take it to CW", ""),
    (" Place ", " Pl "),
    ("N Carolina", "North Carolina"),
    ("1313 L St NW in bike lane", "1313 L St NW"),
    ("1331 Pennysylvania Ave NW", "1331 Pennsylvania Ave NW"),
    ("13th and U St NW NW corner near Alero", "13th and U St NW"),
    ("1815 7th St NW by the Shaw metro entrance", "1815 7th St NW"),
    ("18th and P St NW NE corner", "18th and P St NW"),
    ("circle", "Circle"),
    ("1010 10th St NW NW", "1010 10th St NW"),
    ("1201 15th St", "1201 15th St NW"),
    ("1500 bl 32nd St NW", "1500 32nd St NW"),
    ("NW NW", "NW"),
    (" at the corner with Palmer Alley NW", ""),
    ("1201 15th St", "1201 15th St NW"),
    ("15th and L St", "15th and L St NW"),
    ("17th and L", "17th and L St NW"),
    ("810 7th St SE or NW?", "810 7th St NW"),
    (" near Lafayette Park", ""),
    ("Audi Field Club shop", AUDI),
    ("Audi Stadium", AUDI),
    ("Audi Stadium by store door fronting R St SW and facing North", AUDI),
    ("BB&T Bank", UNKNOWN_ADDRESS),
    ("Brookland in northeast DC", UNKNOWN_ADDRESS),
    ("CUA campus", CUA),
    ("City Center courtyard", CITY_CENTER),
    ("City Center: Burberry", CITY_CENTER),
    ("City Center: H St and 10th", CITY_CENTER),
    ("Adas Israel historic synagogue at 3rd and F NW", "3rd St and F St NW"),
    ("Air and Space Museum", "600 Independence Ave SW"),
    ("Arena Stage", "1101 6th St SW"),
    ("Close to the Embassy of Afghanistan", "2233 Wisconsin Ave NW"),
    ("Coast Guard Building SE", "2703 Martin Luther King Jr Ave SE"),
    ("Conn Ave NW", "Connecticut Ave NW"),
    ("18th and Pennsylvania NW", "18th and Pennsylvania Ave NW"),
    (" and Bouqueria Entrance", ""),
    ("NW and", "NW"),
    ("NE and", "NE"),
    (" corner of 7th and Mt Vernon", ""),
    ("Convention Center corner at 7th and NY Ave", "7th St and New York Ave NW"),
    ("Convention Center overpass", "801 Mt Vernon Pl NW"),
    ("Corner of H St and 18th", "H St and 18th St NW"),
    ("Corner of New Jersey and D St NW", "New Jersey Ave and D St NW"),
    ("Date and location unknown", UNKNOWN_ADDRESS),
    ("Dept of Transportation near Navy Yard", "250 M St SE"),
    ("Dior", "933 Palmer Alley NW"),
    ("Dumbarton Oaks Greenhouse", ""),
    ("E St", ""),
    ("EMS Station", UNKNOWN_ADDRESS),
    ("Eagle Bank NW corner", "700 K St NW"),
    ("Eagle Company", UNKNOWN_ADDRESS),
    ("Eastern Ave", ""),
    ("Eastern Market", ""),
    ("Entrance", ""),
    ("FS Key Park", "1198 34th and M St NW"),
    ("Road", "rd"),
    ("Found in front of 1050 17th St NW", "1050 17th St NW"),
    ("Found in front of Dolcezza north of Dupont Circle", "1704 Connecticut Ave NW"),
    ("Found in the courtyard of 1616 P St NW", "1616 P St NW"),
    ("Freshly dead ovenbird found in front of my small apartment building when I returned home from my route 1917 2nd St NE The glass entry door often has a light on inside all night", "1917 2nd St NE"),
    ("Front of BBT Bank", UNKNOWN_ADDRESS),
    ("GU Law Center", GU_LAW),
    ("GU Law School", GU_LAW),
    ("GU Law School Fitness Center", GU_LAW),
    ("GU Law School Library", "111 G St NW"),
    ("GU Sport and Fitness Center", GU_LAW),
    ("GW Hospital", "3800 Reservoir Rd NW"),
    ("Georgetown University Lauinger Library", GU),
    ("Georgetown Law School", GU_LAW),
    ("Georgetown Law School Fitness Center", GU_LAW),
    ("Georgetown Law Sport and Fitness Center", GU_LAW),
    ("Georgetown University", GU_LAW),
    ("Georgetown University Law School", GU_LAW),
    ("Georgetown University", GU),
    ("Georgetown University at New North Hall glass doors", GU),
    ("GWU", "2121 I St NW"),
    ("Glass Entry 430 E St NW Wash DC", "430 E St NW"),
    ("Glass entry 430 E St NW WDC", "430 E St NW"),
    ("Grey Catbird found dead on ground of outdoor patio of Milk Bar on 1090 I St NW", "1090 I St NW"),
    ("Husband found the bird Juvenile On sidewalk in front of the Georgetown Valet shop at 145 N St NE", "145 N St NE"),
    ("I found this bird while on my lunch break It was still warm at approx 1 pm Found in front of 1040 17th St NW", "1040 17th St NW"),
    ("In front of Audi Field Sports Shop main door facing north R St SW", AUDI),
    ("M St side of 1275 1st St NE", "1275 1st St NE"),
    ("M and 17th NW corner", "M St and 17th Tt NW"),
    ("South side of 1601 K St", "1601 K St NW"),
    ("glass entry 430 E St NW", "430 E St NW"),
    ("World Bank 1818 H St NW", "1818 H St NW"),
    ("No address", UNKNOWN_ADDRESS),
    ("Other", UNKNOWN_ADDRESS),
    ("This was at 700 2nd street NE As we started to drive home", "700 2nd St NE"),
    ("in front of Tesla store on 9th St", "909 H St NW"),
    ("Glover Archibold Park", UNKNOWN_ADDRESS),
    ("Hall of States", "400-444 North Capitol St NW"),
    ("Harbour Square Condominiums", "500 N St SW"),
    ("Hart Senate Building", HART_SENATE),
    ("Hart Senate Office Building", HART_SENATE),
    ("In front of Spy Museum below windows facing west", "700 L'Enfant Plaza SW"),
    ("MLK Library", MLK),
    ("Marie H Reed Recreation Center NW", "2200 Champlain St NW"),
    ("Marriott Marquis Washington", "901 Massachusetts Ave NW"),
    ("Martin Luther King Jr Memorial Library", MLK),
    ("Martin Luther King Library", MLK),
    ("National Arboretum", UNKNOWN_ADDRESS),
    ("National Geographic", "1145 17th St NW"),
    ("National Mall", UNKNOWN_ADDRESS),
    ("National Zoo", "3001 Connecticut Ave NW"),
    ("Nationals Stadium", "1500 S Capitol St SE"),
    ("Old Soldiers and Sailors Home NW", "140 Rock Creek Church Rd NW #7"),
    ("On east side of Metropolitan Branch Trail at R St NE", "Metropolitan Branch Trail and R St NE"),
    ("One Dupont Circle", "1 Dupont Circle NW"),
    ("One Dupont Circle NW side", "1 Dupont Circle NW"),
    ("Del Frisco's restaurant in courtyard", ""),
    ("Potbelly", "1050 K St NW"),
    ("Riverside Condominiums", "1435 4th St SW"),
    ("Rock Creek Park Maintenance Yard", "Maintenance Rd NW"),
    ("Rock Creek Stables", "5100 Glover Rd NW"),
    ("SEC", "100 F St NE"),
    ("SEC Building", "100 F St NE"),
    ("Senate Hart Building", HART_SENATE),
    ("Shaw Metro Station", "1701 8th St NW"),
    ("Souvenir City", "1001 K St NW"),
    ("TD Bank", "1753 Connecticut Ave NW"),
    ("TMB", THURGOOD),
    ("Teamster Building", TEAMSTERS),
    ("Teamsters Building", TEAMSTERS),
    ("Teamsters' Building", TEAMSTERS),
    ("Techworld Plaza", "800 K St NW"),
    ("The Convention Center", CONVENTION_CTR),
    ("The National Zoo", "3001 Connecticut Ave NW"),
    ("Thurgood Marshall", THURGOOD),
    ("Thurgood Marshall Building", THURGOOD),
    ("Tumi Store", "1051 H St NW"),
    ("Washington DC", UNKNOWN_ADDRESS),
    ("Washington Monument", "2 15th St NW"),
    ("601 K St NW AC Hotel", "601 K St NW"),
    ("Kingman Island", UNKNOWN_ADDRESS),
    (" on south facing window of B Building Opposite Ft McNair Closest intersection is P and 4th SW", ""),
    ("455 Massachusetts Avenu NW", "455 Massachusetts Ave NW"),
    ("NJ Ave", "New Jersey Ave"),
    ("NY Ave", "New York Ave"),
    ("bl 32nd St NW", "block of 32nd St NW"),
    ("601 Massachusetts Ave/601 K St", "601 Massachusetts Ave NW"),
    ("new Jersey Ave", "New Jersey Ave"),
    ("Georgia W", UNKNOWN_ADDRESS),
    ("Washington", UNKNOWN_ADDRESS),
    ("No address", UNKNOWN_ADDRESS),
    (" by store door fronting R St SW and facing North", ""),
    (" A Building by front door on north side of building", ""),
    (" B Building", ""),
    (" Building A Breezeway north side", ""),
    (" Building B", ""),
    ("600 New Jersey Ave NNW", "600 New Jersey Ave NW"),
    ("600 New Jersey Ave NW Fitness Center", "600 New Jersey Ave NW"),
    ("600 New Jersey Ave NW Law School", "600 New Jersey Ave NW"),
    ("600 New Jersey Ave NW Library", "600 New Jersey Ave NW"),
    ("600 New Jersey Ave NW at New North Hall glass doors", "600 New Jersey Ave NW"),
    ("601 Massachusetts Ave Building", "601 Massachusetts Ave NW"),
    (" at the corner with Palmer Alley NW", ""),
    ("8th and I St corner Across TechWorld", "8th St and I St NW"),
    ("in front of Veterans Affairs building", ""),
    ("at the corner with Palmer Alley NW", ""),
    ("near Lafayette Park", ""),
    ("9th St side between G and H streets", ""),
    ("in front of main facade", ""),
    ("901 G St NW Library", "901 G St NW"),
    ("901 G St NW 901 G St NW", "901 G St NW"),
    (": next to curb in road", ""),
]
PRE_CLEAN_ADDRESS_REPLACEMENTS = [
    ("entry, 430 E St NW, WDC", "430 E St NW"),
    ("Glass Entry 430 E St., NW Wash DC", "430 E St NW"),
    ("Glass entry 430 E St NW. WDC", "430 E St NW"),
    ("Glass entry, 430 E ST., NW WDC", "430 E St NW"),
    ("Glass entry, 430 E St NW, WDC", "430 E St NW"),
    ("Glass entry, 430 E St., NW WDC", "430 E St NW"),
    ("Glass entry, 430 E St., NW WDC 20001", "430 E St NW"),
    ("Glass entry, 430 E St., NW, WDC", "430 E St NW"),
    ("Glass entry, 430 E st., NW WDC 20001", "430 E St NW"),
    ("Glass entry, west side 430 E St., NW WDC", "430 E St NW"),
    ("entry, 430 E St NW WDC", "430 E St NW"),
    ("entry, 430 E St NW, WDC", "430 E St NW"),
    ("glass entry 430 E St., NW", "430 E St NW"),
    ("glass entry, 430 E St NW, WDC", "430 E St NW"),
    ("glass entry, 430 E St., NW, WDC", "430 E St NW"),
    ("Found at NW corner (8th & P side) of the newer apartment building at 1490 7th St NW (the north half of the building containing the Giant).", "1490 7th St NW"),
    ("Whole Foods, 6th St, NE", "600 H St NE"),
    ("Glass entry, 430 E ST.", "430 E St NW"),
    ("Glass entry 430 E St NW. WDC", "430 E St NW"),
    ("Glass entry, 430 E St., NW", "430 E St NW"),
    ("Glass entry, 430 E st., NW", "430 E St NW"),
    ("Glass entry, 430 E ST., NW ", "430 E St NW"),
    ("Glass entry, 430 E ST., NW ", "430 E St NW"),
    ("Glass entry, 430 E St NW, WDC", "430 E St NW"),
    ("Glass entry, 430 E St NW, WDC", "430 E St NW"),
    ("Glass entry, 430 E St., NW", "430 E St NW"),
    ("Glass entry, 430 E St., NW, WDC", "430 E St NW"),
    ("Glass entry, west side", UNKNOWN_ADDRESS),
    ("glass entry, 430 E St NW, WDC", "430 E St NW"),
    ("430 E St. NW, glass entry", "430 E St NW"),
    ("glass entry 430 E St., NW", "430 E St NW"),
    ("glass entry 430 E St., NW", "430 E St NW"),
    ("entry, 430 E St NW", "430 E St NW"),
    ("entry, 430 E St NW, WDC", "430 E St NW"),
    ("Eagle Bank, NW corner, 20th and K Sts. NW", "20th St NW and K St NW"),
    ("NW corner, 18th and K Sts. NW", "18th St and K St NW"),
    ("1000, Massachusetts Ave NW ", "1000 Massachusetts Ave NW"),
    ("950 - 980 Maine SW, east side between buildings", "950-980 Maine Ave SW"),
    ("Alley, Capitol Hill", UNKNOWN_ADDRESS),
    ("2701 MLK Ave SE", "2701 Martin Luther King Jr Ave SE"),
    ("1 Columbus Circle NE Building", "1 Columbus Circle NE"),
    ("glass entry, 430 E St NW, WDC", "430 E St NW"),
    ("430 E St. NW, glass entry", "430 E St NW"),
    ("glass entry, 430 E St., NW, WDC", "430 E St NW"),
    ("glass entry 430 E St., NW", "430 E St NW"),
]

ADDRESS_ENDINGS = ["Condominiums", "Library"]
BIRD_SUBSTRING_MAPPINGS = [
    ("?", ""), ("sp.", "species"),
    (" Breasted", "-Breasted"),
    (" Feathers Only)", ""),
    ("Sp.", "Species"),
    ("Grey", "Gray"),
]
UNKNOWN_BIRD = "Unknown"
EMPID = "Empidonax Species"
BIRD_REPLACEMENTS = [("Dove/Pigeon", "Rock Dove"),
                     ("Rock Pigeon", "Rock Dove"),
                     ("Pigeon/Rock Dove", "Rock Dove"),
                     ("Empidonax", EMPID),
                     ("Empid. Flycatcher", EMPID),
                     ("Needs Id See Photo", UNKNOWN_BIRD),
                     ("Alder", "Alder Flycatcher"),
                     ("", UNKNOWN_BIRD),
                     ("Black And White Warbler", "Black-And-White Warbler"),
                     ("Black Throated Blue Warbler", "Black-Throated Blue Warbler"),
                     ("Black Throated Green Warbler", "Black-Throated Green Warbler"),
                     ("Blue-Throated Black Warbler", "Black-Throated Blue Warbler"),
                     ("Clay Colored Or Chipping Sparrow", "Sparrow Species"),
                     ("Dark Eyed Junco", "Dark-Eyed Junco"),
                     ("Eastern Wood Pewee", "Eastern Wood-Pewee"),
                     ("Empidonax Flycatcher Species Species Flycatcher", EMPID),
                     ("Empidomax Species", EMPID),
                     ("Flicker", "Northern Flicker"),
                     ("Flycatcher", EMPID),
                     ("Black-Throated Blue", "Black-Throated Blue Warbler"),
                     ("Gray Cheeked Thrush", "Gray-Cheeked Thrush"),
                     ("Junco", "Dark-Eyed Junco"),
                     ("Likely A Warbler", "Warbler Species"),
                     ("Kinglet", "Kinglet Species"),
                     ("Mallard", "Mallard Duck"),
                     ("Mourning Or Connecticut Warbler", "Warbler Species"),
                     ("Northern Parula Warbler", "Northern Parula"),
                     ("Northern Water Thrush", "Northern Waterthrush"),
                     ("Nuthatch", "Nuthatch Species"),
                     ("Ovenbird--1 Of 2 Found", "Ovenbird"),
                     ("Pewee And Flycatcher", EMPID),
                     ("Pied Billed Grebe", "Pied-Billed Grebe"),
                     ("Pigeon", "Rock Dove"),
                     ("Red Bellied Woodpecker", "Red-Bellied Woodpecker"),
                     ("Red Eyed Vireo", "Red-Eyed Vireo"),
                     ("Robin", "American Robin"),
                     ("Rock Dove/Pigeon", "Rock Dove"),
                     ("Ruby Crowned Kinglet", "Ruby-Crowned Kinglet"),
                     ("Ruby Throated Hummingbird", "Ruby-Throated Hummingbird"),
                     ("Rufous Sided Towhee", "Rufous-Sided Towhee"),
                     ("Savannah", "Savannah Sparrow"),
                     ("Sparrow", "Sparrow Species"),
                     ("Swainsons Thrush", "Swainson's Thrush"),
                     ("Swaison's Thrush", "Swainson's Thrush"),
                     ("Tennesee Warbler", "Tennessee Warbler"),
                     ("Thrush Or Sparrow", UNKNOWN_BIRD),
                     ("Thrush", "Thrush Species"),
                     ("Warbler Species - Possible Yellow-Rumped", "Warbler Species"),
                     ("White Throated Sparrow", "White-Throated Sparrow"),
                     ("Whippoorwill", "Whip-Poor-Will"),
                     ("Woodcock", "American Woodcock"),
                     ("Woodpecker", "Woodpecker Species"),
                     ("Yellow Bellied Sapsucker", "Yellow-Bellied Sapsucker"),
                     ("Yellow Billed Cuckoo", "Yellow-Billed Cuckoo"),
                     ("Yellow Rumped Warbler", "Yellow-Rumped Warbler"),
                     ("Yellowbreasted Flycatcher", "Yellow-Bellied Flycatcher"),
                     ("Yellowthroat", "Common Yellowthroat"),
                     ("Cardinal", "American Cardinal"),
                     ("Catbird", "Gray Catbird"),
                     ("Golden Crowned Kinglet", "Golden-Crowned Kinglet"),
                     ("Goldfinch", "American Goldfinch"),
                     ("Grackle", "Common Grackle"),
                     ("Hummingbird", "Hummingbird Species"),
                     ("Parula Warbler", "Northern Parula"),
                     ("Starling", "European Starling"),
                     ("Warbler", "Warbler Species"),
                     ("Empidonax Species Flycatcher", EMPID),
                     ("Mockingbird", "Northern Mockingbird")
                    ]
DIRECTIONS = ["NE", "NW", "SE", "SW"]
DEFAULT_ADDR_COL = "Address where found"
ALT_ADDR_COLS = [DEFAULT_ADDR_COL, "Chinatown Route: Closest Address", "Union Station  Route: Closest Address",
            "address1", "address2", "Street Address", "Location Found", "Street Address Where Found", "notes",
            "Location ", "Location", "Location                          (all District of Columbia addresses)"]
DEFAULT_BIRD_COL = "Bird Species, if known"
ALT_BIRD_COLS = [DEFAULT_BIRD_COL, "Species", "species"]


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
        clean = clean.replace(s_from, s_to)
    clean = addr.replace(".", "").split(";")[0].strip().replace("\n", " ")
    clean = clean.replace("&", "and").replace(" And ", " and ")
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
    clean = clean.replace("Thurgood Marshall Building NW", THURGOOD).replace(" NE Building", "")
    clean = clean.replace("NW NW", "NW")
    for from_s, to_s in [
        ("1 Columbus Circle NW", "1 Columbus Circle NE"),
        ("1 Columbus Circle", "1 Columbus Circle NE"),
        ("920 Mass", "920 Massachusetts Ave NW"),
        ("900 Mass", "900 Massachusetts Ave NW"),
        ("1 Dupont Circle NW side", "1 Dupont Circle NW"),
        ("801 Mt Vernon Pl NW corner at 7th and New York Ave NW", "801 Mt Vernon Pl NW"),
        ("850 10th St NW at the corner with Palmer Alley NW", "850 10th St NW"),
        ("931 H St NW or 900 Palmer Alley NW", "900 Palmer Alley NW"),
        ("Across from 1813 Wiltberger NW", "1813 Wiltberger NW"),
        ("ATF Building", "99 New York Ave NE"),
        ("Alley", UNKNOWN_ADDRESS),
        ("BB and T Bank", UNKNOWN_ADDRESS),
        ("Capital City Charter School", "100 Peabody St NW"),
        ("Connecticut Ave NW M St NW", "Connecticut Ave and M St NW"),
        ("Constitution Ave NW 10th St NW", "Constitution Ave and 10th St NW"),
        ("Convention Center NW", CONVENTION_CTR),
        ("Convention Center", CONVENTION_CTR),
        ("DOE Building", "1000 Independence Avenue SW"),
        ("Lauinger Library", GU),
        ("Lincoln Memorial", "2 Lincoln Memorial Cir NW"),
        ("M St NW 17th St NW", "M St and 17th St NW"),
        ("M St and 17th Tt NW", "M St and 17th St NW"),
        ("Found at NW corner", "1490 7th St NW"),
        ("NW corner", "18th St and K St NW"),
        ("O'Neill Federal Building", "200 C Street SW"),
        ("The 3001 Connecticut Ave NW", "3001 Connecticut Ave NW"),
        ("US Botanic Garden", "100 Maryland Ave SW"),
        ("US Botanic Garden atrium", "100 Maryland Ave SW"),
        ("US Capitol", "First St SE"),
        ("Union Station", "50 Massachusetts Ave NE"),
        ("Verizon Center", "601 F St NW"),
        ("Whole Foods", UNKNOWN_ADDRESS),
        ("Wisc and Massachusetts Ave NW", "Wisc Ave and Massachusetts Ave NW"),
        ("entry", "430 E St NW"),
        ("glass entry", "430 E St NW"),
        ("glass entry 430 NW", "430 E St NW"),
        ("1000", "1000 Massachusetts Ave NW"),
        ("Glass entry", "430 E St NW"),
        ("430 E", "430 E St NW"),
        ("430 NW", "430 E St NW")
    ]:
        if clean == from_s:
            clean = to_s
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
        print(line)
        return "Unknown"
    if "/" in date:
        date_parts = date.strip().split("/")
    else:
        date_parts = date.strip().split("-")
    if date == "9-30--2018":
        return "2018-09-30"
    if date == "10//28/20":
        return "2020-10-28"
    if len(date_parts) != 3:
        print(f"Unexpected date format: {line}")
        return "Unknown"
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
