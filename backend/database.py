"""
数据库操作模块
负责所有数据库连接、表初始化和基本SQL操作
"""
import sqlite3

# 数据库文件路径
DATABASE_FILE = 'user.db'

def get_db_connection():
    """
    获取数据库连接
    返回: sqlite3.Connection对象
    """
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row  # 返回字典形式的结果
    return conn

def init_database():
    """
    初始化数据库表结构
    创建用户表和打卡记录表，并插入示例数据
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 用户表：存储学生、班长、老师的基本信息
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,-- 用户名作为主键
                password TEXT,-- 密码
                role TEXT,-- 角色
                class TEXT,-- 班级
                user_id TEXT UNIQUE-- 学号/工号，唯一标识
            )
        ''')
        
        # 打卡记录表：记录每天的打卡情况
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS punch_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,-- 自增主键
                username TEXT,-- 用户名
                user_id TEXT,-- 学号/工号
                punch_date DATE,-- 打卡日期
                FOREIGN KEY (username) REFERENCES users (username),-- 外键约束，关联用户表
                FOREIGN KEY (user_id) REFERENCES users (user_id)-- 外键约束，关联用户表
            )
        ''')
        
        # 创建必要的索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_date ON punch_records(username, punch_date)')
        
        # 插入示例用户数据（如果不存在）
        sample_users = [
            ('student1', '123456', 'student', '计算机1班', '202430800001'),
            ('student2', '123456', 'student', '计算机1班', '202430800002'),
            ('monitor1', '123456', 'monitor', '计算机1班', '202430800003'),
            ('teacher1', '123456', 'teacher', '计算机1班', 'T001'),
            ('student3', '123456', 'student', '计算机2班', '202430800004'),
            ('student4', '123456', 'student', '计算机2班', '202430800005'),
            ('monitor2', '123456', 'monitor', '计算机2班', '202430800006'),
            ('teacher2', '123456', 'teacher', '计算机2班', 'T002')
        ]
        
        cursor.executemany(
            "INSERT OR IGNORE INTO users VALUES (?, ?, ?, ?, ?)",
            sample_users
        )
        
        conn.commit()
        print("数据库初始化完成")
        
    except Exception as e:
        print(f"数据库初始化失败: {e}")
        conn.rollback()
    finally:
        conn.close()

def execute_query(sql, params=()):
    """
    执行SQL查询并返回所有结果
    参数:
        sql: SQL语句
        params: 参数元组
    返回: 查询结果列表
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        result = cursor.fetchall()
        conn.commit()
        return result
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def execute_query_one(sql, params=()):
    """
    执行SQL查询并返回单条结果
    参数:
        sql: SQL语句
        params: 参数元组
    返回: 单条查询结果
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        result = cursor.fetchone()
        conn.commit()
        return result
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def execute_update(sql, params=()):
    """
    执行SQL更新操作（插入、更新、删除）
    参数:
        sql: SQL语句
        params: 参数元组
    返回: 受影响的行数
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(sql, params)
        conn.commit()
        return cursor.rowcount
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

# 应用启动时自动初始化数据库
if __name__ == '__main__':
    init_database()