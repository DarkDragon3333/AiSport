import os

import psycopg as pg
from dotenv import load_dotenv
from ollama import chat

load_dotenv()


def run_sql(query: str) -> str:
    """
    Выполни SQL запрос к БД PostgreSQL

    Args:
        query: запрос на языке PostgreSQL
    """
    with pg.connect(os.environ["DATABASE_URL"]) as conn:
        conn.read_only = True
        with conn.cursor() as cursor:
            cursor.execute(query)
            return str(cursor.fetchall())


if __name__ == "__main__":
    prompt = "Сколько голов забил Lionel Messi в сезоне 2010/2011?"

    tables = """
        competitions (competition_id, competition_name, country_name);
        seasons (season_id, season_name);
        teams (team_id, team_name);
        players (player_id, player_name, player_nickname, country_name);
        matches (match_id, competition_id, season_id, match_date, kick_off, match_week, competition_stage, home_team_id, away_team_id, home_score,away_score, stadium_name, referee_name);
        goals (goal_id, match_id, player_id, team_id, period, minute, second, goal_type, body_part, is_own_goal); 
    """

    tables_two = """
     table competitions (
        competition_id integer primary key,
        competition_name text not null,
        country_name text not null
    );
    
     table seasons (
        season_id integer primary key,
        season_name text not null
    );
    
     table teams (
        team_id integer primary key,
        team_name text not null
    );
    
     table players (
        player_id integer primary key,
        player_name text not null,
        player_nickname text,
        country_name text
    );
    
     table matches (
        match_id integer primary key,
        competition_id integer not null references competitions,
        season_id integer not null references seasons,
        match_date date not null,
        kick_off time,
        match_week smallint,
        competition_stage text,
        home_team_id integer not null references teams,
        away_team_id integer not null references teams,
        home_score smallint not null,
        away_score smallint not null,
        stadium_name text,
        referee_name text
    );
    
     table goals (
        goal_id uuid primary key,
        match_id integer not null references matches,
        player_id integer not null references players,
        team_id integer not null references teams,
        period smallint not null,
        minute smallint not null,
        second smallint not null,
        goal_type text not null,
        body_part text,
        is_own_goal boolean not null default false
    );
    
     index on goals (player_id);
     index on goals (match_id);
     index on matches (season_id);
     index on matches (home_team_id);
     index on matches (away_team_id);
    """

    rules = {
        "role": "system",
        "content": (
            "Сразу вызывай run_sql, не описывай шаги и не задавай вопросов. "
            "Игрока ищи по players.player_nickname, сезон по seasons.season_name. "
            "Связи: goals.player_id = players.player_id; "
            "goals.match_id = matches.match_id; "
            "matches.season_id = seasons.season_id. "
            "В goals нет season_id, сезон определяй через JOIN с matches и seasons. "
            "Голы игрока считай через count(*), условие: is_own_goal = false.\n"
            f"Таблицы:\n{tables}"
        )
    }

    messages = [
        rules,
        {"role": "user", "content": prompt}
    ]

    options = {
        "temperature": 0
    }

    response = chat(model=os.environ["MODEL"], messages=messages, tools=[run_sql], options=options)
    data = response.model_dump_json()

    print(data)
    print(response.message.content)
    print(response.message.tool_calls)
