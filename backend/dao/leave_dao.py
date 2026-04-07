from db_connection import get_connection


def get_leave_records_by_user(user_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT pr.*, u.username FROM punch_records pr "
            "LEFT JOIN users u ON pr.user_id = u.user_id "
            "WHERE pr.user_id = ? AND pr.leave_start_date IS NOT NULL "
            "ORDER BY pr.leave_start_date DESC",
            (user_id,)
        )
        return cursor.fetchall()
    finally:
        conn.close()


def get_pending_leave_applications_by_class(class_name):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT pr.*, u.username FROM punch_records pr "
            "JOIN users u ON pr.user_id = u.user_id "
            "WHERE pr.leave_status = 'pending' "
            "AND pr.leave_start_date IS NOT NULL "
            "AND pr.leave_end_date IS NOT NULL "
            "AND u.class = ? "
            "ORDER BY pr.id DESC",
            (class_name,)
        )
        return cursor.fetchall()
    finally:
        conn.close()


def get_leave_record_by_id(leave_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM punch_records WHERE id = ?", (leave_id,))
        return cursor.fetchone()
    finally:
        conn.close()


def get_leave_record_by_id_and_class(leave_id, class_name):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT pr.* FROM punch_records pr "
            "JOIN users u ON pr.user_id = u.user_id "
            "WHERE pr.id = ? AND u.class = ?",
            (leave_id, class_name)
        )
        return cursor.fetchone()
    finally:
        conn.close()


def create_leave_record(user_id, leave_start_date, leave_end_date):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO punch_records (user_id, punch_date, leave_start_date, leave_end_date, leave_status) "
            "VALUES (?, NULL, ?, ?, 'pending')",
            (user_id, leave_start_date, leave_end_date)
        )
        conn.commit()
        return cursor.rowcount
    finally:
        conn.close()


def update_leave_status(leave_id, status):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE punch_records SET leave_status = ? WHERE id = ?",
            (status, leave_id)
        )
        conn.commit()
        return cursor.rowcount
    finally:
        conn.close()


def delete_leave_record(record_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM punch_records WHERE id = ? AND leave_start_date IS NOT NULL", (record_id,))
        conn.commit()
        return cursor.rowcount
    finally:
        conn.close()
