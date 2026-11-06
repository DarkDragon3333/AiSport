import requests
from dotenv import load_dotenv

load_dotenv()

def download_seasons():
    competitions_url = "https://raw.githubusercontent.com/statsbomb/open-data/master/data/competitions.json"

    seasons = requests.get(competitions_url).json()

    filter_seasons = [season for season in seasons if season["competition_name"] == "La Liga"]

    for season in filter_seasons:
        id_season = season["season_id"]
        name = season["competition_name"]

        print(id_season, name)

def download_matches():
    competitions_url = "https://raw.githubusercontent.com/statsbomb/open-data/master/data/matches/11/22.json"

    seasons = requests.get(competitions_url).json()

    filter_matches = [
        match for match in seasons
            if match["competition"]["competition_name"] == "La Liga"
                and match["season"]["season_name"] == "2010/2011"
                and match["competition"]["competition_id"] == 11
                and match["season"]["season_id"] == 22
    ]

    sorted_matches = sorted(filter_matches, key=lambda match: match["match_date"])

    for match in sorted_matches:
        print(
            match["match_date"], "|",
            match["match_week"], "|",
            match["home_team"]["home_team_name"],
            match["home_score"],
            match["away_score"],
            match["away_team"]["away_team_name"]
        )

def messi_shots():
    match_id = 69276
    messi_match_events_url = f"https://raw.githubusercontent.com/statsbomb/open-data/master/data/events/{match_id}.json"

    messi_match_events = requests.get(messi_match_events_url).json()

    filter_messi_events = [
        event for event in messi_match_events
            if event["type"]["name"] == "Shot" and
               event["player"]["name"] == "Lionel Andrés Messi Cuccittini" and
               event["shot"]["outcome"]["name"] == "Goal"
    ]

    for event in filter_messi_events:
        print(event["minute"])


if __name__ == "__main__":
    download_seasons()
    download_matches()
    messi_shots()