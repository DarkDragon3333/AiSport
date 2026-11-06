WITH result AS (
    SELECT season_id, match_id,
        ROW_NUMBER() OVER (PARTITION BY season_id ORDER BY match_date) AS rn
    FROM matches
)
SELECT * FROM matches;


WITH result_two AS (
    SELECT season_id, match_id,
        ROW_NUMBER() OVER (PARTITION BY season_id ORDER BY match_date) as rn
    FROM matches
)

SELECT * FROM result WHERE rn % 2 = 0;

WITH result_three AS (
    SELECT m.match_date, count(*) AS goals
    FROM goals g
    JOIN matches m ON m.match_id = g.match_id
    WHERE player_id = 5503 and season_id = 22 and is_own_goal = false
    GROUP BY m.match_date
)

SELECT match_date, goals, SUM(goals) OVER (ORDER BY match_date) AS total_goals
FROM result_three
ORDER BY match_date;