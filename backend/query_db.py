import sqlite3
conn = sqlite3.connect('user.db')
cursor = conn.cursor()

print('=== 请假记录详情 ===')
cursor.execute('SELECT * FROM leaves')
for row in cursor.fetchall():
    print(row)

print()
print('=== 列名 ===')
cursor.execute('PRAGMA table_info(leaves)')
for row in cursor.fetchall():
    print(row)

conn.close()
