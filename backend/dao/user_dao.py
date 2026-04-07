from db_connection import get_connection, hash_password


def get_all_users():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users ORDER BY role, class, username")
        return cursor.fetchall()
    finally:
        conn.close()


def get_user_by_id(user_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        return cursor.fetchone()
    finally:
        conn.close()


def get_users_by_class(class_name):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT username, user_id, role FROM users WHERE class = ? AND role IN ('student', 'monitor')",
            (class_name,)
        )
        return cursor.fetchall()
    finally:
        conn.close()


def get_monitors_by_class(class_name):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT username, user_id FROM users WHERE class = ? AND role = 'monitor'",
            (class_name,)
        )
        return cursor.fetchall()
    finally:
        conn.close()


def get_all_classes():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT DISTINCT class FROM users WHERE role = 'student' AND class != '' ORDER BY class"
        )
        return [row['class'] for row in cursor.fetchall()]
    finally:
        conn.close()


def create_user(username, user_id, password, role, class_name):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, user_id, password, role, class) VALUES (?, ?, ?, ?, ?)",
            (username, user_id, hash_password(password), role, class_name)
        )
        conn.commit()
        return cursor.rowcount
    finally:
        conn.close()


def update_user(username, user_id, password, role, class_name):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET username = ?, password = ?, role = ?, class = ? WHERE user_id = ?",
            (username, hash_password(password), role, class_name, user_id)
        )
        conn.commit()
        return cursor.rowcount
    finally:
        conn.close()


def delete_user(user_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        conn.commit()
        return cursor.rowcount
    finally:
        conn.close()


def update_user_role(user_id, role):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET role = ? WHERE user_id = ?", (role, user_id))
        conn.commit()
        return cursor.rowcount
    finally:
        conn.close()


def reset_password(user_id, new_password):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET password = ? WHERE user_id = ?",
            (hash_password(new_password), user_id)
        )
        conn.commit()
        return cursor.rowcount
    finally:
        conn.close()


def count_admins():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as cnt FROM users WHERE role = 'admin'")
        return cursor.fetchone()['cnt']
    finally:
        conn.close()
