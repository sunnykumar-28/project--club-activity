# 🎯 Club Activities Tracker & Predictor

A modern, full-stack web application designed for colleges and universities to manage student clubs, schedule activities, track attendance roll-call, forecast event turnout using AI, generate verified certificates with cryptographic verification hashes, and maintain secure audit logs.

---

## ✨ Features

- **📊 Comprehensive Executive Dashboard**:
  - Live KPIs: Total Clubs, Registered Members, Logged Activities, and Total Volunteer Hours.
  - Category breakdown (Hackathons, Workshops, Competitions, Socials, Seminars).
  - Campus Leaderboard showcasing top active students by credited hours and event participation.
  - Recent event timeline and notices feed.

- **🔐 Strict Role-Based Access Control (RBAC)**:
  - Three distinct, dedicated sections with strict portal validation:
    - 👑 **Admin Section**: Full management of all campus clubs, rosters, database inspection, and CSV exports.
    - ⚡ **Club Officer Section**: Log club events, conduct roll-call check-ins, run turnout simulations, and broadcast notices.
    - 🎓 **Student Section**: RSVP for upcoming events, inspect verified volunteer hours, and download certificates.
  - Cross-section logins are blocked with explicit access control alerts.
  - Encrypted password authentication (SHA-256) and live session logging.

- **🔮 AI Event Turnout & Attendance Predictor**:
  - Heuristic statistical regression engine analyzing club baseline size, category draw multiplier, day-of-week impact, and duration engagement curves.
  - Live in-form attendance forecast pill during event creation.
  - Standalone Turnout Simulator with actionable strategic insights (venue seating recommendations, refreshment tips).

- **📜 Student RSVP & Verified Participation Certificates**:
  - 1-click event pre-registration (RSVP) with automatic badge display during officer roll-call.
  - Official Certificate of Participation with ornate border layout, signatures, gold seal, and tamper-evident serial hashes (`CAC-YYYYMMDD-HASH`).
  - Print-ready and PDF download support (`window.print()`).

- **🗓️ Interactive Monthly Calendar View**:
  - Switch seamlessly between Table view and Monthly Grid view.
  - Color-coded event chips categorized by activity type.
  - Interactive event detail modal with direct RSVP buttons.

- **🗄️ Database Management & Live Authentication Audit Logs**:
  - Live SQLite Database status (`club_tracker.db` file size, table counts, connection health).
  - Real-time Authentication Audit Trail (`login_logs` table) tracking logins, failed password attempts, blocked section access, and logouts with timestamps and client details.
  - 1-Click Database backup download (`club_tracker.db`).

- **👤 User Profile & Custom DP (Profile Picture)**:
  - Upload custom photos from device with automatic client-side compression.
  - Choose from 12 preset avatars (🎓, 💻, 🚀, 👑, ⚡, 🎨, 🔬, 🤖, etc.).
  - Edit personal details: Department, Roll No./Student ID, Year/Semester, Bio, Skills, LinkedIn, and GitHub profiles.

- **⚡ Zero Dependency Standard Library Backend & Flask Parity**:
  - Built-in zero-dependency Python server (`app.py`) using Python standard library.
  - Alternate full-featured Flask backend (`backend_flask.py`).

---

## 🚀 Quickstart Guide

### 1. Clone the Repository
```bash
git clone https://github.com/<YOUR_GITHUB_USERNAME>/club-activity.git
cd club-activity
```

### 2. Run the Application

**Option A: Zero-Dependency Standard Python (Recommended)**
```bash
python3 app.py
```

**Option B: Flask Backend**
```bash
pip install -r requirements.txt
python3 backend_flask.py
```

### 3. Open in Browser
Visit [http://localhost:8000](http://localhost:8000).

---

## 🔑 Default Demo Accounts

| Role | Username | Password | Access Section |
|---|---|---|---|
| **Administrator** | `admin` | `admin123` | 👑 Admin Section |
| **Club Officer** | `officer` | `officer123` | ⚡ Club Officer Section |
| **Student Member** | `student` | `student123` | 🎓 Student Section |

---

## 📁 Project Structure

```text
club-activities-tracker/
├── app.py             # Python HTTP server & REST API (Zero external dependencies)
├── backend_flask.py   # Flask REST API backend
├── database.py        # SQLite database operations, schema, AI predictor, and exporters
├── club_tracker.db    # Persistent SQLite database file
├── seed_data.py       # Sample data populator
├── requirements.txt   # Dependencies (for Flask mode)
├── README.md          # Documentation & usage guide
├── .gitignore         # Ignored files (caches, OS files)
└── static/            # Frontend SPA
    ├── index.html     # Single-Page UI layout & modal views
    ├── style.css      # Responsive CSS, calendar grid, printable certificates
    └── app.js         # Reactive UI controller & API client
```

---

## 📜 License
MIT License. Free to use for college projects, coursework, and campus deployments.
