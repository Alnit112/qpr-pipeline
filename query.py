import sqlite3

con = sqlite3.connect("championship.db")
sql = """
select m.match_date,
ht.team_name AS home,
m.home_goals || '-' || m.away_goals AS score,
at.team_name AS away
FROM matches m 
JOIN teams ht ON m.home_team_id = ht.team_id
JOIN teams at ON m.away_team_id = at.team_id
WHERE (ht.team_name = 'QPR' and m.result = 'H' )
OR (at.team_name = 'QPR' and m.result = 'A');
"""
for row in con.execute(sql):
    print(row)