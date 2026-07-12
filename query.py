import sqlite3

con = sqlite3.connect("championship.db")
sql = """
SELECT s.label,
       COUNT(*) AS played,
       SUM(m.home_goals + m.away_goals) AS total_goals,
       ROUND(AVG(m.home_goals + m.away_goals), 2) AS avg_goals
FROM matches m
JOIN teams ht ON m.home_team_id = ht.team_id
JOIN seasons s ON m.season_id = s.season_id
GROUP BY s.label
ORDER BY s.label DESC;
"""
for row in con.execute(sql):
    print(row)