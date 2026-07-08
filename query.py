import sqlite3

con = sqlite3.connect("championship.db")
sql = """
SELECT team_name,
       SUM(played)  AS played,
       SUM(points)  AS points
FROM (

    SELECT ht.team_name,
       COUNT(*) AS played,
       SUM(CASE WHEN m.result = 'H' THEN 3
                WHEN m.result = 'D' THEN 1
                ELSE 0 END) AS points
FROM matches m
JOIN teams ht ON m.home_team_id = ht.team_id
JOIN seasons s ON m.season_id = s.season_id
WHERE s.label = '2025-26'
GROUP BY ht.team_name
    
    UNION ALL

    SELECT ht.team_name,
       COUNT(*) AS played,
       SUM(CASE WHEN m.result = 'A' THEN 3
                WHEN m.result = 'D' THEN 1
                ELSE 0 END) AS points
FROM matches m
JOIN teams ht ON m.away_team_id = ht.team_id
JOIN seasons s ON m.season_id = s.season_id
WHERE s.label = '2025-26'
GROUP BY ht.team_name
)
GROUP BY team_name
ORDER BY points DESC;
"""
for row in con.execute(sql):
    print(row)