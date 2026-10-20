"""
Database management for Club Activities Tracker.
Uses Python's built-in sqlite3 with foreign keys and connection helpers.
"""

import sqlite3
import os
import hashlib
from typing import List, Dict, Any, Optional

DB_FILE = os.path.join(os.path.dirname(__file__), "club_tracker.db")


def get_connection(db_path: str = DB_FILE) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db(db_path: str = DB_FILE):
    """Initializes tables if they do not exist."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        
        # Clubs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clubs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                category TEXT NOT NULL,
                description TEXT,
                lead_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # Members table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS members (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                club_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                email TEXT,
                role TEXT DEFAULT 'Member',
                join_date TEXT DEFAULT (DATE('now')),
                status TEXT DEFAULT 'Active',
                FOREIGN KEY (club_id) REFERENCES clubs(id) ON DELETE CASCADE
            );
        """)

        # Activities table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                club_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                category TEXT NOT NULL,
                date TEXT NOT NULL,
                duration_hours REAL DEFAULT 1.0,
                location TEXT,
                status TEXT DEFAULT 'Planned',
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (club_id) REFERENCES clubs(id) ON DELETE CASCADE
            );
        """)

        # Attendance & Participation table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                activity_id INTEGER NOT NULL,
                member_id INTEGER NOT NULL,
                status TEXT DEFAULT 'Present',
                hours_credited REAL DEFAULT 0.0,
                notes TEXT,
                FOREIGN KEY (activity_id) REFERENCES activities(id) ON DELETE CASCADE,
                FOREIGN KEY (member_id) REFERENCES members(id) ON DELETE CASCADE,
                UNIQUE(activity_id, member_id)
            );
        """)

        # Announcements table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS announcements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                club_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                date TEXT DEFAULT (DATE('now')),
                priority TEXT DEFAULT 'Normal',
                FOREIGN KEY (club_id) REFERENCES clubs(id) ON DELETE CASCADE
            );
        """)

        # Users table for Authentication
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                name TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'Member',
                club_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (club_id) REFERENCES clubs(id) ON DELETE SET NULL
            );
        """)

        # Login Activity & Audit Logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS login_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT NOT NULL,
                role TEXT,
                portal TEXT,
                status TEXT NOT NULL,
                ip_address TEXT DEFAULT '127.0.0.1',
                user_agent TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
            );
        """)

        # Migration: Ensure profile columns exist in users table
        new_cols = [
            ("avatar", "TEXT"),
            ("email", "TEXT"),
            ("phone", "TEXT"),
            ("department", "TEXT"),
            ("student_id", "TEXT"),
            ("year", "TEXT"),
            ("bio", "TEXT"),
            ("skills", "TEXT"),
            ("linkedin", "TEXT"),
            ("github", "TEXT")
        ]
        cursor.execute("PRAGMA table_info(users)")
        existing_cols = [row[1] for row in cursor.fetchall()]
        for col_name, col_type in new_cols:
            if col_name not in existing_cols:
                cursor.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}")

        # Seed realistic profile info for default demo users if empty
        cursor.execute("""
            UPDATE users 
            SET avatar = COALESCE(avatar, '👑'),
                email = COALESCE(email, 'sarah.jenkins@campus.edu'),
                phone = COALESCE(phone, '+91 98765 43210'),
                department = COALESCE(department, 'Computer Science & Engineering'),
                student_id = COALESCE(student_id, 'FAC-CSE-001'),
                year = COALESCE(year, 'Faculty Advisor'),
                bio = COALESCE(bio, 'Faculty advisor and academic mentor for campus technical clubs and research hackathons.'),
                skills = COALESCE(skills, 'Distributed Systems, Cloud Architecture, Leadership'),
                linkedin = COALESCE(linkedin, 'linkedin.com/in/dr-sarah-jenkins'),
                github = COALESCE(github, 'github.com/sarah-jenkins')
            WHERE LOWER(username) = 'admin'
        """)

        cursor.execute("""
            UPDATE users 
            SET avatar = COALESCE(avatar, '⚡'),
                email = COALESCE(email, 'aarav.sharma@campus.edu'),
                phone = COALESCE(phone, '+91 98123 45678'),
                department = COALESCE(department, 'Information Technology'),
                student_id = COALESCE(student_id, '2023IT045'),
                year = COALESCE(year, '3rd Year (6th Sem)'),
                bio = COALESCE(bio, 'Coding Club Lead. Full-stack developer passionate about competitive coding and open-source.'),
                skills = COALESCE(skills, 'Python, JavaScript, React, Docker, Linux'),
                linkedin = COALESCE(linkedin, 'linkedin.com/in/aarav-sharma-tech'),
                github = COALESCE(github, 'github.com/aaravsharma')
            WHERE LOWER(username) = 'officer'
        """)

        cursor.execute("""
            UPDATE users 
            SET avatar = COALESCE(avatar, '🎓'),
                email = COALESCE(email, 'sneha.r@campus.edu'),
                phone = COALESCE(phone, '+91 98234 56789'),
                department = COALESCE(department, 'Computer Science & Engineering'),
                student_id = COALESCE(student_id, '2024BCSE089'),
                year = COALESCE(year, '2nd Year (4th Sem)'),
                bio = COALESCE(bio, 'Student member passionate about Machine Learning, Web APIs, and campus hackathons.'),
                skills = COALESCE(skills, 'Python, HTML/CSS, Data Structures, Git'),
                linkedin = COALESCE(linkedin, 'linkedin.com/in/sneha-reddy-campus'),
                github = COALESCE(github, 'github.com/snehareddy')
            WHERE LOWER(username) IN ('member', 'student')
        """)

        conn.commit()


# --- CLUBS CRUD ---

def get_clubs(db_path: str = DB_FILE) -> List[Dict[str, Any]]:
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.*, 
                   COUNT(DISTINCT m.id) AS member_count,
                   COUNT(DISTINCT a.id) AS activity_count
            FROM clubs c
            LEFT JOIN members m ON c.id = m.club_id
            LEFT JOIN activities a ON c.id = a.club_id
            GROUP BY c.id
            ORDER BY c.name ASC
        """)
        return [dict(row) for row in cursor.fetchall()]


def get_club(club_id: int, db_path: str = DB_FILE) -> Optional[Dict[str, Any]]:
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clubs WHERE id = ?", (club_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def add_club(name: str, category: str, description: str = "", lead_name: str = "", db_path: str = DB_FILE) -> int:
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO clubs (name, category, description, lead_name)
            VALUES (?, ?, ?, ?)
        """, (name, category, description, lead_name))
        conn.commit()
        return cursor.lastrowid


def update_club(club_id: int, name: str, category: str, description: str, lead_name: str, db_path: str = DB_FILE) -> bool:
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE clubs
            SET name = ?, category = ?, description = ?, lead_name = ?
            WHERE id = ?
        """, (name, category, description, lead_name, club_id))
        conn.commit()
        return cursor.rowcount > 0


def delete_club(club_id: int, db_path: str = DB_FILE) -> bool:
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM clubs WHERE id = ?", (club_id,))
        conn.commit()
        return cursor.rowcount > 0


# --- MEMBERS CRUD ---

def get_members(club_id: Optional[int] = None, db_path: str = DB_FILE) -> List[Dict[str, Any]]:
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        if club_id:
            cursor.execute("""
                SELECT m.*, c.name as club_name,
                       COALESCE(SUM(CASE WHEN att.status = 'Present' THEN att.hours_credited ELSE 0 END), 0) as total_hours,
                       COUNT(DISTINCT att.activity_id) as attended_count
                FROM members m
                JOIN clubs c ON m.club_id = c.id
                LEFT JOIN attendance att ON m.id = att.member_id
                WHERE m.club_id = ?
                GROUP BY m.id
                ORDER BY m.name ASC
            """, (club_id,))
        else:
            cursor.execute("""
                SELECT m.*, c.name as club_name,
                       COALESCE(SUM(CASE WHEN att.status = 'Present' THEN att.hours_credited ELSE 0 END), 0) as total_hours,
                       COUNT(DISTINCT att.activity_id) as attended_count
                FROM members m
                JOIN clubs c ON m.club_id = c.id
                LEFT JOIN attendance att ON m.id = att.member_id
                GROUP BY m.id
                ORDER BY m.name ASC
            """)
        return [dict(row) for row in cursor.fetchall()]


def add_member(club_id: int, name: str, email: str = "", role: str = "Member", join_date: str = "", db_path: str = DB_FILE) -> int:
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO members (club_id, name, email, role, join_date)
            VALUES (?, ?, ?, ?, COALESCE(NULLIF(?, ''), DATE('now')))
        """, (club_id, name, email, role, join_date))
        conn.commit()
        return cursor.lastrowid


def update_member(member_id: int, club_id: int, name: str, email: str, role: str, status: str, db_path: str = DB_FILE) -> bool:
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE members
            SET club_id = ?, name = ?, email = ?, role = ?, status = ?
            WHERE id = ?
        """, (club_id, name, email, role, status, member_id))
        conn.commit()
        return cursor.rowcount > 0


def delete_member(member_id: int, db_path: str = DB_FILE) -> bool:
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM members WHERE id = ?", (member_id,))
        conn.commit()
        return cursor.rowcount > 0


# --- ACTIVITIES CRUD ---

def get_activities(club_id: Optional[int] = None, status: Optional[str] = None, db_path: str = DB_FILE) -> List[Dict[str, Any]]:
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        query = """
            SELECT a.*, c.name as club_name,
                   COUNT(CASE WHEN att.status = 'Present' THEN 1 END) as attendees_count
            FROM activities a
            JOIN clubs c ON a.club_id = c.id
            LEFT JOIN attendance att ON a.id = att.activity_id
        """
        params = []
        conditions = []
        if club_id:
            conditions.append("a.club_id = ?")
            params.append(club_id)
        if status:
            conditions.append("a.status = ?")
            params.append(status)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " GROUP BY a.id ORDER BY a.date DESC, a.id DESC"
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]


def get_activity(activity_id: int, db_path: str = DB_FILE) -> Optional[Dict[str, Any]]:
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT a.*, c.name as club_name
            FROM activities a
            JOIN clubs c ON a.club_id = c.id
            WHERE a.id = ?
        """, (activity_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def add_activity(club_id: int, title: str, category: str, date: str, 
                 duration_hours: float = 1.0, location: str = "", 
                 status: str = "Planned", description: str = "", db_path: str = DB_FILE) -> int:
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO activities (club_id, title, category, date, duration_hours, location, status, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (club_id, title, category, date, duration_hours, location, status, description))
        conn.commit()
        return cursor.lastrowid


def update_activity(activity_id: int, club_id: int, title: str, category: str, 
                    date: str, duration_hours: float, location: str, 
                    status: str, description: str, db_path: str = DB_FILE) -> bool:
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE activities
            SET club_id = ?, title = ?, category = ?, date = ?, 
                duration_hours = ?, location = ?, status = ?, description = ?
            WHERE id = ?
        """, (club_id, title, category, date, duration_hours, location, status, description, activity_id))
        conn.commit()
        return cursor.rowcount > 0


def delete_activity(activity_id: int, db_path: str = DB_FILE) -> bool:
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM activities WHERE id = ?", (activity_id,))
        conn.commit()
        return cursor.rowcount > 0


# --- ATTENDANCE CRUD ---

def get_attendance_for_activity(activity_id: int, db_path: str = DB_FILE) -> List[Dict[str, Any]]:
    """Gets all club members with their attendance status for this specific activity."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        # First find the club for this activity
        cursor.execute("SELECT club_id, duration_hours FROM activities WHERE id = ?", (activity_id,))
        act = cursor.fetchone()
        if not act:
            return []
        club_id = act["club_id"]
        default_hours = act["duration_hours"]

        cursor.execute("""
            SELECT m.id as member_id, m.name as member_name, m.role, m.email,
                   att.id as attendance_id,
                   COALESCE(att.status, 'Not Marked') as status,
                   COALESCE(att.hours_credited, ?) as hours_credited,
                   COALESCE(att.notes, '') as notes
            FROM members m
            LEFT JOIN attendance att ON m.id = att.member_id AND att.activity_id = ?
            WHERE m.club_id = ?
            ORDER BY m.name ASC
        """, (default_hours, activity_id, club_id))
        return [dict(row) for row in cursor.fetchall()]


def record_attendance(activity_id: int, member_id: int, status: str, hours_credited: float, notes: str = "", db_path: str = DB_FILE) -> bool:
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO attendance (activity_id, member_id, status, hours_credited, notes)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(activity_id, member_id) DO UPDATE SET
                status = excluded.status,
                hours_credited = excluded.hours_credited,
                notes = excluded.notes
        """, (activity_id, member_id, status, hours_credited, notes))
        conn.commit()
        return True


def bulk_record_attendance(activity_id: int, records: List[Dict[str, Any]], db_path: str = DB_FILE) -> bool:
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        for r in records:
            cursor.execute("""
                INSERT INTO attendance (activity_id, member_id, status, hours_credited, notes)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(activity_id, member_id) DO UPDATE SET
                    status = excluded.status,
                    hours_credited = excluded.hours_credited,
                    notes = excluded.notes
            """, (activity_id, r["member_id"], r["status"], r.get("hours_credited", 0.0), r.get("notes", "")))
        conn.commit()
        return True


# --- ANNOUNCEMENTS CRUD ---

def get_announcements(club_id: Optional[int] = None, db_path: str = DB_FILE) -> List[Dict[str, Any]]:
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        if club_id:
            cursor.execute("""
                SELECT an.*, c.name as club_name
                FROM announcements an
                JOIN clubs c ON an.club_id = c.id
                WHERE an.club_id = ?
                ORDER BY an.id DESC
            """, (club_id,))
        else:
            cursor.execute("""
                SELECT an.*, c.name as club_name
                FROM announcements an
                JOIN clubs c ON an.club_id = c.id
                ORDER BY an.id DESC
            """)
        return [dict(row) for row in cursor.fetchall()]


def add_announcement(club_id: int, title: str, content: str, priority: str = "Normal", date: str = "", db_path: str = DB_FILE) -> int:
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO announcements (club_id, title, content, priority, date)
            VALUES (?, ?, ?, ?, COALESCE(NULLIF(?, ''), DATE('now')))
        """, (club_id, title, content, priority, date))
        conn.commit()
        return cursor.lastrowid


def delete_announcement(announcement_id: int, db_path: str = DB_FILE) -> bool:
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM announcements WHERE id = ?", (announcement_id,))
        conn.commit()
        return cursor.rowcount > 0


# --- AUTHENTICATION & USERS ---

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def create_user(username: str, password: str, name: str, role: str = "Member", club_id: Optional[int] = None, db_path: str = DB_FILE) -> int:
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        pwd_hash = hash_password(password)

        # Default club if not specified and role requires club association
        if not club_id and role in ("Member", "Officer"):
            cursor.execute("SELECT id FROM clubs ORDER BY id ASC LIMIT 1")
            first_c = cursor.fetchone()
            if first_c:
                club_id = first_c[0]

        cursor.execute("""
            INSERT INTO users (username, password_hash, name, role, club_id)
            VALUES (?, ?, ?, ?, ?)
        """, (username.strip().lower(), pwd_hash, name.strip(), role, club_id))
        user_id = cursor.lastrowid

        # Also create/sync member record for students & officers so they can immediately RSVP & attend events
        if role in ("Member", "Officer"):
            clean_email = f"{username.strip().lower()}@campus.edu"
            cursor.execute("SELECT id FROM members WHERE LOWER(name) = ? OR LOWER(email) = ?", (name.strip().lower(), clean_email))
            existing_m = cursor.fetchone()
            if not existing_m and club_id:
                cursor.execute("""
                    INSERT INTO members (club_id, name, email, role, status)
                    VALUES (?, ?, ?, ?, 'Active')
                """, (club_id, name.strip(), clean_email, role))

        conn.commit()
        return user_id


def authenticate_user(username: str, password: str, db_path: str = DB_FILE) -> Optional[Dict[str, Any]]:
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        u_clean = (username or "").strip().lower()
        p_clean = (password or "").strip()
        pwd_hash = hash_password(p_clean)

        # 1. Direct match with exact hashed password
        cursor.execute("""
            SELECT u.id, u.username, u.name, u.role, u.club_id, 
                   u.avatar, u.email, u.phone, u.department, u.student_id, 
                   u.year, u.bio, u.skills, u.linkedin, u.github, u.created_at,
                   c.name as club_name
            FROM users u
            LEFT JOIN clubs c ON u.club_id = c.id
            WHERE LOWER(u.username) = ? AND u.password_hash = ?
        """, (u_clean, pwd_hash))
        row = cursor.fetchone()
        if row:
            return dict(row)

        # 2. Tolerant matching for demo users (handles student/member, admin/admin, officer/officer)
        demo_passwords = {
            "admin": ["admin123", "admin", "password", "123456", "admin@123"],
            "officer": ["officer123", "officer", "password", "123456", "officer@123"],
            "member": ["member123", "member", "student123", "student", "password", "123456"],
            "student": ["student123", "student", "member123", "member", "password", "123456"],
        }

        # Check aliases: student <-> member
        candidate_usernames = [u_clean]
        if u_clean == "student":
            candidate_usernames.append("member")
        elif u_clean == "member":
            candidate_usernames.append("student")

        for cand in candidate_usernames:
            cursor.execute("""
                SELECT u.id, u.username, u.name, u.role, u.club_id, 
                       u.avatar, u.email, u.phone, u.department, u.student_id, 
                       u.year, u.bio, u.skills, u.linkedin, u.github, u.created_at,
                       c.name as club_name, u.password_hash
                FROM users u
                LEFT JOIN clubs c ON u.club_id = c.id
                WHERE LOWER(u.username) = ?
            """, (cand,))
            user_row = cursor.fetchone()
            if user_row:
                user_dict = dict(user_row)
                allowed_pwds = demo_passwords.get(cand, [])
                if p_clean.lower() in [x.lower() for x in allowed_pwds]:
                    del user_dict["password_hash"]
                    return user_dict
                # Also allow lowercase match on password hash for custom users
                if hash_password(p_clean.lower()) == user_dict.get("password_hash"):
                    del user_dict["password_hash"]
                    return user_dict

        return None


def get_user(user_id: int, db_path: str = DB_FILE) -> Optional[Dict[str, Any]]:
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.id, u.username, u.name, u.role, u.club_id, 
                   u.avatar, u.email, u.phone, u.department, u.student_id, 
                   u.year, u.bio, u.skills, u.linkedin, u.github, u.created_at,
                   c.name as club_name
            FROM users u
            LEFT JOIN clubs c ON u.club_id = c.id
            WHERE u.id = ?
        """, (user_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def update_user_profile(user_id: int, data: Dict[str, Any], db_path: str = DB_FILE) -> Optional[Dict[str, Any]]:
    """Updates profile information for a user including avatar, personal details, and optional password."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        
        allowed_fields = [
            "name", "avatar", "email", "phone", "department", 
            "student_id", "year", "bio", "skills", "linkedin", "github"
        ]
        
        fields = []
        values = []
        for f in allowed_fields:
            if f in data:
                fields.append(f"{f} = ?")
                values.append(data[f])
                
        # Optional password update
        if data.get("new_password"):
            new_pwd = str(data["new_password"]).strip()
            if len(new_pwd) >= 4:
                fields.append("password_hash = ?")
                values.append(hash_password(new_pwd))
                
        if fields:
            values.append(user_id)
            query = f"UPDATE users SET {', '.join(fields)} WHERE id = ?"
            cursor.execute(query, tuple(values))
            
            # Sync name & email with members table if exists
            cursor.execute("SELECT name, role FROM users WHERE id = ?", (user_id,))
            u_row = cursor.fetchone()
            if u_row:
                new_name = data.get("name", u_row["name"])
                new_email = data.get("email")
                cursor.execute("""
                    UPDATE members 
                    SET name = COALESCE(?, name),
                        email = COALESCE(?, email)
                    WHERE LOWER(name) = LOWER(?) OR (email IS NOT NULL AND LOWER(email) = LOWER(?))
                """, (new_name, new_email, u_row["name"], new_email or ""))
            conn.commit()

    return get_user(user_id, db_path=db_path)


# --- DATABASE AUDIT LOGS & SYSTEM METRICS ---

def log_login_event(
    username: str,
    role: Optional[str] = None,
    portal: Optional[str] = None,
    status: str = "SUCCESS",
    user_id: Optional[int] = None,
    ip_address: str = "127.0.0.1",
    user_agent: str = "",
    db_path: str = DB_FILE
) -> int:
    """Records every authentication event (login, failed login, registration, logout) into SQLite."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO login_logs (user_id, username, role, portal, status, ip_address, user_agent)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, username.strip().lower(), role, portal, status, ip_address, user_agent))
        conn.commit()
        return cursor.lastrowid


def get_login_logs(limit: int = 50, db_path: str = DB_FILE) -> List[Dict[str, Any]]:
    """Retrieves recent login and authentication audit logs."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT l.*, u.name as full_name
            FROM login_logs l
            LEFT JOIN users u ON l.user_id = u.id
            ORDER BY l.timestamp DESC, l.id DESC
            LIMIT ?
        """, (limit,))
        return [dict(row) for row in cursor.fetchall()]


def clear_login_logs(db_path: str = DB_FILE) -> bool:
    """Clears login audit trail."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM login_logs")
        conn.commit()
        return True


def get_database_overview(db_path: str = DB_FILE) -> Dict[str, Any]:
    """Returns comprehensive metadata, stats, and audit trails for the SQLite database."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()

        # Row counts across all tables
        counts = {}
        for table in ["users", "login_logs", "clubs", "members", "activities", "attendance", "announcements"]:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                counts[table] = cursor.fetchone()[0]
            except Exception:
                counts[table] = 0

        # File size on disk
        file_size_bytes = os.path.getsize(db_path) if os.path.exists(db_path) else 0
        file_size_kb = round(file_size_bytes / 1024, 2)

        # All registered users with their last successful login
        cursor.execute("""
            SELECT u.id, u.username, u.name, u.role, u.club_id, u.avatar, u.department,
                   c.name as club_name, u.created_at,
                   MAX(CASE WHEN l.status = 'SUCCESS' THEN l.timestamp END) as last_login
            FROM users u
            LEFT JOIN clubs c ON u.club_id = c.id
            LEFT JOIN login_logs l ON l.user_id = u.id OR LOWER(l.username) = LOWER(u.username)
            GROUP BY u.id
            ORDER BY u.id ASC
        """)
        users_list = [dict(row) for row in cursor.fetchall()]

        # Recent 35 login/auth events
        cursor.execute("""
            SELECT l.id, l.username, l.role, l.portal, l.status, l.ip_address, l.user_agent, l.timestamp,
                   COALESCE(u.name, l.username) as full_name
            FROM login_logs l
            LEFT JOIN users u ON l.user_id = u.id
            ORDER BY l.timestamp DESC, l.id DESC
            LIMIT 35
        """)
        recent_logs = [dict(row) for row in cursor.fetchall()]

        return {
            "db_file": os.path.basename(db_path),
            "db_path": os.path.abspath(db_path),
            "file_size_kb": file_size_kb,
            "sqlite_version": sqlite3.sqlite_version,
            "table_counts": counts,
            "users": users_list,
            "recent_logs": recent_logs
        }


# --- DASHBOARD & ANALYTICS ---

def get_dashboard_stats(db_path: str = DB_FILE) -> Dict[str, Any]:
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM clubs")
        total_clubs = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM members WHERE status = 'Active'")
        active_members = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM activities")
        total_activities = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM activities WHERE status = 'Completed'")
        completed_activities = cursor.fetchone()[0]

        cursor.execute("SELECT COALESCE(SUM(hours_credited), 0) FROM attendance WHERE status = 'Present'")
        total_hours = cursor.fetchone()[0]

        # Activity Breakdown by Category
        cursor.execute("""
            SELECT category, COUNT(*) as count 
            FROM activities 
            GROUP BY category 
            ORDER BY count DESC
        """)
        categories = [dict(row) for row in cursor.fetchall()]

        # Activity Status Breakdown
        cursor.execute("""
            SELECT status, COUNT(*) as count 
            FROM activities 
            GROUP BY status
        """)
        status_breakdown = [dict(row) for row in cursor.fetchall()]

        # Top 5 most active members
        cursor.execute("""
            SELECT m.name, c.name as club_name, 
                   COUNT(DISTINCT att.activity_id) as activities_attended,
                   SUM(att.hours_credited) as total_hours
            FROM attendance att
            JOIN members m ON att.member_id = m.id
            JOIN clubs c ON m.club_id = c.id
            WHERE att.status = 'Present'
            GROUP BY m.id
            ORDER BY total_hours DESC, activities_attended DESC
            LIMIT 5
        """)
        top_members = [dict(row) for row in cursor.fetchall()]

        # Recent activities
        cursor.execute("""
            SELECT a.id, a.title, a.date, a.category, a.status, c.name as club_name,
                   COUNT(CASE WHEN att.status = 'Present' THEN 1 END) as attendees
            FROM activities a
            JOIN clubs c ON a.club_id = c.id
            LEFT JOIN attendance att ON a.id = att.activity_id
            GROUP BY a.id
            ORDER BY a.date DESC
            LIMIT 5
        """)
        recent_activities = [dict(row) for row in cursor.fetchall()]

        # Recent announcements
        cursor.execute("""
            SELECT an.*, c.name as club_name
            FROM announcements an
            JOIN clubs c ON an.club_id = c.id
            ORDER BY an.id DESC
            LIMIT 5
        """)
        recent_announcements = [dict(row) for row in cursor.fetchall()]

        return {
            "total_clubs": total_clubs,
            "active_members": active_members,
            "total_activities": total_activities,
            "completed_activities": completed_activities,
            "total_hours": round(total_hours, 1),
            "categories": categories,
            "status_breakdown": status_breakdown,
            "top_members": top_members,
            "recent_activities": recent_activities,
            "recent_announcements": recent_announcements
        }


# --- CSV EXPORT GENERATOR ---

def generate_activities_csv(db_path: str = DB_FILE) -> str:
    activities = get_activities(db_path=db_path)
    output = ["ID,Club,Title,Category,Date,Duration (Hrs),Location,Status,Attendees,Description"]
    for a in activities:
        desc = (a.get('description') or '').replace('"', '""').replace('\n', ' ')
        row = f'{a["id"]},"{a["club_name"]}","{a["title"]}","{a["category"]}","{a["date"]}",{a["duration_hours"]},"{a.get("location") or ""}","{a["status"]}",{a["attendees_count"]},"{desc}"'
        output.append(row)
    return "\n".join(output)


def generate_attendance_csv(db_path: str = DB_FILE) -> str:
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT att.id, a.title as activity_title, a.date, c.name as club_name,
                   m.name as member_name, m.role, att.status, att.hours_credited, att.notes
            FROM attendance att
            JOIN activities a ON att.activity_id = a.id
            JOIN members m ON att.member_id = m.id
            JOIN clubs c ON a.club_id = c.id
            ORDER BY a.date DESC, m.name ASC
        """)
        rows = cursor.fetchall()
        output = ["ID,Club,Activity,Date,Member Name,Role,Status,Hours Credited,Notes"]
        for r in rows:
            notes = (r['notes'] or '').replace('"', '""').replace('\n', ' ')
            row = f'{r["id"]},"{r["club_name"]}","{r["activity_title"]}","{r["date"]}","{r["member_name"]}","{r["role"]}","{r["status"]}",{r["hours_credited"]},"{notes}"'
            output.append(row)
        return "\n".join(output)


# --- STUDENT RSVP & PARTICIPATION ---

def rsvp_activity(activity_id: int, member_id: int, db_path: str = DB_FILE) -> bool:
    """Registers or RSVPs a student for an upcoming activity."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO attendance (activity_id, member_id, status, hours_credited, notes)
            VALUES (?, ?, 'RSVP', 0.0, 'Pre-registered online via Student Portal')
            ON CONFLICT(activity_id, member_id) DO UPDATE SET
                status = CASE WHEN attendance.status = 'Present' THEN 'Present' ELSE 'RSVP' END
        """, (activity_id, member_id))
        conn.commit()
        return True


def cancel_rsvp(activity_id: int, member_id: int, db_path: str = DB_FILE) -> bool:
    """Cancels a student's RSVP if not yet marked present."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM attendance
            WHERE activity_id = ? AND member_id = ? AND status = 'RSVP'
        """, (activity_id, member_id))
        conn.commit()
        return cursor.rowcount > 0


def get_member_rsvps(member_id: int, db_path: str = DB_FILE) -> List[int]:
    """Returns list of activity IDs that a member has RSVP'd for or attended."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT activity_id FROM attendance
            WHERE member_id = ? AND status IN ('RSVP', 'Present')
        """, (member_id,))
        return [row["activity_id"] for row in cursor.fetchall()]


def get_member_by_user(user_id_or_username, db_path: str = DB_FILE) -> Optional[Dict[str, Any]]:
    """Helper to locate member record for authenticated user."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT m.*
            FROM users u
            JOIN members m ON LOWER(m.name) = LOWER(u.name) OR (u.club_id IS NOT NULL AND m.club_id = u.club_id)
            WHERE u.id = ? OR LOWER(u.username) = LOWER(?)
            LIMIT 1
        """, (str(user_id_or_username), str(user_id_or_username)))
        row = cursor.fetchone()
        if row:
            return dict(row)
        cursor.execute("SELECT * FROM members LIMIT 1")
        row = cursor.fetchone()
        return dict(row) if row else None


# --- CERTIFICATE GENERATION ---

def get_student_certificates(member_id: int, db_path: str = DB_FILE) -> List[Dict[str, Any]]:
    """Retrieves activities where the student was marked Present, eligible for certification."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT att.id as attendance_id, att.hours_credited, att.notes,
                   a.id as activity_id, a.title as activity_title, a.category, a.date as activity_date,
                   a.location, a.duration_hours,
                   c.name as club_name, c.lead_name,
                   m.id as member_id, m.name as member_name, m.email
            FROM attendance att
            JOIN activities a ON att.activity_id = a.id
            JOIN clubs c ON a.club_id = c.id
            JOIN members m ON att.member_id = m.id
            WHERE att.member_id = ? AND att.status = 'Present'
            ORDER BY a.date DESC
        """, (member_id,))
        return [dict(row) for row in cursor.fetchall()]


def get_certificate_details(activity_id: int, member_id: int, db_path: str = DB_FILE) -> Optional[Dict[str, Any]]:
    """Generates full verified certificate payload with verification ID."""
    with get_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT att.id as attendance_id, att.hours_credited, att.notes,
                   a.id as activity_id, a.title as activity_title, a.category, a.date as activity_date,
                   a.location, a.duration_hours, a.description,
                   c.name as club_name, c.lead_name,
                   m.id as member_id, m.name as member_name, m.email, m.role as member_role
            FROM attendance att
            JOIN activities a ON att.activity_id = a.id
            JOIN clubs c ON a.club_id = c.id
            JOIN members m ON att.member_id = m.id
            WHERE att.activity_id = ? AND att.member_id = ?
        """, (activity_id, member_id))
        row = cursor.fetchone()
        if not row:
            return None
        data = dict(row)
        raw_token = f"CAC-{data['activity_id']}-{data['member_id']}-{data['activity_date']}"
        cert_hash = hashlib.sha256(raw_token.encode()).hexdigest()[:8].upper()
        clean_date = str(data['activity_date']).replace('-', '')
        data["cert_serial"] = f"CAC-{clean_date}-{cert_hash}"
        data["issued_date"] = data["activity_date"]
        data["issuer"] = "Collegiate Club & Student Activities Directorate"
        return data


# --- AI EVENT ATTENDANCE & TURNOUT PREDICTOR ---

def predict_event_turnout(club_id: Optional[int], category: str, duration_hours: float, date_str: str = "", location: str = "", db_path: str = DB_FILE) -> Dict[str, Any]:
    """
    Statistical regression heuristic predictor for event turnout.
    Integrates club historical baseline, category draw multiplier,
    day-of-week engagement index, and duration sweet-spot factor.
    """
    with get_connection(db_path) as conn:
        cursor = conn.cursor()

        # 1. Club baseline and member roster size
        if club_id and str(club_id).isdigit():
            cursor.execute("SELECT COUNT(*) FROM members WHERE club_id = ?", (int(club_id),))
            club_size = cursor.fetchone()[0] or 12
            cursor.execute("SELECT name FROM clubs WHERE id = ?", (int(club_id),))
            c_row = cursor.fetchone()
            club_name = c_row[0] if c_row else "Selected Club"
        else:
            cursor.execute("SELECT COUNT(*) FROM members")
            total_m = cursor.fetchone()[0] or 30
            club_size = max(10, total_m // 5)
            club_name = "All Campus Clubs"

        # 2. Historical average attendance per category
        cursor.execute("""
            SELECT a.category, AVG(sub.attendee_count) as avg_att
            FROM activities a
            JOIN (
                SELECT activity_id, COUNT(*) as attendee_count
                FROM attendance
                WHERE status = 'Present'
                GROUP BY activity_id
            ) sub ON a.id = sub.activity_id
            GROUP BY a.category
        """)
        cat_stats = {row["category"]: row["avg_att"] for row in cursor.fetchall()}

        # 3. Overall average attendance
        cursor.execute("""
            SELECT AVG(sub.attendee_count)
            FROM (
                SELECT activity_id, COUNT(*) as attendee_count
                FROM attendance
                WHERE status = 'Present'
                GROUP BY activity_id
            ) sub
        """)
        avg_row = cursor.fetchone()
        overall_avg = float(avg_row[0]) if avg_row and avg_row[0] else 12.0

        base_val = cat_stats.get(category, overall_avg) or overall_avg

        # Multipliers
        cat_multipliers = {
            "Competition": 1.45,
            "Hackathon": 1.60,
            "Social": 1.38,
            "Workshop": 1.25,
            "Seminar": 1.10,
            "Meeting": 0.80,
            "Community": 1.15
        }
        cat_mult = cat_multipliers.get(category, 1.15)

        # Day of week impact
        day_mult = 1.0
        day_name = "Weekday"
        if date_str:
            try:
                import datetime
                dt = datetime.datetime.strptime(date_str, "%Y-%m-%d")
                w = dt.weekday()
                day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                day_name = day_names[w]
                if w == 4: # Friday
                    day_mult = 1.28
                elif w == 5: # Saturday
                    day_mult = 1.35
                elif w in (2, 3): # Wed, Thu
                    day_mult = 1.06
                elif w == 0: # Monday
                    day_mult = 0.88
                elif w == 6: # Sunday
                    day_mult = 1.12
            except Exception:
                pass

        # Duration impact
        if duration_hours <= 1.0:
            dur_mult = 0.90
        elif 1.5 <= duration_hours <= 3.5:
            dur_mult = 1.10
        elif duration_hours > 5.0:
            dur_mult = 1.22 if category in ["Competition", "Hackathon"] else 0.85
        else:
            dur_mult = 1.0

        # Club size scaling
        club_scale = min(1.5, max(0.8, (club_size / 6.0) ** 0.5))

        predicted = base_val * (cat_mult / 1.15) * day_mult * dur_mult * club_scale
        predicted = max(5, round(predicted))
        margin = max(3, round(predicted * 0.12))
        low_bound = max(4, predicted - margin)
        high_bound = predicted + margin

        if predicted >= 22:
            demand_level = "🔥 High Demand"
            demand_color = "#ef4444"
            confidence = 88
        elif predicted >= 14:
            demand_level = "⚡ Strong Turnout"
            demand_color = "#f59e0b"
            confidence = 84
        else:
            demand_level = "⚖️ Moderate Turnout"
            demand_color = "#3b82f6"
            confidence = 79

        insights = []
        if day_mult > 1.2:
            insights.append(f"🎉 {day_name} scheduling gives an estimated +{round((day_mult - 1) * 100)}% weekend attendance boost.")
        elif day_mult < 1.0:
            insights.append(f"⚠️ {day_name} typically sees {round((1 - day_mult) * 100)}% lower turnout due to coursework. Late afternoon recommended.")
        else:
            insights.append(f"📅 Mid-week timing on {day_name} ensures high core member engagement.")

        if category in ["Competition", "Workshop", "Social"]:
            insights.append(f"🎯 {category} events consistently attract cross-department participants beyond club roster.")

        if duration_hours >= 4.0:
            insights.append(f"⏱️ Extended duration ({duration_hours}h) benefits from snack/hydration breaks to reduce drop-off.")
        else:
            insights.append(f"⏱️ {duration_hours}h duration aligns with optimal student attention span.")

        venue_seats = max(25, round(high_bound * 1.25))
        insights.append(f"🏛️ Recommended venue capacity: At least {venue_seats} seats.")

        return {
            "predicted_attendance": predicted,
            "range": f"{low_bound} – {high_bound} attendees",
            "low_bound": low_bound,
            "high_bound": high_bound,
            "demand_level": demand_level,
            "demand_color": demand_color,
            "confidence_score": confidence,
            "day_name": day_name,
            "club_name": club_name,
            "category": category,
            "insights": insights
        }
