import sqlite3

with sqlite3.connect('instance\logs.db') as conn:
    cursor = conn.cursor()
    cursor.execute("UPDATE log_type SET color = 'purple' WHERE id = 7")
    conn.commit()
    