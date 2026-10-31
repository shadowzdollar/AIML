#data base connection

import sqlite3

query = """CREATE TABLE test(a VARCHAR(20), b VARCHAR(30), c REAL, d INTEGER)"""

con = sqlite3.connect("mydatabase.sqlite")

con.execute(query)
con.commit()

data = [("Atlanta", "Georgia", 1.25, 6),

("Tallahassee", "Florida", 2.6, 3),

("Sacramento", "California", 1.7, 5)]


stmt = "INSERT INTO test VALUES(?, ?, ?, ?)"


con.commit()

cursor = con.execute("SELECT * FROM test")

rows = cursor.fetchall()

print(rows)

