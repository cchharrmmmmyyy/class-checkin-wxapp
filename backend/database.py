"""
数据库操作模块
负责所有数据库连接、表初始化和基本SQL操作

"""
import sqlite3
import hashlib
import secrets
from config import DATABASE_FILE, INSERT_TEST_DATA


# 检查并初始化数据库，只在需要时初始化
def check_and_init_database():
    """检查并初始化数据库，只在需要时初始化"""
    conn = _get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 检查表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if cursor.fetchone() is None:#获取查询结果的第一行，如果没有结果则返回 None
            init_database()  # 调用真正的初始化函数
        else:
            print("数据库已存在且结构完整，无需初始化")
    finally:
        conn.close()

def hash_password(password):
    """
    使用SHA-256 + 盐值对密码进行哈希加密，
    返回: 包含盐值和哈希密码的字符串，格式为 "salt:hash"，用于后续验证
    """
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return salt + ':' + password_hash

def verify_password(password, stored_hash):
    """
    验证密码是否匹配
    """
    try:
        salt, password_hash = stored_hash.split(':')
        return password_hash == hashlib.sha256((password + salt).encode()).hexdigest()
    except:
        return False

def _get_db_connection(): # 获取数据库连接
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
    conn = _get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 用户表：存储学生、班长、老师的基本信息
        # user_id 作为主键（学号/工号）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,-- 学号/工号作为主键
                username TEXT,-- 用户名（显示名称）
                password TEXT,-- 密码
                role TEXT,-- 角色
                class TEXT-- 班级
            )
        ''')
        
        # 打卡记录表：记录每天的打卡情况
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS punch_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,-- 自增主键
                user_id TEXT,-- 学号/工号
                punch_date DATE,-- 打卡日期
                leave_start_date DATE,-- 请假开始日期，默认为NULL
                leave_end_date DATE,-- 请假结束日期，默认为NULL
                leave_status TEXT DEFAULT 'pending',-- 请假状态：pending-待审批，approved-已批准，rejected-已拒绝
                FOREIGN KEY (user_id) REFERENCES users (user_id)-- 外键约束，关联用户表
            )
        ''')
        
        
        # 创建打卡位置配置表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS punch_location (
                id INTEGER PRIMARY KEY AUTOINCREMENT,-- 自增主键
                name TEXT NOT NULL,-- 打卡地点名称
                latitude REAL NOT NULL,-- 打卡地点纬度
                longitude REAL NOT NULL,-- 打卡地点经度
                radius REAL NOT NULL,-- 打卡半径
                enabled INTEGER DEFAULT 1-- 是否启用，1表示启用，0表示禁用
            )
        ''')
            
        # 创建必要的索引
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_date ON punch_records(user_id, punch_date)')
        
        if INSERT_TEST_DATA:
            # 插入示例用户数据
            sample_users = [
                ('admin001', '管理员', hash_password('admin123'), 'admin', ''),
                ('2024001', '张三', hash_password('123456'), 'student', '计算机1班'),
                ('2024002', '李四', hash_password('123456'), 'student', '计算机1班'),
                ('2024003', '王五', hash_password('123456'), 'monitor', '计算机1班'),
                ('t001', '张老师', hash_password('123456'), 'teacher', '计算机1班'),
                ('2024004', '赵六', hash_password('123456'), 'student', '计算机2班'),
                ('2024005', '钱七', hash_password('123456'), 'student', '计算机2班'),
                ('2024006', '孙八', hash_password('123456'), 'monitor', '计算机2班'),
                ('t002', '李老师', hash_password('123456'), 'teacher', '计算机2班')
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
    conn = _get_db_connection()
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
    conn = _get_db_connection()
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
    conn = _get_db_connection()
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