from db_connection import get_connection, hash_password
from config import Config

INSERT_TEST_DATA = Config.INSERT_TEST_DATA


def check_and_init_database():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if cursor.fetchone() is None:
            init_database()
        else:
            print("数据库已存在且结构完整，无需初始化")
    finally:
        conn.close()


def init_database():
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                username TEXT,
                password TEXT,
                role TEXT,
                class TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS punch_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                punch_date DATE,
                leave_start_date DATE,
                leave_end_date DATE,
                leave_status TEXT DEFAULT 'pending',
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS punch_location (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                radius REAL NOT NULL,
                enabled INTEGER DEFAULT 1
            )
        ''')

        cursor.execute('CREATE INDEX IF NOT EXISTS idx_user_date ON punch_records(user_id, punch_date)')

        if INSERT_TEST_DATA:
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


if __name__ == '__main__':
    init_database()
