import sqlite3

con = sqlite3.connect("championship.db")
sql = """
-- your query here
"""
for row in con.execute(sql):
    print(row)