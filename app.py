"""
Club Activities Tracker - Web Application Server
Built with standard library Python (http.server, sqlite3, json, csv).
Zero third-party dependencies required! Runs anywhere Python 3 is installed.
"""

import sys
import os
import json
import mimetypes
from urllib.parse import urlparse, parse_qs
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

import database
from seed_data import seed_database

PORT = 8000
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")


class ClubTrackerHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=STATIC_DIR, **kwargs)

    def send_json(self, data, status_code=200):
        body = json.dumps(data, default=str).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.end_headers()
        self.wfile.write(body)

    def send_csv(self, csv_content: str, filename: str):
        body = csv_content.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/csv; charset=utf-8")
        self.send_header("Content-Disposition", f'attachment; filename="{filename}"')
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def read_json_body(self):
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length > 0:
            raw = self.rfile.read(content_length).decode("utf-8")
            return json.loads(raw)
        return {}

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        try:
            # REST API Handlers
            if path == "/api/stats":
                stats = database.get_dashboard_stats()
                return self.send_json({"success": True, "data": stats})

            elif path == "/api/clubs":
                clubs = database.get_clubs()
                return self.send_json({"success": True, "data": clubs})

            elif path.startswith("/api/clubs/"):
                parts = path.strip("/").split("/")
                if len(parts) == 3 and parts[2].isdigit():
                    club = database.get_club(int(parts[2]))
                    if club:
                        return self.send_json({"success": True, "data": club})
                    return self.send_json({"success": False, "error": "Club not found"}, 404)

            elif path == "/api/members":
                club_id = int(query["club_id"][0]) if "club_id" in query and query["club_id"][0].isdigit() else None
                members = database.get_members(club_id=club_id)
                return self.send_json({"success": True, "data": members})

            elif path == "/api/activities":
                club_id = int(query["club_id"][0]) if "club_id" in query and query["club_id"][0].isdigit() else None
                status = query["status"][0] if "status" in query and query["status"][0] else None
                activities = database.get_activities(club_id=club_id, status=status)
                return self.send_json({"success": True, "data": activities})

            elif path.startswith("/api/activities/"):
                parts = path.strip("/").split("/")
                if len(parts) == 3 and parts[2].isdigit():
                    act = database.get_activity(int(parts[2]))
                    if act:
                        return self.send_json({"success": True, "data": act})
                    return self.send_json({"success": False, "error": "Activity not found"}, 404)
                elif len(parts) == 4 and parts[2].isdigit() and parts[3] == "attendance":
                    activity_id = int(parts[2])
                    attendance = database.get_attendance_for_activity(activity_id)
                    return self.send_json({"success": True, "data": attendance})

            elif path == "/api/export/activities":
                csv_data = database.generate_activities_csv()
                return self.send_csv(csv_data, "club_activities_report.csv")

            elif path == "/api/export/attendance":
                csv_data = database.generate_attendance_csv()
                return self.send_csv(csv_data, "club_attendance_report.csv")

            elif path == "/api/announcements":
                club_id = int(query["club_id"][0]) if "club_id" in query and query["club_id"][0].isdigit() else None
                announcements = database.get_announcements(club_id=club_id)
                return self.send_json({"success": True, "data": announcements})

            elif path == "/api/auth/demo-users":
                demo_accounts = [
                    {"username": "admin", "password": "admin123", "role": "Admin", "name": "Dr. Sarah Jenkins (Faculty Advisor)", "desc": "Full administrative access to manage all clubs, records, and exports."},
                    {"username": "officer", "password": "officer123", "role": "Officer", "name": "Aarav Sharma (Coding Club Lead)", "desc": "Can log activities, take attendance roll call, and post notices."},
                    {"username": "member", "password": "member123", "role": "Member", "name": "Sneha Reddy (Student Member)", "desc": "View dashboard, events calendar, notices, and personal attendance."}
                ]
                return self.send_json({"success": True, "data": demo_accounts})

            elif path.startswith("/api/student/") and path.endswith("/rsvps"):
                parts = path.strip("/").split("/")
                member_id = int(parts[2]) if len(parts) >= 3 and parts[2].isdigit() else 49
                rsvps = database.get_member_rsvps(member_id)
                return self.send_json({"success": True, "data": rsvps})

            elif path.startswith("/api/student/") and path.endswith("/certificates"):
                parts = path.strip("/").split("/")
                member_id = int(parts[2]) if len(parts) >= 3 and parts[2].isdigit() else 49
                certs = database.get_student_certificates(member_id)
                return self.send_json({"success": True, "data": certs})

            elif path.startswith("/api/certificate/"):
                parts = path.strip("/").split("/")
                if len(parts) >= 4 and parts[2].isdigit() and parts[3].isdigit():
                    cert_data = database.get_certificate_details(int(parts[2]), int(parts[3]))
                    if cert_data:
                        return self.send_json({"success": True, "data": cert_data})
                    return self.send_json({"success": False, "error": "Certificate not found or activity not completed"}, 404)

            elif path == "/api/database/overview":
                overview = database.get_database_overview()
                return self.send_json({"success": True, "data": overview})

            elif path == "/api/database/login-logs":
                limit = int(query["limit"][0]) if "limit" in query and query["limit"][0].isdigit() else 50
                logs = database.get_login_logs(limit=limit)
                return self.send_json({"success": True, "data": logs})

            elif path == "/api/database/download":
                if os.path.exists(database.DB_FILE):
                    with open(database.DB_FILE, "rb") as f:
                        content = f.read()
                    self.send_response(200)
                    self.send_header("Content-Type", "application/octet-stream")
                    self.send_header("Content-Disposition", 'attachment; filename="club_tracker.db"')
                    self.send_header("Content-Length", str(len(content)))
                    self.end_headers()
                    self.wfile.write(content)
                    return
                return self.send_json({"success": False, "error": "Database file not found"}, 404)

            elif path == "/api/user/profile":
                user_id = int(query["user_id"][0]) if "user_id" in query and query["user_id"][0].isdigit() else None
                if not user_id:
                    return self.send_json({"success": False, "error": "user_id is required"}, 400)
                user = database.get_user(user_id)
                if user:
                    return self.send_json({"success": True, "data": user})
                return self.send_json({"success": False, "error": "User not found"}, 404)

            # Fallback to serving static files or index.html for SPA routes
            if path == "/" or not os.path.exists(os.path.join(STATIC_DIR, path.lstrip("/"))):
                self.path = "/index.html"
            
            return super().do_GET()

        except Exception as e:
            return self.send_json({"success": False, "error": str(e)}, 500)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        try:
            data = self.read_json_body()

            if path == "/api/clubs":
                club_id = database.add_club(
                    name=data.get("name", "").strip(),
                    category=data.get("category", "General"),
                    description=data.get("description", "").strip(),
                    lead_name=data.get("lead_name", "").strip()
                )
                return self.send_json({"success": True, "id": club_id, "message": "Club created successfully"}, 201)

            elif path == "/api/members":
                member_id = database.add_member(
                    club_id=int(data.get("club_id")),
                    name=data.get("name", "").strip(),
                    email=data.get("email", "").strip(),
                    role=data.get("role", "Member"),
                    join_date=data.get("join_date", "")
                )
                return self.send_json({"success": True, "id": member_id, "message": "Member added successfully"}, 201)

            elif path == "/api/activities":
                act_id = database.add_activity(
                    club_id=int(data.get("club_id")),
                    title=data.get("title", "").strip(),
                    category=data.get("category", "Workshop"),
                    date=data.get("date", ""),
                    duration_hours=float(data.get("duration_hours", 1.0)),
                    location=data.get("location", "").strip(),
                    status=data.get("status", "Planned"),
                    description=data.get("description", "").strip()
                )
                return self.send_json({"success": True, "id": act_id, "message": "Activity created successfully"}, 201)

            elif path.startswith("/api/activities/") and path.endswith("/attendance"):
                parts = path.strip("/").split("/")
                activity_id = int(parts[2])
                records = data.get("attendance", [])
                database.bulk_record_attendance(activity_id, records)
            elif path == "/api/predict-attendance":
                club_id = data.get("club_id")
                category = data.get("category", "Workshop")
                duration_hours = float(data.get("duration_hours", 2.0))
                date_str = data.get("date", "")
                location = data.get("location", "")
                pred = database.predict_event_turnout(club_id, category, duration_hours, date_str, location)
                return self.send_json({"success": True, "data": pred})

            elif path.startswith("/api/activities/") and path.endswith("/rsvp"):
                parts = path.strip("/").split("/")
                activity_id = int(parts[2])
                member_id = int(data.get("member_id", 49))
                database.rsvp_activity(activity_id, member_id)
                return self.send_json({"success": True, "message": "RSVP recorded successfully"})

            elif path == "/api/seed":
                seed_database()
                return self.send_json({"success": True, "message": "Sample data seeded"})

            elif path == "/api/announcements":
                ann_id = database.add_announcement(
                    club_id=int(data.get("club_id")),
                    title=data.get("title", "").strip(),
                    content=data.get("content", "").strip(),
                    priority=data.get("priority", "Normal"),
                    date=data.get("date", "")
                )
                return self.send_json({"success": True, "id": ann_id, "message": "Announcement created"}, 201)

            elif path == "/api/database/clear-logs":
                database.clear_login_logs()
                return self.send_json({"success": True, "message": "Login audit trail cleared"})

            elif path == "/api/auth/login":
                username = data.get("username", "").strip()
                password = data.get("password", "").strip()
                portal = data.get("portal", "").strip()  # 'Admin', 'Officer', 'Member'
                client_ip = self.client_address[0] if hasattr(self, 'client_address') and self.client_address else "127.0.0.1"
                user_agent = self.headers.get("User-Agent", "Web Browser")

                user = database.authenticate_user(username, password)
                if not user:
                    database.log_login_event(
                        username=username,
                        role=None,
                        portal=portal,
                        status="FAILED_PASSWORD",
                        ip_address=client_ip,
                        user_agent=user_agent
                    )
                    return self.send_json({"success": False, "error": "❌ Invalid username or password!"}, 401)

                # STRICT ROLE & PORTAL VALIDATION (Portal is mandatory)
                if not portal:
                    return self.send_json({
                        "success": False,
                        "error": "❌ Please select your portal section (Admin, Club Officer, or Student)."
                    }, 400)

                portal_clean = portal.strip().lower()
                user_role_clean = user["role"].strip().lower()
                if portal_clean != user_role_clean:
                    database.log_login_event(
                        username=username,
                        role=user["role"],
                        portal=portal,
                        status="FAILED_ROLE_MISMATCH",
                        user_id=user["id"],
                        ip_address=client_ip,
                        user_agent=user_agent
                    )
                    role_titles = {
                        "admin": "👑 Administrator (Admin)",
                        "officer": "⚡ Club Officer",
                        "member": "🎓 Student Member"
                    }
                    portal_titles = {
                        "admin": "👑 Admin Section",
                        "officer": "⚡ Club Officer Section",
                        "member": "🎓 Student Section"
                    }
                    return self.send_json({
                        "success": False,
                        "error": f"❌ Access Denied: Aapka account '{role_titles.get(user_role_clean, user['role'])}' hai! Aap '{portal_titles.get(portal_clean, portal)}' me login nahi kar sakte. Kripya upar se apna sahi section tab ({role_titles.get(user_role_clean, user['role'])}) select karein."
                    }, 403)

                # Record successful login in database
                database.log_login_event(
                    username=username,
                    role=user["role"],
                    portal=portal,
                    status="SUCCESS",
                    user_id=user["id"],
                    ip_address=client_ip,
                    user_agent=user_agent
                )
                token = f"demo-session-{user['id']}-{user['role'].lower()}"
                return self.send_json({"success": True, "user": user, "token": token})

            elif path == "/api/auth/register":
                username = data.get("username", "").strip()
                password = data.get("password", "").strip()
                name = data.get("name", "").strip()
                role = data.get("role", "Member")
                club_id = int(data.get("club_id")) if data.get("club_id") and str(data.get("club_id")).isdigit() else None
                client_ip = self.client_address[0] if hasattr(self, 'client_address') and self.client_address else "127.0.0.1"
                user_agent = self.headers.get("User-Agent", "Web Browser")

                if not username or not password or not name:
                    return self.send_json({"success": False, "error": "Username, password and full name are required"}, 400)

                try:
                    user_id = database.create_user(username, password, name, role, club_id)
                    user = database.get_user(user_id)
                    database.log_login_event(
                        username=username,
                        role=role,
                        portal=role,
                        status="REGISTERED",
                        user_id=user_id,
                        ip_address=client_ip,
                        user_agent=user_agent
                    )
                    token = f"demo-session-{user['id']}-{user['role'].lower()}"
                    return self.send_json({"success": True, "user": user, "token": token, "message": "Account created successfully"}, 201)
                except Exception as ex:
                    if "UNIQUE constraint failed" in str(ex):
                        return self.send_json({"success": False, "error": "Username already taken"}, 400)
                    return self.send_json({"success": False, "error": str(ex)}, 400)

            elif path == "/api/auth/logout":
                client_ip = self.client_address[0] if hasattr(self, 'client_address') and self.client_address else "127.0.0.1"
                user_agent = self.headers.get("User-Agent", "Web Browser")
                u_id = data.get("user_id") if data else None
                u_name = data.get("username", "Unknown") if data else "Unknown"
                u_role = data.get("role") if data else None
                database.log_login_event(
                    username=u_name,
                    role=u_role,
                    portal=u_role,
                    status="LOGOUT",
                    user_id=u_id,
                    ip_address=client_ip,
                    user_agent=user_agent
                )
                return self.send_json({"success": True, "message": "Logged out successfully"})

            return self.send_json({"success": False, "error": "Endpoint not found"}, 404)

        except Exception as e:
            return self.send_json({"success": False, "error": str(e)}, 400)

    def do_PUT(self):
        parsed = urlparse(self.path)
        path = parsed.path

        try:
            data = self.read_json_body()
            parts = path.strip("/").split("/")

            if len(parts) == 3 and parts[1] == "clubs" and parts[2].isdigit():
                club_id = int(parts[2])
                success = database.update_club(
                    club_id=club_id,
                    name=data.get("name", "").strip(),
                    category=data.get("category", "General"),
                    description=data.get("description", "").strip(),
                    lead_name=data.get("lead_name", "").strip()
                )
                return self.send_json({"success": success})

            elif len(parts) == 3 and parts[1] == "members" and parts[2].isdigit():
                member_id = int(parts[2])
                success = database.update_member(
                    member_id=member_id,
                    club_id=int(data.get("club_id")),
                    name=data.get("name", "").strip(),
                    email=data.get("email", "").strip(),
                    role=data.get("role", "Member"),
                    status=data.get("status", "Active")
                )
                return self.send_json({"success": success})

            elif len(parts) == 3 and parts[1] == "activities" and parts[2].isdigit():
                act_id = int(parts[2])
                success = database.update_activity(
                    activity_id=act_id,
                    club_id=int(data.get("club_id")),
                    title=data.get("title", "").strip(),
                    category=data.get("category", "Workshop"),
                    date=data.get("date", ""),
                    duration_hours=float(data.get("duration_hours", 1.0)),
                    location=data.get("location", "").strip(),
                    status=data.get("status", "Planned"),
                    description=data.get("description", "").strip()
                )
                return self.send_json({"success": success})

            elif path == "/api/user/profile":
                user_id = int(data.get("user_id")) if data.get("user_id") else None
                if not user_id:
                    return self.send_json({"success": False, "error": "user_id is required"}, 400)
                updated_user = database.update_user_profile(user_id, data)
                if updated_user:
                    return self.send_json({
                        "success": True, 
                        "user": updated_user, 
                        "message": "Profile updated successfully"
                    })
                return self.send_json({"success": False, "error": "User not found or update failed"}, 400)

            return self.send_json({"success": False, "error": "Endpoint not found"}, 404)

        except Exception as e:
            return self.send_json({"success": False, "error": str(e)}, 400)

    def do_DELETE(self):
        parsed = urlparse(self.path)
        parts = parsed.path.strip("/").split("/")

        try:
            if len(parts) == 3 and parts[1] == "clubs" and parts[2].isdigit():
                success = database.delete_club(int(parts[2]))
                return self.send_json({"success": success, "message": "Club deleted"})

            elif len(parts) == 3 and parts[1] == "members" and parts[2].isdigit():
                success = database.delete_member(int(parts[2]))
                return self.send_json({"success": success, "message": "Member deleted"})

            elif len(parts) == 3 and parts[1] == "activities" and parts[2].isdigit():
                success = database.delete_activity(int(parts[2]))
                return self.send_json({"success": success, "message": "Activity deleted"})

            elif len(parts) == 3 and parts[1] == "announcements" and parts[2].isdigit():
                success = database.delete_announcement(int(parts[2]))
                return self.send_json({"success": success, "message": "Announcement deleted"})

            elif len(parts) == 4 and parts[1] == "activities" and parts[2].isdigit() and parts[3] == "rsvp":
                activity_id = int(parts[2])
                query = parse_qs(parsed.query)
                member_id_str = query.get("member_id", ["49"])[0]
                member_id = int(member_id_str) if member_id_str.isdigit() else 49
                success = database.cancel_rsvp(activity_id, member_id)
                return self.send_json({"success": success, "message": "RSVP cancelled"})

            return self.send_json({"success": False, "error": "Endpoint not found"}, 404)

        except Exception as e:
            return self.send_json({"success": False, "error": str(e)}, 400)

    def log_message(self, format, *args):
        # Clean logging format
        print(f"[{self.log_date_time_string()}] {format % args}")


def main():
    database.init_db()
    # If starting with an empty database, seed automatically
    clubs = database.get_clubs()
    if not clubs:
        print("Empty database detected. Initializing sample data...")
        seed_database()

    ports_to_try = [8000, 8080, 5050, 3000]
    httpd = None
    selected_port = PORT

    for p in ports_to_try:
        try:
            server_address = ("0.0.0.0", p)
            httpd = ThreadingHTTPServer(server_address, ClubTrackerHandler)
            selected_port = p
            break
        except OSError as e:
            if e.errno == 48:  # Address already in use
                print(f"⚠️ Port {p} is busy, checking next port...")
                continue
            raise e

    if not httpd:
        print("❌ Could not bind to any available port.")
        sys.exit(1)

    print("\n" + "="*60)
    print(" 🚀 CLUB ACTIVITIES TRACKER SERVER IS RUNNING!")
    print(f" 🌐 Access Web Dashboard: http://localhost:{selected_port}")
    print(f" 🌐 Alternate Link:       http://127.0.0.1:{selected_port}")
    print(" 🗄️ Database: club_tracker.db (SQLite)")
    print(" ⏹️ Press Ctrl+C in terminal to stop server")
    print("="*60 + "\n")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Club Activities Tracker server...")
        httpd.server_close()


if __name__ == "__main__":
    main()
