import sqlite3
from contextlib import contextmanager
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

@contextmanager
def connect():
    con = sqlite3.connect("aubus.db")
    con.execute("PRAGMA foreign_keys = ON;")
    con.row_factory = sqlite3.Row
    try:
        yield con
        con.commit()
    except:
        con.rollback()
        raise
    finally:
        con.close()

def init_db():
    with connect() as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                username TEXT UNIQUE NOT NULL,
                pwd_hash TEXT NOT NULL,
                is_driver INTEGER NOT NULL,
                area_code TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
        """)

        con.execute("""
            CREATE TABLE IF NOT EXISTS driver_schedules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                weekday INTEGER NOT NULL,
                depart_time TEXT NOT NULL,
                direction TEXT NOT NULL,
                seats_total INTEGER NOT NULL,
                seats_free INTEGER NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id)
            );
        """)

        con.execute("""
            CREATE TABLE IF NOT EXISTS ride_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                passenger_id INTEGER NOT NULL,
                area_code TEXT NOT NULL,
                weekday INTEGER NOT NULL,
                desired_time TEXT NOT NULL,
                direction TEXT NOT NULL,
                min_driver_rating REAL,
                status TEXT DEFAULT 'open',
                FOREIGN KEY(passenger_id) REFERENCES users(id)
            );
        """)

        con.execute("""
            CREATE TABLE IF NOT EXISTS ride_matches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                request_id INTEGER NOT NULL,
                driver_id INTEGER NOT NULL,
                schedule_id INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                status TEXT NOT NULL,
                FOREIGN KEY(request_id) REFERENCES ride_requests(id),
                FOREIGN KEY(driver_id) REFERENCES users(id),
                FOREIGN KEY(schedule_id) REFERENCES driver_schedules(id)
            );
        """)

        con.execute("""
            CREATE TABLE IF NOT EXISTS ratings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rater_id INTEGER NOT NULL,
                ratee_id INTEGER NOT NULL,
                ride_match_id INTEGER NOT NULL,
                score INTEGER NOT NULL,
                comment TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY(rater_id) REFERENCES users(id),
                FOREIGN KEY(ratee_id) REFERENCES users(id),
                FOREIGN KEY(ride_match_id) REFERENCES ride_matches(id)
            );
        """)

def create_user(name: str, email: str, username: str, pwd_hash: str,
                is_driver: int, area_code: str, created_at: str) -> int:
    with connect() as con:
        cur = con.execute("""
            INSERT INTO users(name,email,username,pwd_hash,is_driver,area_code,created_at)
            VALUES (?,?,?,?,?,?,?)""",
            (name, email, username, pwd_hash, is_driver, area_code, created_at))
        return cur.lastrowid

def get_user_for_login(username: str) -> Optional[Dict[str, Any]]:
    with connect() as con:
        row = con.execute("""
            SELECT id, pwd_hash, is_driver, area_code
            FROM users
            WHERE username=?""",
            (username,)).fetchone()
        if row:
            return dict(row)
        else:
            return None

def username_exists(username: str) -> bool:
    with connect() as con:
        row = con.execute("SELECT id FROM users WHERE username=?", (username,)).fetchone()
        return row is not None

def add_schedule(user_id: int, weekday: int, depart_time: str, direction: str,
                 seats_total: int, seats_free: int) -> int:
    with connect() as con:
        cur = con.execute("""
          INSERT INTO driver_schedules(user_id,weekday,depart_time,direction,seats_total,seats_free)
          VALUES (?,?,?,?,?,?)""",
          (user_id, weekday, depart_time, direction, seats_total, seats_free))
        return cur.lastrowid

def post_request(passenger_id: int, area_code: str, weekday: int, desired_time: str,
                 direction: str, min_driver_rating: float) -> int:
    with connect() as con:
        cur = con.execute("""
          INSERT INTO ride_requests(passenger_id,area_code,weekday,desired_time,direction,min_driver_rating,status)
          VALUES (?,?,?,?,?,?,'open')""",
          (passenger_id, area_code, weekday, desired_time, direction, min_driver_rating))
        return cur.lastrowid

def find_candidate_schedules(area_code: str, weekday: int, desired_time: str,
                             direction: str, min_rating: float, delta_minutes: int = 20) -> List[Dict[str, Any]]:
    dt = datetime.strptime(desired_time, "%H:%M")
    start = (dt - timedelta(minutes=delta_minutes)).strftime("%H:%M")
    end = (dt + timedelta(minutes=delta_minutes)).strftime("%H:%M")

    with connect() as con:
        rows = con.execute("""
            SELECT u.id AS driver_id, s.id AS schedule_id
            FROM users u
            JOIN driver_schedules s ON s.user_id = u.id
            WHERE u.is_driver = 1
              AND u.area_code = ?
              AND s.weekday = ?
              AND s.direction = ?
              AND s.seats_free > 0
              AND s.depart_time BETWEEN ? AND ?
              AND COALESCE((SELECT AVG(score) FROM ratings WHERE ratee_id = u.id), 0) >= ?;
        """,
        (area_code, weekday, direction, start, end, min_rating)).fetchall()
    return [dict(r) for r in rows]

def accept_request_first_come(request_id: int, driver_id: int, schedule_id: int, created_at: str) -> bool:
    with connect() as con:
        r = con.execute("SELECT status FROM ride_requests WHERE id=?", (request_id,)).fetchone()
        if not r or r["status"] != "open":
            return False

        s = con.execute("""
            SELECT seats_free FROM driver_schedules
            WHERE id=? AND user_id=?""",
            (schedule_id, driver_id)).fetchone()
        if not s or s["seats_free"] <= 0:
            return False

        con.execute("""
            INSERT INTO ride_matches(request_id, driver_id, schedule_id, created_at, status)
            VALUES (?,?,?,?, 'pending')""",
            (request_id, driver_id, schedule_id, created_at))
        con.execute("UPDATE ride_requests SET status='accepted' WHERE id=?", (request_id,))
        con.execute("UPDATE driver_schedules SET seats_free = seats_free - 1 WHERE id=?", (schedule_id,))
        return True

def add_rating(rater_id: int, ratee_id: int, match_id: int, score: int, comment: str, created_at: str) -> int:
    with connect() as con:
        cur = con.execute("""
          INSERT INTO ratings(rater_id, ratee_id, ride_match_id, score, comment, created_at)
          VALUES (?,?,?,?,?,?)""",
          (rater_id, ratee_id, match_id, score, comment, created_at))
        return cur.lastrowid

def get_avg_rating(user_id: int) -> Dict[str, Any]:
    with connect() as con:
        row = con.execute("""
          SELECT IFNULL(AVG(score),0) AS avg_rating, COUNT(*) AS n
          FROM ratings WHERE ratee_id=?""", (user_id,)).fetchone()
        return dict(row)

def current_timestamp() -> str:
    return datetime.now().isoformat(timespec="seconds")

def update_user_profile(user_id: int, is_driver: int, area_code: str) -> None:
    with connect() as con:
        con.execute(
            "UPDATE users SET is_driver = ?, area_code = ? WHERE id = ?",
            (is_driver, area_code, user_id)
        )
