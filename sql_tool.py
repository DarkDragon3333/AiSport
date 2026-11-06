import os

import psycopg as pg
from dotenv import load_dotenv
from ollama import chat

load_dotenv()

QUESTIONS = [
    ("Сколько голов забил Lionel Messi в сезоне 2010/2011?", "31"),
    ("Сколько всего голов забил Lionel Messi?", "138"),
    ("Сколько домашних матчей сыграла Barcelona в сезоне 2009/2010?", "16"),
]

tables = """
        competitions (competition_id, competition_name, country_name);
        seasons (season_id, season_name);
        teams (team_id, team_name);
        players (player_id, player_name, player_nickname, country_name);
        matches (match_id, competition_id, season_id, match_date, kick_off, match_week, competition_stage, home_team_id, away_team_id, home_score,away_score, stadium_name, referee_name);
        goals (goal_id, match_id, player_id, team_id, period, minute, second, goal_type, body_part, is_own_goal); 
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

options = {
    "temperature": 0
}


def run_sql(query: str) -> str:
    """
    Выполни SQL запрос к БД PostgreSQL

    Args:
        query: запрос на языке PostgreSQL
    """
    try:
        with pg.connect(os.environ["DATABASE_URL"]) as conn:
            conn.read_only = True
            with conn.cursor() as cursor:
                cursor.execute(query)
                return str(cursor.fetchall())
    except pg.Error as e:
        print(e)


if __name__ == "__main__":
    model = os.environ["MODEL"]
    print("Model: ", model)

    for q, expected in QUESTIONS:
        print("Question: ", q)
        messages = [
            rules,
            {"role": "user", "content": q}
        ]

        response = chat(model=model, messages=messages, tools=[run_sql], think=False, options=options)
        sql = response.message.tool_calls[0].function.arguments["query"]
        result = run_sql(sql)
        print("SQL:", sql)
        print("Результат:", result)

        messages.append(response.message)
        messages.append({"role": "tool", "tool_name": "run_sql", "content": result})

        response_two = chat(model=model, messages=messages, think=False, options=options)
        print("Ответ:", response_two.message.content)
