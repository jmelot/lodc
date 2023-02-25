# lodc

This repository contains scripts to clean up and reformat historical Lights Out DC data. To clean and reformat a directory of data, use

`python clean_data_dir.py`

This will read and write files to default locations. Run with `-h` to view command line options.

This script outputs four files:

* `all_years_bird_bldg_counts.csv` - counts of strikes per bird, building, and year
* `all_years_bird_counts.csv` - counts of total strikes for each bird species and year
* `all_years_bldg_counts.csv` - counts of total bird strikes for each building per year
* `all_years_clean.csv` - complete data for all years, with cleaned address and bird name columns


### Manual cleanup notes

2016 - I had to rename the two address columns to "address1" and
"address2"

2017 - removed these lines from the end of the sheet:

,,,,,,,,
Gray shading:,,Birds left at site or released,,,,,,
Yellow shading:,,Missing birds,,,,,,
Green shading:,,"Given to Genoscape Project, UCLA",,,,,,
Orange shading:,,"Given to National Zoo, Bird House",,,,,,
"Note: Some ID numbers have been removed because the birds were not eligible for listing (flew off; not in DC, fledglings, etc.)",,,,,,,,
Final:,360 birds,,,,,,,
