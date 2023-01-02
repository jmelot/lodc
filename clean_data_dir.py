import argparse
import os

from pathlib import Path
from clean_data import get_cleaned_data, write_clean_sheet, write_address_counts, write_bird_counts, get_year


def write_data(input_dir: str, output_dir: str) -> None:
    """
    Clean and write out all years of data in a directory
    :param input_dir: Directory containing raw data
    :param output_dir: Directory where output files should be written
    :return: None
    """
    output_stub = Path(output_dir) / "all_years"
    cleaned_rows, address_to_bird, bird_counts = [], {}, {}
    for fi in os.listdir(input_dir):
        if fi.startswith("."):
            continue
        year = get_year(fi)
        curr_cleaned_rows, curr_address_to_bird, curr_bird_counts = get_cleaned_data(Path(input_dir) / fi, year)
        cleaned_rows.extend(curr_cleaned_rows)
        address_to_bird.update(curr_address_to_bird)
        bird_counts.update(curr_bird_counts)
    write_clean_sheet(cleaned_rows, output_stub)
    write_address_counts(address_to_bird, output_stub)
    write_bird_counts(bird_counts, output_stub)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", default="LODC_spreadsheets")
    parser.add_argument("--output_dir", default="LODC_clean")
    args = parser.parse_args()

    write_data(args.input_dir, args.output_dir)
