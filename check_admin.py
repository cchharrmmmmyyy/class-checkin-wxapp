import sqlite3

# 连接数据库
conn = sqlite3.connect('user.db')
cursor = conn.cursor()

# 查询所有用户
print("数据库中所有用户:")
cursor.execute("SELECT * FROM users")
users = cursor.fetchall()

for user in users:
    print(user)

# 关闭连接
conn.close()