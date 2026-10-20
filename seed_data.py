"""
Sample data seeder for Club Activities Tracker.
Populates rich, realistic dummy data for clubs, members, activities, attendance records, and announcements.
"""

import os
from database import (
    init_db, add_club, add_member, add_activity,
    record_attendance, add_announcement, create_user, get_clubs, get_connection, DB_FILE
)

def seed_database(force: bool = False):
    init_db()

    # If force=True, wipe existing tables to reseed cleanly
    if force:
        with get_connection() as conn:
            conn.execute("PRAGMA foreign_keys = OFF;")
            conn.execute("DELETE FROM attendance;")
            conn.execute("DELETE FROM activities;")
            conn.execute("DELETE FROM members;")
            conn.execute("DELETE FROM announcements;")
            conn.execute("DELETE FROM users;")
            conn.execute("DELETE FROM clubs;")
            conn.execute("PRAGMA foreign_keys = ON;")
            conn.commit()
    else:
        clubs = get_clubs()
        if clubs:
            print(f"Database already contains {len(clubs)} clubs. Use force=True to reseed.")
            return

    print("🌱 Seeding rich dummy dataset for Club Activities Tracker...")

    # =========================================================================
    # 1. CLUBS DUMMY DATA (6 Distinct Clubs)
    # =========================================================================
    c_coding = add_club(
        name="Coding & Open Source Club",
        category="Technology",
        description="Fosters hands-on software development, competitive programming, open-source projects, and hackathons.",
        lead_name="Aarav Sharma"
    )

    c_robotics = add_club(
        name="Robotics & AI Society",
        category="Engineering",
        description="Focuses on autonomous robotics, IoT hardware prototypes, drones, and computer vision algorithms.",
        lead_name="Pooja Verma"
    )

    c_eco = add_club(
        name="Eco Action & Green Campus Club",
        category="Community Service",
        description="Champions sustainability, carbon-neutral drives, campus biodiversity gardening, and e-waste recycling.",
        lead_name="Rohan Mukherjee"
    )

    c_debate = add_club(
        name="Debate & Model United Nations (MUN)",
        category="Academic",
        description="Promotes policy debate, geopolitical research, crisis simulations, and parliamentary public speaking.",
        lead_name="Ananya Iyer"
    )

    c_media = add_club(
        name="ShutterBug Media & Photography",
        category="Arts & Music",
        description="Covers university event photojournalism, cinematic videography, lighting workshops, and digital editing.",
        lead_name="Kabir Mehta"
    )

    c_cultural = add_club(
        name="Aura Cultural & Music Society",
        category="Arts & Music",
        description="A collective of instrumentalists, vocalists, and performing artists organizing annual cultural festivals.",
        lead_name="Simran Kaur"
    )

    # =========================================================================
    # 2. MEMBERS DUMMY DATA (35+ Members with varying roles)
    # =========================================================================
    # Coding Club Members
    m_aarav = add_member(c_coding, "Aarav Sharma", "aarav.sharma@campus.edu", "President", "2026-01-05")
    m_riya = add_member(c_coding, "Riya Patel", "riya.patel@campus.edu", "Vice President", "2026-01-10")
    m_tushar = add_member(c_coding, "Tushar Gupta", "tushar.g@campus.edu", "Tech Lead", "2026-01-15")
    m_sneha = add_member(c_coding, "Sneha Reddy", "sneha.r@campus.edu", "Member", "2026-02-01")
    m_vikram = add_member(c_coding, "Vikram Joshi", "vikram.j@campus.edu", "Member", "2026-02-15")
    m_neha = add_member(c_coding, "Neha Saxena", "neha.s@campus.edu", "Member", "2026-03-01")

    # Robotics Club Members
    m_pooja = add_member(c_robotics, "Pooja Verma", "pooja.verma@campus.edu", "President", "2026-01-08")
    m_karan = add_member(c_robotics, "Karan Malhotra", "karan.m@campus.edu", "Hardware Lead", "2026-01-18")
    m_dev = add_member(c_robotics, "Dev Singhania", "dev.s@campus.edu", "Secretary", "2026-02-05")
    m_tanvi = add_member(c_robotics, "Tanvi Chawla", "tanvi.c@campus.edu", "Member", "2026-02-20")
    m_aditya = add_member(c_robotics, "Aditya Rao", "aditya.r@campus.edu", "Member", "2026-03-10")

    # Eco Club Members
    m_rohan = add_member(c_eco, "Rohan Mukherjee", "rohan.m@campus.edu", "President", "2026-01-12")
    m_meera = add_member(c_eco, "Meera Nambiar", "meera.n@campus.edu", "Vice President", "2026-01-20")
    m_arjun = add_member(c_eco, "Arjun Sen", "arjun.sen@campus.edu", "Volunteer", "2026-02-08")
    m_ishita = add_member(c_eco, "Ishita Roy", "ishita.roy@campus.edu", "Volunteer", "2026-02-18")
    m_kavita = add_member(c_eco, "Kavita Das", "kavita.das@campus.edu", "Member", "2026-03-05")

    # Debate Club Members
    m_ananya = add_member(c_debate, "Ananya Iyer", "ananya.iyer@campus.edu", "President", "2026-01-07")
    m_siddharth = add_member(c_debate, "Siddharth Menon", "sid.menon@campus.edu", "Secretary", "2026-01-25")
    m_pallavi = add_member(c_debate, "Pallavi Kulkarni", "pallavi.k@campus.edu", "Officer", "2026-02-12")
    m_rahul = add_member(c_debate, "Rahul Nair", "rahul.nair@campus.edu", "Member", "2026-02-22")
    m_zoya = add_member(c_debate, "Zoya Akhtar", "zoya.a@campus.edu", "Member", "2026-03-12")

    # Media Club Members
    m_kabir = add_member(c_media, "Kabir Mehta", "kabir.m@campus.edu", "President", "2026-01-14")
    m_sakshi = add_member(c_media, "Sakshi Kapoor", "sakshi.k@campus.edu", "Treasurer", "2026-01-28")
    m_manish = add_member(c_media, "Manish Jain", "manish.j@campus.edu", "Editor", "2026-02-14")
    m_shreya = add_member(c_media, "Shreya Ghosh", "shreya.g@campus.edu", "Member", "2026-03-02")

    # Cultural & Music Members
    m_simran = add_member(c_cultural, "Simran Kaur", "simran.k@campus.edu", "President", "2026-01-09")
    m_aman = add_member(c_cultural, "Aman Gill", "aman.gill@campus.edu", "Vice President", "2026-01-22")
    m_tanya = add_member(c_cultural, "Tanya Batra", "tanya.b@campus.edu", "Vocal Lead", "2026-02-10")
    m_harsh = add_member(c_cultural, "Harsh Agarwal", "harsh.a@campus.edu", "Instrumentalist", "2026-02-25")
    m_payal = add_member(c_cultural, "Payal Sethi", "payal.s@campus.edu", "Member", "2026-03-15")

    # =========================================================================
    # 3. ACTIVITIES DUMMY DATA (20+ Activities across categories & statuses)
    # =========================================================================
    # Coding Club Activities
    act1 = add_activity(c_coding, "Modern Fullstack Web Architecture & APIs", "Workshop", "2026-08-20", 3.0, "CS Seminar Hall 1", "Completed", "Interactive hands-on session on building RESTful microservices and frontend SPAs.")
    act2 = add_activity(c_coding, "HackNation 24-Hour Campus Hackathon", "Competition", "2026-09-12", 8.0, "Central Innovation Center", "Completed", "Annual overnight hackathon focusing on AI-assisted healthcare and student accessibility tools.")
    act3 = add_activity(c_coding, "Git & Open-Source Pull Request Sprint", "Workshop", "2026-10-04", 2.5, "Lab 204", "Completed", "Practical mentorship on resolving GitHub issues, branching, and licensing.")
    act4 = add_activity(c_coding, "Algorithm Design & Competitive Coding League", "Competition", "2026-10-22", 3.0, "Lab 301", "Planned", "Speed programming contest on dynamic programming and graph theory algorithms.")
    act5 = add_activity(c_coding, "Cloud Deployment with Docker & Kubernetes", "Workshop", "2026-11-05", 2.5, "Virtual Zoom & Lab 102", "Planned", "Containerizing fullstack applications and deploying to cloud infrastructure.")

    # Robotics Club Activities
    act6 = add_activity(c_robotics, "Autonomous Micro-Rover Assembly & Soldering", "Workshop", "2026-08-28", 4.0, "Makerspace Bay 3", "Completed", "Hardware fabrication, motor chassis wiring, and soldering sensor shields.")
    act7 = add_activity(c_robotics, "Computer Vision with YOLOv8 & OpenCV", "Workshop", "2026-09-25", 3.5, "Robotics Lab", "Completed", "Object tracking and live camera stream classification on Raspberry Pi.")
    act8 = add_activity(c_robotics, "Intra-College RoboWars & Line Follower Clash", "Competition", "2026-10-18", 5.0, "Indoor Sports Arena", "Ongoing", "High-stakes combat robotics and obstacle race championship.")
    act9 = add_activity(c_robotics, "Drone Dynamics & Flight Controller Calibration", "Workshop", "2026-11-12", 3.0, "Open Football Ground", "Planned", "Tuning PID controllers and test flights for quadcopters.")

    # Eco Club Activities
    act10 = add_activity(c_eco, "Campus Green Canopy Tree Plantation Drive", "Volunteer/Service", "2026-08-15", 5.0, "Botanical Reserve West", "Completed", "Planted 120 indigenous trees and built bamboo protective tree guards.")
    act11 = add_activity(c_eco, "E-Waste & Battery Neutralization Campaign", "Volunteer/Service", "2026-09-18", 4.0, "Student Union Atrium", "Completed", "Gathered over 350 kg of electronic scrap for certified zero-landfill recycling.")
    act12 = add_activity(c_eco, "Rooftop Solar & Carbon Footprint Audit", "Meeting", "2026-10-10", 2.0, "Conference Room B", "Completed", "Analyzed campus building energy dissipation data and formulated recommendations.")
    act13 = add_activity(c_eco, "Organic Waste Composting Workshop", "Workshop", "2026-10-28", 2.5, "Campus Canteen Backlot", "Planned", "Teaching vermicomposting methods for cafeteria organic food waste.")

    # Debate Club Activities
    act14 = add_activity(c_debate, "National Parliamentary Debate Championship", "Competition", "2026-09-05", 6.0, "Auditorium Hall 2", "Completed", "Oxford format debates on international climate treaties and AI governance.")
    act15 = add_activity(c_debate, "Crisis Simulation: Global Energy Transition", "Meeting", "2026-09-30", 3.0, "Law Department Moot Court", "Completed", "Multi-nation delegate roleplay addressing international maritime energy blockades.")
    act16 = add_activity(c_debate, "Freshers Public Speaking & Rhetoric Boot Camp", "Workshop", "2026-10-25", 2.5, "Hall 105", "Planned", "Vocal modulation, cross-examination techniques, and persuasive rebuttals.")

    # Media Club Activities
    act17 = add_activity(c_media, "Golden Hour Campus Architecture Photo Walk", "Workshop", "2026-09-14", 3.0, "Main Heritage Campus Quad", "Completed", "Hands-on camera exposure triangle mastery, composition, and framing.")
    act18 = add_activity(c_media, "Color Grading & Cinematic Video Editing", "Workshop", "2026-10-08", 3.0, "Multimedia Studio 4", "Completed", "DaVinci Resolve color wheels, audio sweetening, and storytelling.")
    act19 = add_activity(c_media, "Annual Visual Arts & Photography Showcase", "Social", "2026-11-15", 4.0, "Library Art Gallery", "Planned", "Public exhibition showcasing 80 curated student photo prints.")

    # Cultural & Music Activities
    act20 = add_activity(c_cultural, "Monsoon Acoustic Jam & Open Mic Evening", "Social", "2026-08-30", 3.5, "Open Amphitheater", "Completed", "Unplugged vocal solos, band duets, and poetry performances under string lights.")
    act21 = add_activity(c_cultural, "Inter-College Battle of the Bands Preliminary", "Competition", "2026-10-15", 5.0, "Main Auditorium", "Ongoing", "Rock, indie, and fusion bands competing for regional festival qualifiers.")
    act22 = add_activity(c_cultural, "Sound Engineering & Live Audio Mixing", "Workshop", "2026-10-29", 3.0, "Stage Audio Control Booth", "Planned", "Operating digital audio consoles, condenser microphones, and monitor mixes.")

    # =========================================================================
    # 4. ATTENDANCE DUMMY DATA (60+ Participation & Volunteer Hours)
    # =========================================================================
    # Coding Act1
    record_attendance(act1, m_aarav, "Present", 3.0, "Session Speaker & Host")
    record_attendance(act1, m_riya, "Present", 3.0, "Co-speaker on FastAPI")
    record_attendance(act1, m_tushar, "Present", 3.0, "Live code demonstration")
    record_attendance(act1, m_sneha, "Present", 3.0, "Completed workshop lab tasks")
    record_attendance(act1, m_vikram, "Present", 3.0, "Assisted lab setup")
    record_attendance(act1, m_neha, "Absent", 0.0, "Medical leave")

    # Coding Act2 (Hackathon)
    record_attendance(act2, m_aarav, "Present", 8.0, "Lead Organizer & Judge liaison")
    record_attendance(act2, m_riya, "Present", 8.0, "Logistics & Sponsor manager")
    record_attendance(act2, m_tushar, "Present", 8.0, "Mentor room manager")
    record_attendance(act2, m_sneha, "Present", 8.0, "Competitor - 1st Runner Up")
    record_attendance(act2, m_vikram, "Present", 8.0, "Competitor team lead")
    record_attendance(act2, m_neha, "Present", 8.0, "Competitor")

    # Coding Act3 (Git Sprint)
    record_attendance(act3, m_aarav, "Present", 2.5, "Reviewed PR submissions")
    record_attendance(act3, m_riya, "Present", 2.5, "Conducted git merge conflict demo")
    record_attendance(act3, m_sneha, "Present", 2.5, "Authored docs PR")

    # Robotics Act6 (Rover Assembly)
    record_attendance(act6, m_pooja, "Present", 4.0, "Hardware team lead")
    record_attendance(act6, m_karan, "Present", 4.0, "Soldering instructor")
    record_attendance(act6, m_dev, "Present", 4.0, "Inventory recording")
    record_attendance(act6, m_tanvi, "Present", 4.0, "Chassis mechanical mounting")
    record_attendance(act6, m_aditya, "Present", 4.0, "Power supply calibration")

    # Robotics Act7 (YOLO Workshop)
    record_attendance(act7, m_pooja, "Present", 3.5, "Introduction to neural nets")
    record_attendance(act7, m_karan, "Present", 3.5, "Trained dataset demo")
    record_attendance(act7, m_dev, "Present", 3.5, "Lab support")
    record_attendance(act7, m_tanvi, "Present", 3.5, "Model inference testing")

    # Eco Act10 (Tree Plantation - High Volunteer Hours)
    record_attendance(act10, m_rohan, "Present", 5.0, "Coordinated horticulture team")
    record_attendance(act10, m_meera, "Present", 5.0, "Sapling inventory & tags")
    record_attendance(act10, m_arjun, "Present", 5.0, "Soil preparation & deep trench digging")
    record_attendance(act10, m_ishita, "Present", 5.0, "Tree planting & mulching")
    record_attendance(act10, m_kavita, "Present", 5.0, "Water irrigation setup")

    # Eco Act11 (E-Waste Drive)
    record_attendance(act11, m_rohan, "Present", 4.0, "Event director")
    record_attendance(act11, m_meera, "Present", 4.0, "Certificate distribution")
    record_attendance(act11, m_arjun, "Present", 4.0, "Scrap sorting and weigh-in")
    record_attendance(act11, m_ishita, "Present", 4.0, "Collection counter manager")

    # Eco Act12 (Solar Audit)
    record_attendance(act12, m_rohan, "Present", 2.0, "Audit presenter")
    record_attendance(act12, m_meera, "Present", 2.0, "Data logger")
    record_attendance(act12, m_arjun, "Present", 2.0, "Photovoltaic panel inspection")

    # Debate Act14 (Championship)
    record_attendance(act14, m_ananya, "Present", 6.0, "Finals Adjudicator")
    record_attendance(act14, m_siddharth, "Present", 6.0, "Best Speaker Awardee")
    record_attendance(act14, m_pallavi, "Present", 6.0, "Government Whip speaker")
    record_attendance(act14, m_rahul, "Present", 6.0, "Opposition Deputy Leader")
    record_attendance(act14, m_zoya, "Present", 6.0, "Research & motion framer")

    # Debate Act15 (Crisis Sim)
    record_attendance(act15, m_ananya, "Present", 3.0, "Crisis Director")
    record_attendance(act15, m_siddharth, "Present", 3.0, "Delegate of Germany")
    record_attendance(act15, m_pallavi, "Present", 3.0, "Delegate of Japan")

    # Media Act17 (Photo Walk)
    record_attendance(act17, m_kabir, "Present", 3.0, "Guided architectural walk")
    record_attendance(act17, m_sakshi, "Present", 3.0, "Organized lens gear rental")
    record_attendance(act17, m_manish, "Present", 3.0, "Portfolio review mentor")
    record_attendance(act17, m_shreya, "Present", 3.0, "Submitted 12 exhibition photos")

    # Cultural Act20 (Acoustic Jam)
    record_attendance(act20, m_simran, "Present", 3.5, "Stage host & lead vocals")
    record_attendance(act20, m_aman, "Present", 3.5, "Acoustic guitar & arrangements")
    record_attendance(act20, m_tanya, "Present", 3.5, "Duet vocal performance")
    record_attendance(act20, m_harsh, "Present", 3.5, "Cajon & percussion accompaniment")
    record_attendance(act20, m_payal, "Present", 3.5, "Event lighting & stage decor")

    # =========================================================================
    # 5. ANNOUNCEMENTS DUMMY DATA (8 Realistic Notices)
    # =========================================================================
    add_announcement(c_coding, "HackNation Winners Felicitation Ceremony", "Join us this Friday at 4 PM in Seminar Hall 1 for certificates, cash prizes, and sponsor networking.", "Important", "2026-10-10")
    add_announcement(c_coding, "Call for Mentors: Open Source Sprint", "Looking for 3 senior students with React & Python experience to mentor newcomers next week.", "Normal", "2026-10-12")

    add_announcement(c_robotics, "RoboWars Arena Setup Volunteers Needed", "All members are requested to report to the Sports Arena on Thursday 5 PM for track testing.", "Urgent", "2026-10-11")
    add_announcement(c_robotics, "Drone Lab Parts Arrival", "The new LiPo batteries and flight controllers have arrived at Makerspace Bay 3.", "Normal", "2026-10-09")

    add_announcement(c_eco, "Campus Green Audit Report Released", "Our solar recommendations were approved by the University Senate! Read the summary on the club drive.", "Important", "2026-10-11")
    add_announcement(c_eco, "Tree Plantation Volunteer Certificates Ready", "All 15 participants can download their verified volunteer hours report via the dashboard.", "Normal", "2026-09-22")

    add_announcement(c_debate, "Registrations Open for Intra-MUN 2026", "Committee allocations: UNSC, UNEP, and Lok Sabha. Early-bird registration closes on Oct 20.", "Important", "2026-10-08")

    add_announcement(c_cultural, "Final Auditions for Annual College Fest Band", "Drummers and keyboard players wanted for the main stage rock band. Auditions this Saturday.", "Urgent", "2026-10-12")

    # =========================================================================
    # 6. DEMO USERS (Authentication Accounts)
    # =========================================================================
    create_user(
        username="admin",
        password="admin123",
        name="Dr. Sarah Jenkins",
        role="Admin"
    )

    create_user(
        username="officer",
        password="officer123",
        name="Aarav Sharma",
        role="Officer",
        club_id=c_coding
    )

    create_user(
        username="member",
        password="member123",
        name="Sneha Reddy",
        role="Member",
        club_id=c_coding
    )

    create_user(
        username="student",
        password="student123",
        name="Sneha Reddy",
        role="Member",
        club_id=c_coding
    )

    print(f"✅ Successfully seeded database with:")
    print("   • 6 Active Clubs")
    print("   • 31 Registered Members")
    print("   • 22 Club Activities")
    print("   • 58 Attendance & Volunteer Hour Records")
    print("   • 8 Club Announcements")
    print("   • 3 Demo Authentication Accounts (admin, officer, member)")

if __name__ == "__main__":
    import sys
    force_reseed = "--force" in sys.argv or "-f" in sys.argv
    seed_database(force=force_reseed)
