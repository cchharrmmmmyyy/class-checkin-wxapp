from db_connection import get_connection


def get_punch_location():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM punch_location LIMIT 1")
        return cursor.fetchone()
    finally:
        conn.close()


def get_enabled_punch_location():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM punch_location WHERE enabled = 1 LIMIT 1")
        return cursor.fetchone()
    finally:
        conn.close()


def upsert_punch_location(name, latitude, longitude, radius, enabled=1):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM punch_location")
        existing = cursor.fetchone()

        if existing:
            cursor.execute(
                "UPDATE punch_location SET name = ?, latitude = ?, longitude = ?, radius = ?, enabled = ? WHERE id = ?",
                (name, latitude, longitude, radius, enabled, existing['id'])
            )
        else:
            cursor.execute(
                "INSERT INTO punch_location (name, latitude, longitude, radius, enabled) VALUES (?, ?, ?, ?, ?)",
                (name, latitude, longitude, radius, enabled)
            )
        conn.commit()
        return cursor.rowcount
    finally:
        conn.close()


def delete_punch_location(location_id):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM punch_location WHERE id = ?", (location_id,))
        conn.commit()
        return cursor.rowcount
    finally:
        conn.close()
