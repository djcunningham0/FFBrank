FFBrank
=======

This is the repository for the **ffbrank** package for scraping (and aggregating... in progress)
fantasy football rankings.



**Scraping rankings:** There are two objects used for scraping rankings from experts available
on FantasyPros. The ExpertScraper object is used to find the experts that are included in the 
FantasyPros consensus rankings for any given week. The RankingScraper object is used to scrape
the rankings from those experts. There is functionality to write the expert and ranking lists
to CSV files in nested subdirectories.

**Aggregating rankings**: Not done yet. There will eventually be functionality to aggregate
rankings from individual experts using various rank aggregation methods.

Example Usage
-------------

>>> import ffbrank
>>> 
>>> # initialize scrapers
>>> exp = ffbrank.ExpertScraper()
>>> rnk = ffbrank.RankingScraper()
>>> 
>>> # write available experts to CSV
>>> exp.write_draft_experts()                    # draft experts for current season
>>> exp.write_draft_experts(year=2018)           # draft experts for specific season
>>> exp.write_weekly_experts()                   # weekly experts for current season and week
>>> exp.write_weekly_experts(year=2019, week=1)  # weekly experts for specific season and week
>>> 
>>> # write rankings for all experts to CSV
>>> rnk.write_draft_rankings()                    # draft rankings for current season
>>> rnk.write_draft_rankings(year=2018)           # draft rankings for specific season
>>> rnk.write_weekly_rankings()                   # weekly rankings for current season and week
>>> rnk.write_weekly_rankings(year=2019, week=1)  # weekly rankings for specific season and week
