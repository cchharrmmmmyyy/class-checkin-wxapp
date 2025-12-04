import sqlite3

# 数据库文件路径
DATABASE_FILE = '../user.db'

# 连接数据库
conn = sqlite3.connect(DATABASE_FILE)
cursor = conn.cursor()

try:
    # 检查punch_records表是否有leave_status字段
    cursor.execute("PRAGMA table_info(punch_records)")
    columns = cursor.fetchall()
    column_names = [column[1] for column in columns]
    
    print(f"当前表字段: {column_names}")
    
    if 'leave_status' not in column_names:
        print("添加leave_status字段")
        cursor.execute("ALTER TABLE punch_records ADD COLUMN leave_status TEXT DEFAULT 'pending'")
        print("字段添加成功")
    else:
        print("leave_status字段已存在")
        
    conn.commit()
except Exception as e:
    print(f"操作失败: {e}")
    conn.rollback()
finally:
    conn.close()