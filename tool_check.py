from ollama import chat
import os
from dotenv import load_dotenv

load_dotenv()


def get_goal_count(player_name: str) -> str:
    """Возвращает количество голов игрока.

           Args:
             player_name: Имя игрока
    """

    return "138"


if __name__ == "__main__":
    rules = {"role": "system",
        "content": "для вопросов о статистике всегда вызывай инструмент, имя игрока бери из вопроса, не задавай уточняющих вопросов, если имя указано"
    }

    messages = [rules, {"role": "user", "content": "Сколько голов забил Мессии?"}]

    # pass functions directly as tools in the tools list or as a JSON schema
    response = chat(model=os.environ["MODEL"], messages=messages, tools=[get_goal_count], options={"temperature": 0})

    messages.append(response.message)
    print(messages)
    print(response)
