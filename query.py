import sqlite3

con = sqlite3.connect("championship.db")
sql = """
SELECT match_date,
       qpr_points,
       SUM(qpr_points) OVER (
           ORDER BY match_date
           ROWS BETWEEN 4 PRECEDING AND CURRENT ROW
       ) AS form_last5
FROM (
    SELECT m.match_date,
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
WHERE (ht.team_name = 'QPR' OR at.team_name = 'QPR')
  AND s.label = '2025-26'
)
ORDER BY match_date;
"""
for row in con.execute(sql):
    print(row)