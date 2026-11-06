import os
import psycopg as pg
import requests
from dotenv import load_dotenv

load_dotenv()

SEASON_IDS = {41, 21, 22, 23}
SEASON_NAMES = {"2008/2009", "2009/2010", "2010/2011", "2011/2012"}
BASE_URL = "https://raw.githubusercontent.com/statsbomb/open-data/master/data/"


def fetch(url_to_data: str):
    return requests.get(url_to_data).json()


def load_competition_and_season(fetch_data: list, cursor):
    filter_data = [
        no_filter_data for no_filter_data in fetch_data
        if no_filter_data["competition_name"] == "La Liga"
           and no_filter_data["season_name"] in SEASON_NAMES
           and no_filter_data["competition_id"] == 11
           and no_filter_data["season_id"] in SEASON_IDS
    ]
    print(filter_data)

    for data in filter_data:
        competition_id = data["competition_id"]
        competition_name = data["competition_name"]
        country_name = data["country_name"]

        cursor.execute(
            "INSERT INTO competitions (competition_id, competition_name, country_name) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING",
            (competition_id, competition_name, country_name),
        )

        s_id = data["season_id"]
        season_name = data["season_name"]
        cursor.execute(
            "INSERT INTO seasons (season_id, season_name) VALUES (%s, %s) ON CONFLICT DO NOTHING",
            (s_id, season_name),
        )


def load_teams(match_data, cursor):
    for data in match_data:
        home_team_id = data["home_team"]["home_team_id"]
        home_team_name = data["home_team"]["home_team_name"]

        away_team_id = data["away_team"]["away_team_id"]
        away_team_name = data["away_team"]["away_team_name"]

        cursor.execute(
            "INSERT INTO teams (team_id, team_name) VALUES (%s, %s) ON CONFLICT DO NOTHING",
            (home_team_id, home_team_name),
        )

        cursor.execute(
            "INSERT INTO teams (team_id, team_name) VALUES (%s, %s) ON CONFLICT DO NOTHING",
            (away_team_id, away_team_name),
        )


def load_matches(s_id, cursor) -> list[int]:
    id_list = []
    match_url = f"https://raw.githubusercontent.com/statsbomb/open-data/master/data/matches/11/{s_id}.json"

    match_data = requests.get(match_url).json()
    load_teams(match_data, cursor)

    for match in match_data:
        match_id = match["match_id"]
        competition_id = match["competition"]["competition_id"]
        season_id = match["season"]["season_id"]
        match_date = match["match_date"]
        kick_off = match["kick_off"]
        match_week = match["match_week"]
        competition_stage = match["competition_stage"]["name"]
        home_team_id = match["home_team"]["home_team_id"]
        away_team_id = match["away_team"]["away_team_id"]
        home_score = match["home_score"]
        away_score = match["away_score"]
        stadium_name = match.get("stadium", {}).get("name")
        referee_name = match.get("referee", {}).get("name")

        cursor.execute(
            "INSERT INTO matches " +
            "(match_id, competition_id, season_id, match_date, kick_off, match_week, competition_stage, home_team_id, away_team_id, home_score, away_score, stadium_name, referee_name) " +
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING",
            (
                match_id, competition_id, season_id,
                match_date, kick_off, match_week,
                competition_stage, home_team_id, away_team_id,
                home_score, away_score, stadium_name, referee_name
            )
        )
        id_list.append(match_id)

    return id_list


def load_players(m_id, cursor):
    lineups_url = f"{BASE_URL}lineups/{m_id}.json"

    teams = fetch(lineups_url)

    for team in teams:
        for player in team["lineup"]:
            player_id = player["player_id"]
            player_name = player["player_name"]
            player_nickname = player.get("player_nickname")
            country_name = player.get("country", {}).get("name")

            cursor.execute(
                "INSERT INTO players " +
                "(player_id, player_name, player_nickname, country_name) " +
                "VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING",
                (player_id, player_name, player_nickname, country_name),
            )


def load_goals(m_id, cursor):
    goals_url = f"{BASE_URL}events/{m_id}.json"
    goals = fetch(goals_url)

    for event in goals:
        event_type = event["type"]["name"]
        if event_type == "Shot" and event["shot"]["outcome"]["name"] == "Goal":
            goal_type = event["shot"]["type"]["name"]
            body_part = event["shot"]["body_part"]["name"]
            is_own_goal = False
        elif event_type == "Own Goal Against":
            goal_type = "Own Goal"
            body_part = None
            is_own_goal = True
        else:
            continue

        goal_id = event["id"]
        player_id = event["player"]["id"]
        team_id = event["team"]["id"]
        period = event["period"]
        minute = event["minute"]
        second = event["second"]

        cursor.execute(
            "INSERT INTO goals " +
            "(goal_id, match_id, player_id, team_id, period, minute, second, goal_type, body_part, is_own_goal) " +
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING",
            (goal_id, m_id, player_id, team_id, period, minute, second, goal_type, body_part, is_own_goal),
        )


if __name__ == "__main__":
    url = F"{BASE_URL}competitions.json"
    my_list = fetch(url)
    print(my_list)

    with pg.connect(os.environ["DATABASE_URL"]) as conn:
        with conn.cursor() as cur:
            load_competition_and_season(my_list, cur)

            for season_id in SEASON_IDS:
                id_matches_list = load_matches(season_id, cur)
                print(f"Сезон {season_id}: {len(id_matches_list)} матчей")

                for i, match_id in enumerate(id_matches_list, start=1):
                    load_players(match_id, cur)
                    # print(f"Сезон {season_id}: {i}/{len(id_matches_list)} матч")
                    load_goals(match_id, cur)
