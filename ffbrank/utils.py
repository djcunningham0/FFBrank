from bs4 import BeautifulSoup as bs
import requests
from datetime import datetime
import os


def get_soup(url, headers=None, payload=None, verbose=True):
    """
    Get the HTML for a given URL using the BeautifulSoup library.

    :return: a BeautifulSoup object
    """
    result = requests.get(url, headers=headers, params=payload)
    if result.status_code != 200:
        if verbose:
            print(f'Failed to connect to {url} with error code {result.status_code}: {result.reason}')
        return None
    else:
        return bs(result.content, 'html5lib')


def get_json(url, headers=None, payload=None, verbose=True):
    """
    Get the JSON output from a URL.

    :return: dictionary from webpage's JSON
    """
    result = requests.get(url, headers=headers, params=payload)
    if result.status_code != 200:
        if verbose:
            print(f'Failed to connect to {url} with error code {result.status_code}: {result.reason}')
        return None
    else:
        return result.json()


def get_current_season():
    """
    Gets the year of the current fantasy football season. If March or later, return this calendar year. Otherwise,
    return last year.

    :return: the year of the current fantasy football season
    """
    now = datetime.now()
    if now.month > 2:
        year = now.year
    else:
        year = now.year - 1

    return year


def get_current_week():
    """
    Gets the current week of a given season for weekly rankings. Go to the FantasyPros weekly rankings and scrape
    the week number from the title.

    :return: the current week with weekly rankings
    """
    url = 'https://www.fantasypros.com/nfl/rankings/qb.php'
    soup = get_soup(url)
    week = int(soup.find('title').text.split()[1])  # title is, e.g., "Week 1 QB Rankings ..."

    return week


def experts_range():
    """
    Returns the expert IDs to check in the FantasyPros URL. Maybe try to refine this in the future.
    """
    # TODO: remove dependence on this
    return range(1000)


def write_df(df, filepath, verbose=False):
    """
    Write a dataframe to a CSV file, creating the directory path if necessary.

    :param df: pandas dataframe
    :param filepath: full file path
    """
    # add CSV file extension if it's missing
    if os.path.splitext(filepath)[-1].lower() != '.csv':
        filepath += '.csv'

    # create directories if they don't exist
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    if verbose:
        print(f'Writing {filepath}')
    df.to_csv(filepath, index=False)
