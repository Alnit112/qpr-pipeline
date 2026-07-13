import sqlite3
import pandas as pd

con = sqlite3.connect("championship.db")

qpr_form = pd.read_sql_query("""
SELECT match_date,
       season,
       qpr_points,
       SUM(qpr_points) OVER (
           PARTITION BY season
           ORDER BY match_date
           ROWS BETWEEN 4 PRECEDING AND CURRENT ROW
       ) AS form_last5
FROM (
    SELECT m.match_date,
           s.label AS season,
           CASE
               WHEN ht.team_name = 'QPR' AND m.result = 'H' THEN 3
               WHEN at.team_name = 'QPR' AND m.result = 'A' THEN 3
               WHEN m.result = 'D' THEN 1
               ELSE 0
           END AS qpr_points
    FROM matches m
    JOIN teams ht ON m.home_team_id = ht.team_id
    JOIN teams at ON m.away_team_id = at.team_id
    JOIN seasons s ON m.season_id = s.season_id
    WHERE ht.team_name = 'QPR' OR at.team_name = 'QPR'
)
ORDER BY match_date
""", con)

qpr_form.to_csv("qpr_form.csv", index=False)
print(f"Exported {len(qpr_form)} rows to qpr_form.csv")