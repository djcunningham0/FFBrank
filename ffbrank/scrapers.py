import os
import pandas as pd
import ffbrank.utils as utils
from datetime import datetime

_pos_scoring_dict = {
            'QB': ['STD'],
            'RB': ['STD', 'HALF', 'PPR'],
            'WR': ['STD', 'HALF', 'PPR'],
            'TE': ['STD', 'HALF', 'PPR'],
            'FLEX': ['STD', 'HALF', 'PPR'],
            'QB-FLEX': ['STD', 'HALF', 'PPR'],
            'DST': ['STD'],
            'K': ['STD']
        }
_draft_positions = [x for x in _pos_scoring_dict.keys() if x not in ['FLEX', 'QB-FLEX']]

ranking_dir = 'rankings'
expert_dir = 'experts'
expert_master_file = 'master_expert_list.csv'
_timestamp_format = '%Y-%m-%d %H:%M:%S'


def _check_scoring(pos, scoring):
    """
    Raise an error if the specified scoring option is invalid for the specified position.

    :param pos: position (string)
    :param scoring: scoring (string)
    """
    if scoring.upper() not in ['STD', 'HALF', 'PPR']:
        raise ValueError("scoring should be one of ['STD', 'HALF', 'PPR']")
    elif pos.upper() != 'ALL':
        if scoring.upper() not in _pos_scoring_dict[pos.upper()]:
            raise ValueError(f'{scoring.upper()} is not a valid scoring option for {pos.upper}')


class ExpertScraper(object):
    """
    This object is used to scrape the available experts on FantasyPros.

    NOTE: scraping is done straight from the FantasyPros webpage, not the API. The check marks probably won't be
    accurate for prior years.
    """
    def __init__(self, base_dir=os.getcwd(), verbose=False):
        """
        :param base_dir: base directory for writing files (defaults to current directory)
        :param verbose: if True, print progress messages when writing files
        """
        self.base_dir = base_dir
        self.expert_dir = os.path.join(base_dir, expert_dir)
        self.master_file = os.path.join(self.expert_dir, expert_master_file)
        self.verbose = verbose

        self._draft_url_dict = {
            'STD': 'https://www.fantasypros.com/nfl/rankings/{pos}-cheatsheets.php',
            'HALF': 'https://www.fantasypros.com/nfl/rankings/half-point-ppr-{pos}-cheatsheets.php',
            'PPR': 'https://www.fantasypros.com/nfl/rankings/ppr-{pos}-cheatsheets.php'
        }

        self._draft_overall_url_dict = {
            'STD': 'https://www.fantasypros.com/nfl/rankings/consensus-cheatsheets.php',
            'HALF': 'https://www.fantasypros.com/nfl/rankings/half-point-ppr-cheatsheets.php',
            'PPR': 'https://www.fantasypros.com/nfl/rankings/ppr-cheatsheets.php'
        }

        self._weekly_url_dict = {
            'STD': 'https://www.fantasypros.com/nfl/rankings/{pos}.php',
            'HALF': 'https://www.fantasypros.com/nfl/rankings/half-point-ppr-{pos}.php',
            'PPR': 'https://www.fantasypros.com/nfl/rankings/ppr-{pos}.php'
        }

    def write_draft_experts(self, year=utils.get_current_season(), update_master=True):
        """
        Write the experts currently available for draft rankings to CSV files. One CSV file per expert/position/scoring
        combination. For example:
        ./experts/2019/draft/2019_expert_list_draft_OVERALL_STD.csv

        Repeatedly calls the get_draft_experts method and writes the returned dataframe to CSV.

        Maintains a "master" file containing information about every expert that has ever been scraped.

        NOTE: check marks will probably not be accurate if this method is run for a year earlier than the current year.

        :param year: the season year to return experts for (int) (defaults to current year)
        :param update_master: if True, update the master file with the results
        """
        combined_df = pd.DataFrame()
        directory = os.path.join(self.expert_dir, str(year), 'draft')

        # first do the overall rankings
        for scoring in ['STD', 'HALF', 'PPR']:
            df = self.get_draft_experts(pos='ALL', scoring=scoring, year=year)
            file = os.path.join(directory, f'{year}_expert_list_draft_OVERALL_{scoring.upper()}.csv')
            utils.write_df(df=df, filepath=file, verbose=self.verbose)

            if update_master:
                combined_df = combined_df.append(df)

        # then do positional rankings
        for pos in _draft_positions:
            for scoring in _pos_scoring_dict[pos]:
                df = self.get_draft_experts(pos=pos, scoring=scoring, year=year)
                file = os.path.join(directory, f'{year}_expert_list_draft_{pos.upper()}_{scoring.upper()}.csv')
                utils.write_df(df=df, filepath=file, verbose=self.verbose)

                if update_master:
                    combined_df = combined_df.append(df)

        if update_master:
            rank_id = f'{year}_draft'
            combined_df = (
                combined_df
                .groupby(['expert_id', 'expert_name', 'site'], as_index=False)
                .agg({'timestamp': 'min'})
            )
            self._update_master(df=combined_df, rank_id=rank_id)

    def write_weekly_experts(self, year=utils.get_current_season(), week=utils.get_current_week(), update_master=True):
        """
        Write the experts currently available for weekly rankings to CSV files. One CSV file per expert/position/scoring
        combination. For example:
        ./experts/2019/weekly/week1/2019_expert_list_week1_RB_STD.csv

        Repeatedly calls the get_weekly_experts method and writes the returned dataframe to CSV.

        Maintains a "master" file containing information about every expert that has ever been scraped.

        NOTE: check marks will probably not be accurate if this method is run for a year earlier than the current year.

        :param year: the season year to return experts for (int) (defaults to current year)
        :param week: the week number to return experts for (int) (defaults to current week number)
        :param update_master: if True, update the master file with the results
        """
        if week == 0:
            print(f"Writing draft experts because 'week' was set to 0.")
            # this won't return anything, but it will prevent the rest of this method from running
            return self.write_draft_experts(year=year, update_master=update_master)

        combined_df = pd.DataFrame()
        directory = os.path.join(self.expert_dir, str(year), 'weekly', f'week{week}')

        for pos in _pos_scoring_dict.keys():
            for scoring in _pos_scoring_dict[pos]:
                df = self.get_weekly_experts(pos=pos, scoring=scoring, year=year, week=week)
                file = os.path.join(directory, f'{year}_expert_list_week{week}_{pos.upper()}_{scoring.upper()}.csv')
                utils.write_df(df=df, filepath=file, verbose=self.verbose)

                if update_master:
                    combined_df = combined_df.append(df)

        if update_master:
            rank_id = f'{year}_week{week}'
            combined_df = (
                combined_df
                .groupby(['expert_id', 'expert_name', 'site'], as_index=False)
                .agg({'timestamp': 'min'})
            )
            self._update_master(df=combined_df, rank_id=rank_id)

    def get_draft_experts(self, pos='ALL', scoring='STD', year=utils.get_current_season()):
        """
        Scrape draft experts for one position and scoring option and return results in a Pandas dataframe. Include
        whether the expert is checked to be included in the FantasyPros consensus rankings. (NOTE: check marks will
        probably only be accurate for the current year.)

        Wrapper around _scrape_experts method with some input validation.

        :param pos: position (string)
        :param scoring: scoring option -- one of ['STD', 'HALF', 'PPR']
        :param year: year, defaults to current year (int)

        :return: Pandas dataframe with expert list
        """
        if pos == 'ALL':
            url = self._draft_overall_url_dict[scoring.upper()]
        elif pos.upper() in _draft_positions:
            _check_scoring(pos, scoring)
            url = self._draft_overall_url_dict[scoring.upper()].format(pos=pos.lower())
        else:
            raise ValueError(f"Invalid position for draft rankings -- should be in {['ALL'] + _draft_positions}")

        payload = {'year': year}
        df = self._scrape_experts(url=url, payload=payload)

        return df

    def get_weekly_experts(self, pos, scoring='STD', year=utils.get_current_season(), week=utils.get_current_week()):
        """
        Scrape weekly experts for one position and scoring option and return results in a Pandas dataframe. Include
        whether the expert is checked to be included in the FantasyPros consensus rankings. (NOTE: check marks will
        probably only be accurate for the current year.)

        Wrapper around _scrape_experts method with some input validation.

        :param pos: position (string)
        :param scoring: scoring option -- one of ['STD', 'HALF', 'PPR']
        :param year: year, defaults to current year (int)
        :param week: week, defaults to current week (int)

        :return: Pandas dataframe with expert list
        """
        if week == 0:
            print(f"Returning draft experts because 'week' was set to 0.")
            return self.get_draft_experts(pos=pos, scoring=scoring, year=year)

        _check_scoring(pos, scoring)

        payload = {'year': year, 'week': week}
        url = self._weekly_url_dict[scoring.upper()].format(pos=pos.lower())
        df = self._scrape_experts(url=url, payload=payload)

        return df

    @staticmethod
    def _scrape_experts(url, payload=None):
        """
        Perform the scraping of the experts available on FantasyPros.

        :param url: URL to scrape
        :param payload: dict with payload to append to URL

        :return: Pandas dataframe with expert list
        """
        expert_df = pd.DataFrame()
        soup = utils.get_soup(url, payload=payload)
        tr = soup.find_all('tr')

        timestamp = datetime.now().strftime(_timestamp_format)
        for row in tr:
            if row.find('input', class_='expert') is None:
                continue

            expert_info = row.find_all('a')
            expert_name = expert_info[0].text
            expert_site = expert_info[1].text

            attrs = row.find('input').attrs
            expert_id = attrs['value']
            if 'checked' in attrs and attrs['checked'] == 'checked':
                checked = True
            else:
                checked = False

            updated_date = row.find_all('td')[-1].text

            expert_df = expert_df.append(
                pd.DataFrame({
                    'expert_id': [expert_id],
                    'expert_name': [expert_name],
                    'site': [expert_site],
                    'checked': [checked],
                    'updated_date': [updated_date],
                    'timestamp': [timestamp]
                })
            )

        return expert_df

    def _update_master(self, df, rank_id):
        """
        Update the master file with a list of available experts. Keep track of expert ID/name/site mappings and
        record the first and latest appearance of each expert.

        NOTE: the name of the master file is specified at the top of this script.

        :param df: dataframe of experts
        :param rank_id: string to identify when this expert produced a ranking (e.g., '2019_draft')
        """
        try:
            existing_df = pd.read_csv(self.master_file, dtype=str)
        except FileNotFoundError:
            if self.verbose:
                print(f'File not found. Creating {self.master_file}')
            existing_df = pd.DataFrame({
                'expert_id': [],
                'expert_name': [],
                'site': [],
                'first_timestamp': [],
                'latest_timestamp': [],
                'first_appearance': [],
                'latest_appearance': []
            }, dtype=str)

        for i, row in df.iterrows():
            conds = (existing_df['expert_id'] == row['expert_id']) & \
                    (existing_df['expert_name'] == row['expert_name']) & \
                    (existing_df['site'] == row['site'])
            existing_row = existing_df.loc[conds]

            # if there's no row with this expert, ID, site combo, add a new row
            if existing_row.shape[0] == 0:
                existing_df = existing_df.append(
                    pd.DataFrame({
                        'expert_id': [row['expert_id']],
                        'expert_name': [row['expert_name']],
                        'site': [row['site']],
                        'first_timestamp': [row['timestamp']],
                        'latest_timestamp': [row['timestamp']],
                        'first_appearance': [rank_id],
                        'latest_appearance': [rank_id]
                    })
                )
            # otherwise update the existing row
            else:
                existing_df.loc[conds & (existing_df['first_timestamp'] > row['timestamp']),
                                'first_timestamp'] = row['timestamp']
                existing_df.loc[conds & (existing_df['latest_timestamp'] < row['timestamp']),
                                'latest_timestamp'] = row['timestamp']
                existing_df.loc[conds & (existing_df['first_appearance'] > rank_id),
                                'first_appearance'] = rank_id
                existing_df.loc[conds & (existing_df['latest_appearance'] < rank_id),
                                'latest_appearance'] = rank_id

        # drop duplicates before writing in case we get duplicate rows (shouldn't happen)
        existing_df['expert_id'] = existing_df['expert_id'].astype(int)
        existing_df = existing_df.drop_duplicates().sort_values('expert_id')
        utils.write_df(df=existing_df, filepath=self.master_file, verbose=self.verbose)


class RankingScraper(object):
    """
    This object is used to scrape draft and weekly rankings from individual experts through the FantasyPros API.
    """
    def __init__(self, base_dir=os.getcwd(), verbose=False):
        """
        :param base_dir: base directory for writing files (defaults to current directory)
        :param verbose: if True, print progress messages when writing files
        """
        self.verbose = verbose
        self.base_dir = base_dir
        self.ranking_dir = os.path.join(base_dir, 'rankings')
        self.url = 'https://partners.fantasypros.com/api/v1/consensus-rankings.php'

        # read dataframe with all experts that have ever been scraped
        self.expert_master_file = os.path.join(self.base_dir, expert_dir, expert_master_file)
        self.expert_df = self._get_all_experts()

        self.pos_map = {
            'QB': 'QB',
            'RB': 'RB',
            'WR': 'WR',
            'TE': 'TE',
            'FLEX': 'FLX',
            'QB-FLEX': 'OP',
            'DST': 'DST',
            'K': 'K',
            'ALL': 'ALL'
        }

    def write_draft_rankings(self, year=utils.get_current_season(), start_exp=0):
        """
        Write the draft rankings for all available FantasyPros experts to CSV files. Available experts are read from
        the expert master file. One CSV file per expert/position/scoring combination. For example:
        ./rankings/2019/draft/2019_draft_9_Scott Pianowski_Yahoo! Sports_OVERALL_STD.csv

        Repeatedly calls the get_draft_rankings method and writes the returned dataframe to CSV.

        :param year: the season year to return rankings for (int) (defaults to current year)
        :param start_exp: the expert ID number to start with (defaults to 0 to scrape all experts)
        """
        expert_df = self._get_all_experts()

        for i, row in expert_df.iterrows():
            expert_id = row['expert_id']
            expert_name = row['expert_name']
            site = row['site']
            if expert_id < start_exp:
                continue

            # first get overall rankings
            for scoring in ['STD', 'HALF', 'PPR']:
                rank_df = self.get_draft_rankings(expert_id=expert_id, scoring=scoring, pos='ALL', year=year)

                # write to CSV if results were found
                if rank_df.shape[0] > 0:
                    filename = f'{year}_draft_{expert_id}_{expert_name}_{site}_OVERALL_{scoring}.csv'
                    path = os.path.join(self.ranking_dir, str(year), 'draft', filename)
                    utils.write_df(rank_df, path, verbose=self.verbose)

            # then get positional rankings
            for pos in _draft_positions:
                for scoring in _pos_scoring_dict[pos]:
                    rank_df = self.get_draft_rankings(expert_id=expert_id, scoring=scoring, pos=pos, year=year)

                    # write to CSV if results were found
                    if rank_df.shape[0] > 0:
                        filename = f'{year}_draft_{expert_id}_{expert_name}_{site}_{pos.upper()}_{scoring}.csv'
                        path = os.path.join(self.ranking_dir, str(year), 'draft', filename)
                        utils.write_df(rank_df, path, verbose=self.verbose)

    def write_weekly_rankings(self, year=utils.get_current_season(), week=utils.get_current_week(), start_exp=0):
        """
        Write the draft rankings for all available FantasyPros experts to CSV files. Available experts are read from
        the expert master file. One CSV file per expert/position/scoring combination. For example:
        ./rankings/2019/weekly/2019_week1_9_Scott Pianowski_Yahoo! Sports_RB_STD.csv

        Repeatedly calls the get_weekly_rankings method and writes the returned dataframe to CSV.

        :param year: the season year to return rankings for (int) (defaults to current year)
        :param week: the week number to return rankings for (int) (defaults to current week number)
        :param start_exp: the expert ID number to start with (defaults to 0 to scrape all experts)
        """
        if week == 0:
            print(f"Writing draft rankings because 'week' was set to 0.")
            # this won't return anything, but returning the value will prevent the rest of this method from running
            return self.write_draft_rankings(year=year, start_exp=start_exp)

        expert_df = self._get_all_experts()

        for i, row in expert_df.iterrows():
            expert_id = row['expert_id']
            expert_name = row['expert_name']
            site = row['site']
            if expert_id < start_exp:
                continue

            for pos in _pos_scoring_dict.keys():
                for scoring in _pos_scoring_dict[pos]:
                    rank_df = self.get_weekly_rankings(expert_id=expert_id, scoring=scoring, pos=pos, year=year,
                                                       week=week)

                    # write to CSV if results were found
                    if rank_df.shape[0] > 0:
                        filename = f'{year}_week{week}_{expert_id}_{expert_name}_{site}_{pos}_{scoring}.csv'
                        path = os.path.join(self.ranking_dir, str(year), 'weekly', f'week{week}', filename)
                        utils.write_df(rank_df, path, verbose=self.verbose)

    def get_draft_rankings(self, expert_id, scoring, pos='ALL', year=utils.get_current_season()):
        """
        Simple wrapper around _scrape_rankings to get draft rankings for a single expert and the specified parameters.
        Performs some basic input validation.

        :param expert_id: expert ID (integer)
        :param scoring: 'STD', 'HALF', or 'PPR'
        :param pos: 'ALL' for overall, or one of 'QB', 'RB', 'WR', 'TE', 'FLEX', 'QB-FLEX', 'DST', 'K'
        :param year: year (integer); defaults to current year

        :return: dataframe with rankings for one expert
        """
        _check_scoring(pos, scoring)
        return self._scrape_rankings(expert_id=expert_id, scoring=scoring, pos=pos, year=year, week=0)

    def get_weekly_rankings(self, expert_id, scoring, pos, year=utils.get_current_season(),
                            week=utils.get_current_week()):
        """
        Simple wrapper around _scrape_rankings to get weekly rankings for a single expert and the specified parameters.
        Performs some basic input validation.

        :param expert_id: expert ID (integer)
        :param scoring: 'STD', 'HALF', or 'PPR'
        :param pos: 'ALL' for overall, or one of 'QB', 'RB', 'WR', 'TE', 'FLEX', 'QB-FLEX', 'DST', 'K'
        :param year: year (integer); defaults to current year
        :param week: week number (integer); defaults to current week

        :return: dataframe with rankings for one expert
        """
        if week == 0:
            print(f"Returning draft rankings because 'week' was set to 0.")
            return self.get_draft_rankings(expert_id=expert_id, scoring=scoring, pos=pos, year=year)

        if pos.upper() == 'ALL':
            raise ValueError("'ALL' is not valid for weekly rankings. Overall rankings only available for draft.")

        _check_scoring(pos, scoring)

        return self._scrape_rankings(expert_id=expert_id, scoring=scoring, pos=pos, year=year, week=week)

    def _scrape_rankings(self, expert_id, scoring, pos, year, week):
        """
        Scrape rankings from a single expert using FantasyPros API.

        :param expert_id: expert ID (integer)
        :param scoring: 'STD', 'HALF', or 'PPR'
        :param pos: 'ALL' for overall, or one of 'QB', 'RB', 'WR', 'TE', 'FLEX', 'QB-FLEX', 'DST', 'K'
        :param year: year (integer); defaults to current year
        :param week: week number (integer); defaults to current week

        :return: dataframe with rankings for one expert
        """
        payload = {
            'sport': 'NFL',
            'year': year,
            'week': week,
            'id': 1054,    # not quite sure what this is, but it's in the link from Yahoo rankings
            'position': self.pos_map[pos.upper()],
            'type': 'ST',  # not quite sure what this is, but it's in the link from Yahoo rankings
            'scoring': scoring.upper(),
            'filters': expert_id,
            'export': 'json'
        }

        rank_dict = utils.get_json(self.url, payload=payload)
        players = rank_dict['players']

        fields = ['player_id', 'player_name', 'player_team_id', 'player_position_id']
        ranks = [[expert_id] + [player[f] for f in fields] for player in players if 'player_name' in player]

        rank_df = pd.DataFrame(ranks, columns=['expert_id', 'player_id', 'player_name', 'team', 'pos'])
        if rank_df.shape[0] > 0:
            rank_df['rank'] = rank_df.index + 1
            rank_df['pos_rank'] = rank_df['pos'].str.upper() + \
                                  rank_df.groupby('pos')['rank'].rank().astype(int).astype(str)

        timestamp = datetime.now().strftime(_timestamp_format)
        rank_df['timestamp'] = timestamp

        return rank_df

    def _get_all_experts(self):
        """
        Return the dataframe of all experts that have ever been scraped from the FantasyPros expert list. If there are
        multiple entries a given expert ID, select the one scraped most recently (should never happen).

        :return: dataframe containing expert ID, expert name, and site
        """
        try:
            expert_df = pd.read_csv(self.expert_master_file)
        except FileNotFoundError:
            raise FileNotFoundError(f'Master expert list does not exist at {self.expert_master_file}.')

        # make sure we have one row per expert_id -- take the most recent timestamp
        expert_df['latest_timestamp'] = pd.to_datetime(expert_df['latest_timestamp'], format=_timestamp_format)
        expert_df['r'] = expert_df.groupby('expert_id')['latest_timestamp'].rank(ascending=False, method='first')

        return expert_df.loc[expert_df['r'] == 1, ['expert_id', 'expert_name', 'site']]
