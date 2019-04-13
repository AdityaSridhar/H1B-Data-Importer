import argparse
import re

import pandas as pd
import requests

import config


def scrape(title, city, year):
    url = f"https://h1bdata.info/index.php?em=&job={title}&city={city}&year={year}"
    print(f"Search URL: {url}")
    r = requests.get(url)
    r.raise_for_status()
    df = pd.read_html(r.content)[0]
    return df


def get_raw_data(cities, year, use_cache):
    config.DATA_FOLDER_PATH.mkdir(parents=True, exist_ok=True)
    cache_exists = config.RAW_DATA_FILE_PATH.exists()

    if use_cache:
        if cache_exists:
            print(f"Using the cached raw data from {config.RAW_DATA_FILE_PATH.absolute()}")
            return pd.read_csv(config.RAW_DATA_FILE_PATH)
        else:
            print("Cache file does not exist. Proceed to download? ([y]/n)? \t")
            answer = input()
            if answer.strip().lower() == 'n':
                print("\n Exiting...")
                exit()

    # Proceed to download the data.
    year = year if year is not None else ''
    frames = []
    for area in cities:
        # Get data for all titles even if provided, and then filter later.
        # The website's pattern matching is not optimal for this study.
        frames.append(scrape('', area, year))
    data = pd.concat(frames)
    data.to_csv(config.RAW_DATA_FILE_PATH, index=False)
    return data


def filter_data(dataset: pd.DataFrame, params: argparse.Namespace):
    # Create a filter based on provided job titles.
    title_filter = dataset['JOB TITLE'].str.contains('|'.join(params.titles),
                                                     flags=re.IGNORECASE,
                                                     regex=True)

    # Create a filter for salaries based on the provided cutoff.
    salary_filter = dataset['BASE SALARY'] >= params.cutoff

    return dataset[title_filter & salary_filter]


def main(params: argparse.Namespace):
    data = get_raw_data(params.cities, params.year, params.use_cache)

    filtered_data = filter_data(data, params)

    # Sort employers alphabetically, and salaries in descending order.
    sorted_data = filtered_data.sort_values(by=['EMPLOYER', 'BASE SALARY'],
                                            ascending=[True, False])

    # Save the data.
    sorted_data.to_csv(config.FILTERED_DATA_FILE_PATH, index=False)

    print(f"The raw data is present at {config.RAW_DATA_FILE_PATH.absolute()}")
    print(f"The filtered data is present at {config.FILTERED_DATA_FILE_PATH.absolute()}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=f"Retrieve filing data from h1bdata.info "
    f"The raw data is generated at {config.RAW_DATA_FILE_PATH}. The filtered data will be available at {config.FILTERED_DATA_FILE_PATH}")
    parser.add_argument('--titles', nargs='+', default=[],
                        help="Provide a list of job titles to look for.")
    parser.add_argument('--cities', nargs='+', required=True,
                        help="Provide a list of cities (at least one)")
    parser.add_argument('--year', type=int,
                        help="Provide the year to filter for.")
    parser.add_argument('--cutoff', type=int,
                        default=0, help="Provide the minimum salary to filter on. Default value is 0.")
    parser.add_argument('--use-cache', action='store_true',
                        help="Specify this to use a locally cached file instead of downloading.")

    args = parser.parse_args()
    main(args)
