# lodc

This repository contains scripts to clean up and reformat historical Lights Out DC data. To clean and reformat a 
directory of data, install the requirements in `requirements.txt`, then use

`python clean_data_dir.py`

This will read and write files to default locations. Run with `-h` to view command line options.

This script outputs four files:

* `all_years_bird_bldg_counts.csv` - counts of strikes per bird, building, and year
* `all_years_bird_counts.csv` - counts of total strikes for each bird species and year
* `all_years_bldg_counts.csv` - counts of total bird strikes for each building per year
* `all_years_clean.csv` - complete data for all years, with cleaned address and bird name columns

You will need to download the relevant google sheet for each year as csv and put it in your
input directory (default name `LODC_spreadsheets`) before running the script. As of 2026-03-22, 
these were the csv names in my input directory:

```
2021 Lights Out Inventory FINAL.csv
2024 Lights Out DC bird inventory-FINAL.xlsx - Submissions.csv
LIghts Out Bird Inventory 2012-FINAL.xls - Sheet1.csv
LIghts Out Bird Inventory 2013-FINAL.xls - Sheet1.csv
LIghts Out DC 2023 Inventory - FINAL PUBLIC.xlsx - Lights Out DC 2023 - Final.csv
Lights Out Bird Inventory 2010-FINAL.xlsx - Sheet1 - Table 1 - Table 1.csv
Lights Out Bird Inventory 2011-FINAL.xlsx - Sheet1.csv
Lights Out Bird Inventory 2014-FINAL.xlsx - Sheet1.csv
Lights Out Bird Inventory 2015-FINAL.xlsx - Sheet1.csv
Lights Out Bird Inventory 2016-FINAL .xls - Raw list.csv
Lights Out Bird Inventory 2017-FINAL.xlsx - Raw List.csv
Lights Out Bird Inventory 2018-FINAL.xlsx - Submissions.csv
Lights Out Bird Inventory 2019-FINAL.xlsx - Submissions.csv
Lights Out Bird inventory 2020-FINAL.xlsx - Submissions.csv
Lights Out DC 2022 birds FINAL.xlsx - Submissions.csv
```

# Methods

## Addresses

See `clean_data.clean_address`. This could use some cleanup. It uses a combination of 
specific address replacements (e.g. `Lincoln Memorial, Washington, DC` is replaced by 
`2 Lincoln Memorial Circle NW`) and general rules (e.g. replacing `Avenue` with `Ave` in
all addresses). Generally, to fix a specific address, update `PRE_CLEAN_ADDRESS_REPLACEMENTS`,
and to fix a recurring issue or one that only affects part of an address, update `ADDRESS_REPLACEMENTS`. 

## Bird names

See `clean_data.clean_bird`. This similarly happens in two phases, with general replacements
in `BIRD_SUBSTRING_MAPPINGS` and specific ones that only affect a particular bird name in `BIRD_REPLACEMENTS`.

## Manual cleanup notes

2017 - removed these lines from the end of the sheet:

,,,,,,,,
Gray shading:,,Birds left at site or released,,,,,,
Yellow shading:,,Missing birds,,,,,,
Green shading:,,"Given to Genoscape Project, UCLA",,,,,,
Orange shading:,,"Given to National Zoo, Bird House",,,,,,
"Note: Some ID numbers have been removed because the birds were not eligible for listing (flew off; not in DC, fledglings, etc.)",,,,,,,,
Final:,360 birds,,,,,,,
