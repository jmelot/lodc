import argparse
import os

from pathlib import Path
from pydantic.utils import deep_update
from clean_data import get_cleaned_data, write_clean_sheet, write_address_counts, write_bird_counts, get_year


def write_data(input_dir: Path, output_dir: Path) -> None:
    """
    Clean and write out all years of data in a directory
    :param input_dir: Directory containing raw data
    :param output_dir: Directory where output files should be written
    :return: None
    """
    if not output_dir.exists():
        output_dir.mkdir()
    output_stub = output_dir / "all_years"
    cleaned_rows, address_to_bird, bird_counts = [], {}, {}
    for fi in input_dir.iterdir():
        if fi.name.startswith("."):
            continue
        year = get_year(fi.name)
        curr_cleaned_rows, curr_address_to_bird, curr_bird_counts = get_cleaned_data(fi, year)
        cleaned_rows.extend(curr_cleaned_rows)
        address_to_bird = deep_update(address_to_bird, curr_address_to_bird)
        bird_counts = deep_update(bird_counts, curr_bird_counts)
    write_clean_sheet(cleaned_rows, output_stub)
    write_address_counts(address_to_bird, output_stub)
    write_bird_counts(bird_counts, output_stub)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", default="LODC_spreadsheets")
    parser.add_argument("--output_dir", default="LODC_clean")
    args = parser.parse_args()

    write_data(Path(args.input_dir), Path(args.output_dir))
