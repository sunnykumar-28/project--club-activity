"""
Club Activities Tracker - Flask Backend Server
Alternative backend implementation using Python Flask & SQLite.
Run this if you prefer Flask over standard library Python!
"""

import os
from flask import Flask, request, jsonify, Response, send_from_directory
import database
from seed_data import seed_database

# Initialize Flask app
STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
app = Flask(__name__, static_folder=STATIC_DIR)

# Enable CORS headers manually (zero dependency on flask-cors if not installed)
@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    return response


# --- STATIC FILES / FRONTEND ROUTES ---

@app.route("/")
def serve_index():
    return send_from_directory(STATIC_DIR, "index.html")


@app.route("/<path:path>")
def serve_static(path):
    if os.path.exists(os.path.join(STATIC_DIR, path)):
        return send_from_directory(STATIC_DIR, path)
    return send_from_directory(STATIC_DIR, "index.html")


# --- REST API: STATS & DASHBOARD ---

@app.route("/api/stats", methods=["GET"])
def get_stats():
    stats = database.get_dashboard_stats()
    return jsonify({"success": True, "data": stats})


# --- REST API: CLUBS CRUD ---

@app.route("/api/clubs", methods=["GET"])
def list_clubs():
    clubs = database.get_clubs()
    return jsonify({"success": True, "data": clubs})


@app.route("/api/clubs/<int:club_id>", methods=["GET"])
def get_club(club_id):
    club = database.get_club(club_id)
    if not club:
        return jsonify({"success": False, "error": "Club not found"}), 404
    return jsonify({"success": True, "data": club})


@app.route("/api/clubs", methods=["POST"])
def create_club():
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    if not name:
        return jsonify({"success": False, "error": "Club name is required"}), 400

    club_id = database.add_club(
        name=name,
        category=data.get("category", "General"),
        description=data.get("description", "").strip(),
        lead_name=data.get("lead_name", "").strip()
    )
    return jsonify({"success": True, "id": club_id, "message": "Club created successfully"}), 201


@app.route("/api/clubs/<int:club_id>", methods=["PUT"])
def update_club(club_id):
    data = request.get_json() or {}
    success = database.update_club(
        club_id=club_id,
        name=data.get("name", "").strip(),
        category=data.get("category", "General"),
        description=data.get("description", "").strip(),
        lead_name=data.get("lead_name", "").strip()
    )
    return jsonify({"success": success})


@app.route("/api/clubs/<int:club_id>", methods=["DELETE"])
def delete_club(club_id):
    success = database.delete_club(club_id)
    return jsonify({"success": success, "message": "Club deleted"})


# --- REST API: MEMBERS CRUD ---

@app.route("/api/members", methods=["GET"])
def list_members():
    club_id_arg = request.args.get("club_id")
    club_id = int(club_id_arg) if club_id_arg and club_id_arg.isdigit() else None
    members = database.get_members(club_id=club_id)
    return jsonify({"success": True, "data": members})


@app.route("/api/members", methods=["POST"])
def create_member():
    data = request.get_json() or {}
    club_id = data.get("club_id")
    name = data.get("name", "").strip()
    if not club_id or not name:
        return jsonify({"success": False, "error": "Club and Name are required"}), 400

    member_id = database.add_member(
        club_id=int(club_id),
        name=name,
        email=data.get("email", "").strip(),
        role=data.get("role", "Member"),
        join_date=data.get("join_date", "")
    )
    return jsonify({"success": True, "id": member_id, "message": "Member added successfully"}), 201


@app.route("/api/members/<int:member_id>", methods=["PUT"])
def update_member(member_id):
    data = request.get_json() or {}
    success = database.update_member(
        member_id=member_id,
        club_id=int(data.get("club_id")),
        name=data.get("name", "").strip(),
        email=data.get("email", "").strip(),
        role=data.get("role", "Member"),
        status=data.get("status", "Active")
    )
    return jsonify({"success": success})


@app.route("/api/members/<int:member_id>", methods=["DELETE"])
def delete_member(member_id):
    success = database.delete_member(member_id)
    return jsonify({"success": success, "message": "Member deleted"})


# --- REST API: ACTIVITIES CRUD ---

@app.route("/api/activities", methods=["GET"])
def list_activities():
    club_id_arg = request.args.get("club_id")
    club_id = int(club_id_arg) if club_id_arg and club_id_arg.isdigit() else None
    status = request.args.get("status")
    activities = database.get_activities(club_id=club_id, status=status)
    return jsonify({"success": True, "data": activities})


@app.route("/api/activities/<int:activity_id>", methods=["GET"])
def get_activity(activity_id):
    act = database.get_activity(activity_id)
    if not act:
        return jsonify({"success": False, "error": "Activity not found"}), 404
    return jsonify({"success": True, "data": act})


@app.route("/api/activities", methods=["POST"])
def create_activity():
    data = request.get_json() or {}
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
    return jsonify({"success": True, "id": act_id, "message": "Activity created successfully"}), 201


@app.route("/api/activities/<int:activity_id>", methods=["PUT"])
def update_activity(activity_id):
    data = request.get_json() or {}
    success = database.update_activity(
        activity_id=activity_id,
        club_id=int(data.get("club_id")),
        title=data.get("title", "").strip(),
        category=data.get("category", "Workshop"),
        date=data.get("date", ""),
        duration_hours=float(data.get("duration_hours", 1.0)),
        location=data.get("location", "").strip(),
        status=data.get("status", "Planned"),
        description=data.get("description", "").strip()
    )
    return jsonify({"success": success})


@app.route("/api/activities/<int:activity_id>", methods=["DELETE"])
def delete_activity(activity_id):
    success = database.delete_activity(activity_id)
    return jsonify({"success": success, "message": "Activity deleted"})


# --- REST API: ATTENDANCE & ROLL CALL ---

@app.route("/api/activities/<int:activity_id>/attendance", methods=["GET"])
def get_attendance(activity_id):
    attendance = database.get_attendance_for_activity(activity_id)
    return jsonify({"success": True, "data": attendance})


@app.route("/api/activities/<int:activity_id>/attendance", methods=["POST"])
def record_attendance(activity_id):
    data = request.get_json() or {}
    records = data.get("attendance", [])
    database.bulk_record_attendance(activity_id, records)
    return jsonify({"success": True, "message": "Attendance records saved"})


# --- REST API: ANNOUNCEMENTS ---

@app.route("/api/announcements", methods=["GET"])
def get_announcements():
    club_id_arg = request.args.get("club_id")
    club_id = int(club_id_arg) if club_id_arg and club_id_arg.isdigit() else None
    announcements = database.get_announcements(club_id=club_id)
    return jsonify({"success": True, "data": announcements})


@app.route("/api/announcements", methods=["POST"])
def create_announcement():
    data = request.get_json() or {}
    ann_id = database.add_announcement(
        club_id=int(data.get("club_id")),
        title=data.get("title", "").strip(),
        content=data.get("content", "").strip(),
        priority=data.get("priority", "Normal"),
        date=data.get("date", "")
    )
    return jsonify({"success": True, "id": ann_id, "message": "Announcement created"}), 201


@app.route("/api/announcements/<int:ann_id>", methods=["DELETE"])
def delete_announcement(ann_id):
    success = database.delete_announcement(ann_id)
    return jsonify({"success": success, "message": "Announcement deleted"})


# --- REST API: PREDICTOR, RSVP & CERTIFICATES ---

@app.route("/api/predict-attendance", methods=["POST"])
def predict_attendance():
    data = request.get_json() or {}
    club_id = data.get("club_id")
    category = data.get("category", "Workshop")
    duration_hours = float(data.get("duration_hours", 2.0))
    date_str = data.get("date", "")
    location = data.get("location", "")
    pred = database.predict_event_turnout(club_id, category, duration_hours, date_str, location)
    return jsonify({"success": True, "data": pred})


@app.route("/api/activities/<int:activity_id>/rsvp", methods=["POST"])
def rsvp_activity_route(activity_id):
    data = request.get_json() or {}
    member_id = int(data.get("member_id", 49))
    database.rsvp_activity(activity_id, member_id)
    return jsonify({"success": True, "message": "RSVP recorded successfully"})


@app.route("/api/activities/<int:activity_id>/rsvp", methods=["DELETE"])
def cancel_rsvp_route(activity_id):
    member_id_str = request.args.get("member_id", "49")
    member_id = int(member_id_str) if member_id_str.isdigit() else 49
    success = database.cancel_rsvp(activity_id, member_id)
    return jsonify({"success": success, "message": "RSVP cancelled"})


@app.route("/api/student/<int:member_id>/rsvps", methods=["GET"])
def get_student_rsvps_route(member_id):
    rsvps = database.get_member_rsvps(member_id)
    return jsonify({"success": True, "data": rsvps})


@app.route("/api/student/<int:member_id>/certificates", methods=["GET"])
def get_student_certificates_route(member_id):
    certs = database.get_student_certificates(member_id)
    return jsonify({"success": True, "data": certs})


@app.route("/api/certificate/<int:activity_id>/<int:member_id>", methods=["GET"])
def get_certificate_route(activity_id, member_id):
    cert = database.get_certificate_details(activity_id, member_id)
    if not cert:
        return jsonify({"success": False, "error": "Certificate not found"}), 404
    return jsonify({"success": True, "data": cert})


# --- REST API: DATABASE & AUDIT LOGS ---

@app.route("/api/database/overview", methods=["GET"])
def database_overview():
    overview = database.get_database_overview()
    return jsonify({"success": True, "data": overview})


@app.route("/api/database/login-logs", methods=["GET"])
def database_login_logs():
    limit_arg = request.args.get("limit", "50")
    limit = int(limit_arg) if limit_arg.isdigit() else 50
    logs = database.get_login_logs(limit=limit)
    return jsonify({"success": True, "data": logs})


@app.route("/api/database/clear-logs", methods=["POST"])
def database_clear_logs():
    database.clear_login_logs()
    return jsonify({"success": True, "message": "Login audit trail cleared"})


@app.route("/api/database/download", methods=["GET"])
def database_download():
    if os.path.exists(database.DB_FILE):
        return send_file(database.DB_FILE, as_attachment=True, download_name="club_tracker.db")
    return jsonify({"success": False, "error": "Database file not found"}), 404


# --- REST API: AUTHENTICATION ---

@app.route("/api/auth/login", methods=["POST"])
def auth_login():
    data = request.get_json() or {}
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()
    portal = data.get("portal", "").strip()
    client_ip = request.remote_addr or "127.0.0.1"
    user_agent = request.headers.get("User-Agent", "Web Browser")

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
        return jsonify({"success": False, "error": "❌ Invalid username or password!"}), 401

    # STRICT ROLE & PORTAL VALIDATION (Portal is mandatory)
    if not portal:
        return jsonify({
            "success": False,
            "error": "❌ Please select your portal section (Admin, Club Officer, or Student)."
        }), 400

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
        return jsonify({
            "success": False,
            "error": f"❌ Access Denied: Aapka account '{role_titles.get(user_role_clean, user['role'])}' hai! Aap '{portal_titles.get(portal_clean, portal)}' me login nahi kar sakte. Kripya upar se apna sahi section tab ({role_titles.get(user_role_clean, user['role'])}) select karein."
        }), 403

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
    return jsonify({"success": True, "user": user, "token": token})


@app.route("/api/auth/register", methods=["POST"])
def auth_register():
    data = request.get_json() or {}
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()
    name = data.get("name", "").strip()
    role = data.get("role", "Member")
    club_id = int(data.get("club_id")) if data.get("club_id") and str(data.get("club_id")).isdigit() else None
    client_ip = request.remote_addr or "127.0.0.1"
    user_agent = request.headers.get("User-Agent", "Web Browser")

    if not username or not password or not name:
        return jsonify({"success": False, "error": "Username, password and full name are required"}), 400

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
        return jsonify({"success": True, "user": user, "token": token, "message": "Account created successfully"}), 201
    except Exception as ex:
        if "UNIQUE constraint failed" in str(ex):
            return jsonify({"success": False, "error": "Username already taken"}), 400
        return jsonify({"success": False, "error": str(ex)}), 400


@app.route("/api/auth/logout", methods=["POST"])
def auth_logout():
    data = request.get_json() or {}
    client_ip = request.remote_addr or "127.0.0.1"
    user_agent = request.headers.get("User-Agent", "Web Browser")
    database.log_login_event(
        username=data.get("username", "Unknown"),
        role=data.get("role"),
        portal=data.get("role"),
        status="LOGOUT",
        user_id=data.get("user_id"),
        ip_address=client_ip,
        user_agent=user_agent
    )
    return jsonify({"success": True, "message": "Logged out successfully"})


@app.route("/api/auth/demo-users", methods=["GET"])
def auth_demo_users():
    demo_accounts = [
        {"username": "admin", "password": "admin123", "role": "Admin", "name": "Dr. Sarah Jenkins (Faculty Advisor)", "desc": "Full administrative access to manage all clubs, records, and exports."},
        {"username": "officer", "password": "officer123", "role": "Officer", "name": "Aarav Sharma (Coding Club Lead)", "desc": "Can log activities, take attendance roll call, and post notices."},
        {"username": "member", "password": "member123", "role": "Member", "name": "Sneha Reddy (Student Member)", "desc": "View dashboard, events calendar, notices, and personal attendance."}
    ]
    return jsonify({"success": True, "data": demo_accounts})


@app.route("/api/user/profile", methods=["GET"])
def user_profile_get():
    user_id = request.args.get("user_id")
    if not user_id or not user_id.isdigit():
        return jsonify({"success": False, "error": "user_id is required"}), 400
    user = database.get_user(int(user_id))
    if user:
        return jsonify({"success": True, "data": user})
    return jsonify({"success": False, "error": "User not found"}), 404


@app.route("/api/user/profile", methods=["PUT"])
def user_profile_put():
    data = request.get_json() or {}
    user_id = data.get("user_id")
    if not user_id:
        return jsonify({"success": False, "error": "user_id is required"}), 400
    updated_user = database.update_user_profile(int(user_id), data)
    if updated_user:
        return jsonify({"success": True, "user": updated_user, "message": "Profile updated successfully"})
    return jsonify({"success": False, "error": "User not found or update failed"}), 400


# --- CSV EXPORT & SAMPLE SEED ---

@app.route("/api/export/activities", methods=["GET"])
def export_activities():
    csv_data = database.generate_activities_csv()
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=club_activities_report.csv"}
    )


@app.route("/api/export/attendance", methods=["GET"])
def export_attendance():
    csv_data = database.generate_attendance_csv()
    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=club_attendance_report.csv"}
    )


@app.route("/api/seed", methods=["POST"])
def seed_data_endpoint():
    seed_database(force=True)
    return jsonify({"success": True, "message": "Sample dummy dataset loaded successfully"})


if __name__ == "__main__":
    database.init_db()
    clubs = database.get_clubs()
    if not clubs:
        seed_database()

    PORT = 8000
    print("\n" + "="*60)
    print(" 🚀 CLUB ACTIVITIES TRACKER (FLASK BACKEND) RUNNING!")
    print(f" 🌐 Web Dashboard: http://localhost:{PORT}")
    print(" 🗄️ Database: club_tracker.db (SQLite)")
    print("="*60 + "\n")
    app.run(host="0.0.0.0", port=PORT, debug=True)
