from db_connection import get_connection


def get_punch_records_by_user(user_id, limit=None):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        if limit:
            cursor.execute(
                "SELECT pr.*, u.username FROM punch_records pr "
                "LEFT JOIN users u ON pr.user_id = u.user_id "
                "WHERE pr.user_id = ? AND pr.punch_date IS NOT NULL "
                "ORDER BY pr.punch_date DESC LIMIT ?",
                (user_id, limit)
            )
        else:
            cursor.execute(
                "SELECT pr.*, u.username FROM punch_records pr "
                "LEFT JOIN users u ON pr.user_id = u.user_id "
                "WHERE pr.user_id = ? AND pr.punch_date IS NOT NULL "
                "ORDER BY pr.punch_date DESC",
                (user_id,)
            )
        return cursor.fetchall()
    finally:
        conn.close()


def get_punch_record_by_user_and_date(user_id, punch_date):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM punch_records WHERE user_id = ? AND punch_date = ?",
            (user_id, punch_date)
        )
        return cursor.fetchone()
    finally:
        conn.close()


def create_punch_record(user_id, punch_date):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO punch_records (user_id, punch_date) VALUES (?, ?)",
            (user_id, punch_date)
        )
        conn.commit()
        return cursor.rowcount
    finally:
        conn.close()


def delete_punch_record(record_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM punch_records WHERE id = ?", (record_id,))
        conn.commit()
        return cursor.rowcount
    finally:
        conn.close()


def update_punch_record(record_id, user_id, punch_date, leave_start_date, leave_end_date, leave_status):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE punch_records SET user_id = ?, punch_date = ?, "
            "leave_start_date = ?, leave_end_date = ?, leave_status = ? WHERE id = ?",
            (user_id, punch_date, leave_start_date, leave_end_date, leave_status, record_id)
        )
        conn.commit()
        return cursor.rowcount
    finally:
        conn.close()


def get_punch_user_ids_for_date(user_ids, date):
    if not user_ids:
        return []
    conn = get_connection()
    try:
        cursor = conn.cursor()
        placeholders = ','.join('?' * len(user_ids))
        cursor.execute(
            f"SELECT user_id FROM punch_records WHERE user_id IN ({placeholders}) AND punch_date = ?",
            user_ids + [date]
        )
        return [row['user_id'] for row in cursor.fetchall()]
    finally:
        conn.close()


def get_leave_user_ids_for_date(user_ids, date):
    if not user_ids:
        return []
    conn = get_connection()
    try:
        cursor = conn.cursor()
        placeholders = ','.join('?' * len(user_ids))
        cursor.execute(
            f"SELECT user_id FROM punch_records WHERE user_id IN ({placeholders}) "
            f"AND ? BETWEEN leave_start_date AND leave_end_date AND leave_status = 'approved'",
            user_ids + [date]
        )
        return [row['user_id'] for row in cursor.fetchall()]
    finally:
        conn.close()


def get_all_attendance_records(username=None, user_id=None, start_date=None, end_date=None, leave_status=None):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        query = "SELECT pr.*, u.username FROM punch_records pr LEFT JOIN users u ON pr.user_id = u.user_id WHERE 1=1"
        params = []

        if username:
            query += " AND u.username LIKE ?"
            params.append(f"%{username}%")
        if user_id:
            query += " AND pr.user_id LIKE ?"
            params.append(f"%{user_id}%")

        date_filter = "COALESCE(pr.punch_date, pr.leave_start_date)"
        if start_date:
            query += f" AND {date_filter} >= ?"
            params.append(start_date)
        if end_date:
            query += f" AND {date_filter} <= ?"
            params.append(end_date)
        if leave_status:
            query += " AND pr.leave_status = ?"
            params.append(leave_status)

        query += f" ORDER BY {date_filter} DESC"
        cursor.execute(query, params)
        return cursor.fetchall()
    finally:
        conn.close()


def create_attendance_record(user_id, punch_date, leave_start_date, leave_end_date, leave_status):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO punch_records (user_id, punch_date, leave_start_date, leave_end_date, leave_status) "
            "VALUES (?, ?, ?, ?, ?)",
            (user_id, punch_date, leave_start_date, leave_end_date, leave_status)
        )
        conn.commit()
        return cursor.rowcount
    finally:
        conn.close()
