/**
 * Club Activities Tracker - Client Application
 */

const API_BASE = "";

let currentTab = "dashboard";
let clubsData = [];
let activitiesData = [];
let membersData = [];
let currentAttendanceActivityId = null;
let currentAttendanceRecords = [];
let currentUser = null;
let selectedSection = "Admin"; // 'Admin', 'Officer', or 'Member'
let activitiesViewMode = "table"; // 'table' or 'calendar'
let currentCalYear = 2026;
let currentCalMonth = 9; // 0-indexed (9 = October)
let studentRsvps = []; // array of activity_ids

// Initialize on page load
document.addEventListener("DOMContentLoaded", () => {
  // Set default date for new activity input to today
  const today = new Date().toISOString().split("T")[0];
  const dateInput = document.getElementById("act-date");
  if (dateInput) dateInput.value = today;

  // Live prediction listeners on new activity modal fields
  ["act-club", "act-category", "act-duration", "act-date"].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.addEventListener("change", updateLiveActivityPrediction);
    if (el && id === "act-duration") el.addEventListener("input", updateLiveActivityPrediction);
  });

  switchSection("Admin");
  checkAuth();
});

// --- AUTHENTICATION & PORTAL SECTION CONTROLLER ---
function switchSection(section) {
  selectedSection = section; // 'Admin', 'Officer', 'Member'

  // Update tabs active state
  ["Admin", "Officer", "Member"].forEach(sec => {
    const btn = document.getElementById(`sec-btn-${sec.toLowerCase()}`);
    if (btn) {
      if (sec === section) btn.classList.add("active");
      else btn.classList.remove("active");
    }
  });

  // Update Section Info Box
  const banner = document.getElementById("section-info-banner");
  const title = document.getElementById("section-info-title");
  const desc = document.getElementById("section-info-desc");
  const submitBtn = document.getElementById("login-submit-btn");
  const userInput = document.getElementById("login-username");
  const passInput = document.getElementById("login-password");
  const hintUser = document.getElementById("login-hint-username");
  const hintPass = document.getElementById("login-hint-password");
  const regRoleSelect = document.getElementById("reg-role");
  const demoTitle = document.getElementById("demo-box-title");
  const demoContainer = document.getElementById("demo-buttons-container");
  const errorBox = document.getElementById("login-error");

  if (errorBox) errorBox.style.display = "none";
  if (regRoleSelect) regRoleSelect.value = section;

  if (section === "Admin") {
    if (banner) {
      banner.className = "section-info-banner banner-admin";
      title.textContent = "👑 Administrator Section";
      desc.textContent = "Only Faculty Advisors & System Admins can log in here. (Students & Officers are blocked).";
    }
    if (submitBtn) submitBtn.textContent = "🔑 Sign In to Admin Section →";
    if (userInput) {
      userInput.value = "admin";
      userInput.placeholder = "e.g. admin";
    }
    if (passInput) {
      passInput.value = "admin123";
      passInput.placeholder = "admin123 (or admin)";
    }
    if (hintUser) hintUser.textContent = "Valid: admin";
    if (hintPass) hintPass.textContent = "Valid: admin123 or admin";
    if (demoTitle) demoTitle.textContent = "⚡ 1-Click Demo Credentials for Admin:";
    if (demoContainer) {
      demoContainer.innerHTML = `
        <button type="button" class="demo-btn" onclick="quickLogin('admin', 'admin123')">
          <span class="demo-role">👑 Faculty / Admin Demo</span>
          <span class="demo-cred">admin / admin123</span>
        </button>
      `;
    }
  } else if (section === "Officer") {
    if (banner) {
      banner.className = "section-info-banner banner-officer";
      title.textContent = "⚡ Club Officer Section";
      desc.textContent = "Only authorized Club Officers and Event Leads can log in here to manage their club.";
    }
    if (submitBtn) submitBtn.textContent = "🔑 Sign In to Officer Section →";
    if (userInput) {
      userInput.value = "officer";
      userInput.placeholder = "e.g. officer";
    }
    if (passInput) {
      passInput.value = "officer123";
      passInput.placeholder = "officer123 (or officer)";
    }
    if (hintUser) hintUser.textContent = "Valid: officer";
    if (hintPass) hintPass.textContent = "Valid: officer123 or officer";
    if (demoTitle) demoTitle.textContent = "⚡ 1-Click Demo Credentials for Officer:";
    if (demoContainer) {
      demoContainer.innerHTML = `
        <button type="button" class="demo-btn" onclick="quickLogin('officer', 'officer123')">
          <span class="demo-role">⚡ Club Officer Demo (Coding Club)</span>
          <span class="demo-cred">officer / officer123</span>
        </button>
      `;
    }
  } else if (section === "Member") {
    if (banner) {
      banner.className = "section-info-banner banner-member";
      title.textContent = "🎓 Student Member Section";
      desc.textContent = "Only registered Student Members can log in here to view activities, attendance & hours.";
    }
    if (submitBtn) submitBtn.textContent = "🔑 Sign In to Student Section →";
    if (userInput) {
      userInput.value = "student";
      userInput.placeholder = "student or member";
    }
    if (passInput) {
      passInput.value = "student123";
      passInput.placeholder = "student123 or member123";
    }
    if (hintUser) hintUser.textContent = "Valid: student or member";
    if (hintPass) hintPass.textContent = "Valid: student123 or member123";
    if (demoTitle) demoTitle.textContent = "⚡ 1-Click Demo Credentials for Student:";
    if (demoContainer) {
      demoContainer.innerHTML = `
        <button type="button" class="demo-btn" onclick="quickLogin('student', 'student123')">
          <span class="demo-role">🎓 Student Member Demo (Sneha Reddy)</span>
          <span class="demo-cred">student / student123</span>
        </button>
      `;
    }
  }
}

function togglePasswordVisibility() {
  const pwdInput = document.getElementById("login-password");
  const btn = document.getElementById("btn-toggle-pwd");
  if (!pwdInput) return;
  if (pwdInput.type === "password") {
    pwdInput.type = "text";
    if (btn) btn.textContent = "🔒";
  } else {
    pwdInput.type = "password";
    if (btn) btn.textContent = "👁️";
  }
}

function checkAuth() {
  const savedUser = localStorage.getItem("club_tracker_user");
  if (savedUser) {
    try {
      currentUser = JSON.parse(savedUser);
      showApp(false);
    } catch (e) {
      localStorage.removeItem("club_tracker_user");
      showLogin();
    }
  } else {
    showLogin();
  }
}

function showLogin() {
  document.getElementById("login-view").style.display = "flex";
  document.getElementById("app-view").style.display = "none";
  switchAuthMode('login');
  switchSection(selectedSection || "Admin");
}

function browseAsGuest() {
  currentUser = null;
  localStorage.removeItem("club_tracker_user");
  showApp(true);
  showToast("Browsing in guest mode. Sign in to edit or log events.");
}

function showApp(isGuest = false) {
  document.getElementById("login-view").style.display = "none";
  document.getElementById("app-view").style.display = "block";

  const userBadge = document.getElementById("nav-user-badge");
  const logoutBtn = document.getElementById("btn-logout");
  const loginGuestBtn = document.getElementById("btn-login-guest");
  const quickLogBtn = document.getElementById("btn-quick-log");
  const indicator = document.getElementById("nav-section-indicator");
  const studentBanner = document.getElementById("student-welcome-banner");
  const studentNameDisplay = document.getElementById("student-name-display");

  const addActBtn = document.getElementById("btn-add-activity-main");
  const addMemBtn = document.getElementById("btn-add-member-main");
  const addClubBtn = document.getElementById("btn-add-club-main");
  const reloadSampleBtn = document.getElementById("btn-reload-sample");
  const postNoticeBtn = document.getElementById("btn-post-notice");

  if (isGuest || !currentUser) {
    if (userBadge) userBadge.style.display = "none";
    if (logoutBtn) logoutBtn.style.display = "none";
    if (loginGuestBtn) loginGuestBtn.style.display = "flex";
    if (quickLogBtn) quickLogBtn.style.display = "none";
    if (addActBtn) addActBtn.style.display = "none";
    if (addMemBtn) addMemBtn.style.display = "none";
    if (addClubBtn) addClubBtn.style.display = "none";
    if (reloadSampleBtn) reloadSampleBtn.style.display = "none";
    if (postNoticeBtn) postNoticeBtn.style.display = "none";
    if (indicator) {
      indicator.className = "nav-section-indicator tag-guest";
      indicator.textContent = "👀 Guest View (Read Only)";
    }
    if (studentBanner) studentBanner.style.display = "none";
  } else {
    if (userBadge) userBadge.style.display = "flex";
    if (logoutBtn) logoutBtn.style.display = "flex";
    if (loginGuestBtn) loginGuestBtn.style.display = "none";
    updateUserUI();

    // Section Badge in Navbar & Strict Permissions
    if (currentUser.role === "Admin") {
      if (indicator) {
        indicator.className = "nav-section-indicator tag-admin";
        indicator.textContent = "👑 Admin Section";
      }
      if (quickLogBtn) quickLogBtn.style.display = "inline-flex";
      if (addActBtn) addActBtn.style.display = "inline-flex";
      if (addMemBtn) addMemBtn.style.display = "inline-flex";
      if (addClubBtn) addClubBtn.style.display = "inline-flex";
      if (reloadSampleBtn) reloadSampleBtn.style.display = "inline-flex";
      if (postNoticeBtn) postNoticeBtn.style.display = "inline-flex";
      if (studentBanner) studentBanner.style.display = "none";
    } else if (currentUser.role === "Officer") {
      if (indicator) {
        indicator.className = "nav-section-indicator tag-officer";
        indicator.textContent = `⚡ Officer: ${currentUser.club_name || 'Club Lead'}`;
      }
      if (quickLogBtn) quickLogBtn.style.display = "inline-flex";
      if (addActBtn) addActBtn.style.display = "inline-flex";
      if (addMemBtn) addMemBtn.style.display = "inline-flex";
      if (addClubBtn) addClubBtn.style.display = "none";
      if (reloadSampleBtn) reloadSampleBtn.style.display = "none";
      if (postNoticeBtn) postNoticeBtn.style.display = "inline-flex";
      if (studentBanner) studentBanner.style.display = "none";
    } else if (currentUser.role === "Member") {
      if (indicator) {
        indicator.className = "nav-section-indicator tag-student";
        indicator.textContent = "🎓 Student Section";
      }
      // Strictly Read-Only for students
      if (quickLogBtn) quickLogBtn.style.display = "none";
      if (addActBtn) addActBtn.style.display = "none";
      if (addMemBtn) addMemBtn.style.display = "none";
      if (addClubBtn) addClubBtn.style.display = "none";
      if (reloadSampleBtn) reloadSampleBtn.style.display = "none";
      if (postNoticeBtn) postNoticeBtn.style.display = "none";
      if (studentBanner) {
        studentBanner.style.display = "block";
        if (studentNameDisplay) studentNameDisplay.textContent = currentUser.name || "Student";
      }
    }
  }

  loadInitialData();
}

function updateUserUI() {
  if (!currentUser) return;
  const initials = (currentUser.name || currentUser.username || "U")
    .split(" ")
    .map(w => w[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();

  const avatarEl = document.getElementById("nav-user-avatar");
  if (avatarEl) {
    if (currentUser.avatar && (currentUser.avatar.startsWith("data:image") || currentUser.avatar.startsWith("http"))) {
      avatarEl.textContent = "";
      avatarEl.style.backgroundImage = `url('${currentUser.avatar}')`;
    } else if (currentUser.avatar) {
      avatarEl.textContent = currentUser.avatar;
      avatarEl.style.backgroundImage = "none";
    } else {
      avatarEl.textContent = initials;
      avatarEl.style.backgroundImage = "none";
    }
  }

  // Also update student banner avatar if present
  const studentBannerAvatar = document.getElementById("student-banner-avatar");
  if (studentBannerAvatar) {
    if (currentUser.avatar && (currentUser.avatar.startsWith("data:image") || currentUser.avatar.startsWith("http"))) {
      studentBannerAvatar.textContent = "";
      studentBannerAvatar.style.backgroundImage = `url('${currentUser.avatar}')`;
    } else if (currentUser.avatar) {
      studentBannerAvatar.textContent = currentUser.avatar;
      studentBannerAvatar.style.backgroundImage = "none";
    } else {
      studentBannerAvatar.textContent = "🎓";
      studentBannerAvatar.style.backgroundImage = "none";
    }
  }

  document.getElementById("nav-user-name").textContent = currentUser.name || currentUser.username;
  document.getElementById("nav-user-role").textContent = currentUser.role || "Member";
}

function switchAuthMode(mode) {
  const loginForm = document.getElementById("login-form");
  const regForm = document.getElementById("register-form");
  const demoBox = document.getElementById("demo-logins-box");
  const toggleLogin = document.getElementById("auth-toggle-login");
  const toggleReg = document.getElementById("auth-toggle-register");
  const errorBox = document.getElementById("login-error");

  if (errorBox) errorBox.style.display = "none";

  if (mode === "register") {
    loginForm.style.display = "none";
    regForm.style.display = "block";
    demoBox.style.display = "none";
    toggleLogin.classList.remove("active");
    toggleReg.classList.add("active");
  } else {
    loginForm.style.display = "block";
    regForm.style.display = "none";
    demoBox.style.display = "block";
    toggleLogin.classList.add("active");
    toggleReg.classList.remove("active");
  }
}

async function handleLogin(event) {
  if (event) event.preventDefault();
  const username = (document.getElementById("login-username").value || "").trim();
  const password = (document.getElementById("login-password").value || "").trim();
  const errorBox = document.getElementById("login-error");
  const submitBtn = document.getElementById("login-submit-btn");

  if (errorBox) errorBox.style.display = "none";

  if (!username || !password) {
    if (errorBox) {
      errorBox.textContent = "⚠️ Please enter both username and password.";
      errorBox.style.display = "flex";
    }
    return;
  }

  if (submitBtn) submitBtn.textContent = "Verifying...";

  try {
    const res = await fetch(`${API_BASE}/api/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, password, portal: selectedSection })
    });
    const json = await res.json();

    if (json.success && json.user) {
      currentUser = json.user;
      localStorage.setItem("club_tracker_user", JSON.stringify(currentUser));
      if (submitBtn) submitBtn.textContent = `🔑 Sign In to ${selectedSection} Section →`;
      showToast(`Welcome back, ${currentUser.name}!`);
      showApp(false);
    } else {
      if (submitBtn) submitBtn.textContent = `🔑 Sign In to ${selectedSection} Section →`;
      if (errorBox) {
        errorBox.textContent = json.error || "Invalid username or password";
        errorBox.style.display = "flex";
      }
    }
  } catch (err) {
    if (submitBtn) submitBtn.textContent = `🔑 Sign In to ${selectedSection} Section →`;
    if (errorBox) {
      errorBox.textContent = "⚠️ Could not connect to authentication server.";
      errorBox.style.display = "flex";
    }
  }
}

async function handleRegister(event) {
  if (event) event.preventDefault();
  const name = document.getElementById("reg-name").value.trim();
  const username = document.getElementById("reg-username").value.trim();
  const password = document.getElementById("reg-password").value;
  const role = document.getElementById("reg-role").value;
  const errorBox = document.getElementById("login-error");
  const submitBtn = document.getElementById("reg-submit-btn");

  if (errorBox) errorBox.style.display = "none";
  if (submitBtn) submitBtn.textContent = "Creating Account...";

  try {
    const res = await fetch(`${API_BASE}/api/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, username, password, role })
    });
    const json = await res.json();

    if (json.success && json.user) {
      currentUser = json.user;
      localStorage.setItem("club_tracker_user", JSON.stringify(currentUser));
      if (submitBtn) submitBtn.textContent = "✨ Create Account & Sign In →";
      showToast(`Account created! Welcome, ${currentUser.name}!`);
      showApp(false);
    } else {
      if (submitBtn) submitBtn.textContent = "✨ Create Account & Sign In →";
      if (errorBox) {
        errorBox.textContent = `⚠️ ${json.error || "Failed to create account"}`;
        errorBox.style.display = "flex";
      }
    }
  } catch (err) {
    if (submitBtn) submitBtn.textContent = "✨ Create Account & Sign In →";
    if (errorBox) {
      errorBox.textContent = "⚠️ Server error creating account.";
      errorBox.style.display = "flex";
    }
  }
}

function quickLogin(username, password) {
  document.getElementById("login-username").value = username;
  document.getElementById("login-password").value = password;
  handleLogin();
}

async function logout() {
  try {
    const user = currentUser;
    await fetch(`${API_BASE}/api/auth/logout`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_id: user ? user.id : null,
        username: user ? user.username : "Unknown",
        role: user ? user.role : null
      })
    });
  } catch (e) {
    // ignore
  }
  currentUser = null;
  localStorage.removeItem("club_tracker_user");
  showToast("You have been signed out successfully.");
  showLogin();
}

async function loadInitialData() {
  await Promise.all([
    fetchClubs(),
    fetchActivities(),
    fetchMembers(),
    loadDashboardStats(),
    fetchStudentRsvps()
  ]);
  populateClubDropdowns();
}

// --- TAB SWITCHING ---
function switchTab(tabId) {
  currentTab = tabId;

  // Toggle active tab buttons
  document.querySelectorAll(".nav-btn").forEach(btn => btn.classList.remove("active"));
  const activeBtn = document.getElementById(`tab-btn-${tabId}`);
  if (activeBtn) activeBtn.classList.add("active");

  // Toggle tab contents
  document.querySelectorAll(".tab-pane").forEach(pane => pane.classList.remove("active"));
  const activePane = document.getElementById(`tab-${tabId}`);
  if (activePane) activePane.classList.add("active");

  // Refresh tab-specific data
  if (tabId === "dashboard") loadDashboardStats();
  if (tabId === "activities") {
    fetchActivities();
    if (activitiesViewMode === "calendar") renderCalendar();
  }
  if (tabId === "members") fetchMembers();
  if (tabId === "clubs") fetchClubs();
  if (tabId === "database") fetchDatabaseOverview();
}

// --- TOAST NOTIFICATIONS ---
function showToast(message, type = "success") {
  const container = document.getElementById("toast-container");
  const toast = document.createElement("div");
  toast.className = `toast ${type}`;
  toast.innerHTML = `<span>${type === 'success' ? '✅' : '⚠️'}</span> <span>${message}</span>`;
  container.appendChild(toast);
  setTimeout(() => {
    toast.remove();
  }, 3500);
}

// --- POPULATE CLUB DROPDOWNS ---
function populateClubDropdowns() {
  const clubSelects = [
    document.getElementById("activity-club-filter"),
    document.getElementById("member-club-filter"),
    document.getElementById("act-club"),
    document.getElementById("member-club"),
    document.getElementById("ann-club")
  ];

  clubSelects.forEach(select => {
    if (!select) return;
    const isFilter = select.id.includes("filter");
    const currentValue = select.value;
    select.innerHTML = isFilter ? '<option value="">All Clubs</option>' : '';

    clubsData.forEach(club => {
      const opt = document.createElement("option");
      opt.value = club.id;
      opt.textContent = club.name;
      select.appendChild(opt);
    });

    if (currentValue) select.value = currentValue;
  });
}

// --- API DATA CALLS ---
async function fetchClubs() {
  try {
    const res = await fetch(`${API_BASE}/api/clubs`);
    const json = await res.json();
    if (json.success) {
      clubsData = json.data;
      renderClubsList(clubsData);
      populateClubDropdowns();
    }
  } catch (err) {
    console.error("Error fetching clubs:", err);
  }
}

async function fetchActivities() {
  try {
    const res = await fetch(`${API_BASE}/api/activities`);
    const json = await res.json();
    if (json.success) {
      activitiesData = json.data;
      renderActivitiesTable(activitiesData);
      renderCalendar();
    }
  } catch (err) {
    console.error("Error fetching activities:", err);
  }
}

async function fetchMembers() {
  try {
    const res = await fetch(`${API_BASE}/api/members`);
    const json = await res.json();
    if (json.success) {
      membersData = json.data;
      renderMembersTable(membersData);
    }
  } catch (err) {
    console.error("Error fetching members:", err);
  }
}

async function loadDashboardStats() {
  try {
    const res = await fetch(`${API_BASE}/api/stats`);
    const json = await res.json();
    if (json.success) {
      const stats = json.data;
      document.getElementById("stat-clubs").textContent = stats.total_clubs;
      document.getElementById("stat-activities").textContent = stats.total_activities;
      document.getElementById("stat-members").textContent = stats.active_members;
      document.getElementById("stat-hours").textContent = `${stats.total_hours} hrs`;

      renderCategoryBars(stats.categories, stats.total_activities);
      renderTopMembers(stats.top_members);
      renderRecentActivities(stats.recent_activities);
      renderAnnouncements(stats.recent_announcements);
    }
  } catch (err) {
    console.error("Error loading dashboard stats:", err);
  }
}

// --- RENDER DASHBOARD VISUALS ---
function renderCategoryBars(categories, total) {
  const container = document.getElementById("category-bars-container");
  if (!categories || categories.length === 0) {
    container.innerHTML = '<p style="color: var(--gray-400); font-size: 0.9rem;">No activities logged yet.</p>';
    return;
  }

  container.innerHTML = categories.map(cat => {
    const pct = total > 0 ? Math.round((cat.count / total) * 100) : 0;
    return `
      <div class="category-item">
        <div class="category-info">
          <span>${cat.category}</span>
          <span style="color: var(--gray-500); font-weight: normal;">${cat.count} events (${pct}%)</span>
        </div>
        <div class="progress-track">
          <div class="progress-fill" style="width: ${pct}%"></div>
        </div>
      </div>
    `;
  }).join("");
}

function renderTopMembers(topMembers) {
  const container = document.getElementById("top-members-container");
  if (!topMembers || topMembers.length === 0) {
    container.innerHTML = '<p style="color: var(--gray-400); font-size: 0.9rem;">No participation hours recorded yet.</p>';
    return;
  }

  container.innerHTML = topMembers.map((m, idx) => {
    const initials = m.name.split(" ").map(w => w[0]).join("").slice(0, 2).toUpperCase();
    return `
      <div class="member-rank-item">
        <div class="rank-avatar">${initials}</div>
        <div class="rank-details">
          <div class="rank-name">${m.name}</div>
          <div class="rank-club">${m.club_name}</div>
        </div>
        <div class="rank-score">
          <div class="rank-hours">${m.total_hours} hrs</div>
          <div class="rank-events">${m.activities_attended} events</div>
        </div>
      </div>
    `;
  }).join("");
}

function renderRecentActivities(recent) {
  const tbody = document.getElementById("recent-activities-table");
  if (!recent || recent.length === 0) {
    tbody.innerHTML = '<tr><td colspan="6" style="text-align: center; color: var(--gray-400);">No recent activities</td></tr>';
    return;
  }

  tbody.innerHTML = recent.map(act => {
    const statusClass = act.status === 'Completed' ? 'badge-completed' : (act.status === 'Planned' ? 'badge-planned' : 'badge-ongoing');
    return `
      <tr>
        <td style="font-weight: 600; color: var(--gray-900);">${act.title}</td>
        <td>${act.club_name}</td>
        <td><span class="badge badge-category">${act.category}</span></td>
        <td>${act.date}</td>
        <td><span class="badge ${statusClass}">${act.status}</span></td>
        <td>${act.attendees} attendees</td>
      </tr>
    `;
  }).join("");
}

function renderAnnouncements(announcements) {
  const container = document.getElementById("announcements-container");
  if (!container) return;
  if (!announcements || announcements.length === 0) {
    container.innerHTML = '<p style="color: var(--gray-400); font-size: 0.9rem; grid-column: 1/-1;">No announcements posted yet.</p>';
    return;
  }

  container.innerHTML = announcements.map(an => {
    const priorityColor = an.priority === 'Urgent' ? '#ef4444' : (an.priority === 'Important' ? '#f59e0b' : '#3b82f6');
    const priorityBg = an.priority === 'Urgent' ? '#fee2e2' : (an.priority === 'Important' ? '#fef3c7' : '#eff6ff');
    return `
      <div style="background: white; border: 1px solid var(--gray-200); border-radius: var(--radius-md); padding: 1rem; border-left: 4px solid ${priorityColor};">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.35rem;">
          <h4 style="font-size: 0.95rem; font-weight: 700; color: var(--gray-900);">${escapeHtml(an.title)}</h4>
          <span style="font-size: 0.7rem; font-weight: 700; padding: 0.15rem 0.5rem; border-radius: 999px; background: ${priorityBg}; color: ${priorityColor};">${an.priority}</span>
        </div>
        <div style="font-size: 0.8rem; color: var(--gray-500); margin-bottom: 0.5rem;">
          <span>${escapeHtml(an.club_name)}</span> • <span>${an.date}</span>
        </div>
        <p style="font-size: 0.85rem; color: var(--gray-700); line-height: 1.4; margin-bottom: 0.75rem;">${escapeHtml(an.content)}</p>
        ${currentUser && (currentUser.role === 'Admin' || currentUser.role === 'Officer') ? `
        <div style="text-align: right;">
          <button class="btn btn-secondary btn-sm" onclick="deleteAnnouncement(${an.id})" style="color: var(--danger); font-size: 0.75rem; padding: 0.2rem 0.5rem;">🗑️ Delete</button>
        </div>` : ''}
      </div>
    `;
  }).join("");
}

function openAnnouncementModal() {
  document.getElementById("announcement-form").reset();
  document.getElementById("ann-date").value = new Date().toISOString().split("T")[0];
  openModal("modal-announcement");
}

async function saveAnnouncement(event) {
  event.preventDefault();
  const payload = {
    club_id: document.getElementById("ann-club").value,
    title: document.getElementById("ann-title").value,
    priority: document.getElementById("ann-priority").value,
    date: document.getElementById("ann-date").value,
    content: document.getElementById("ann-content").value
  };

  try {
    const res = await fetch(`${API_BASE}/api/announcements`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const json = await res.json();
    if (json.success) {
      showToast("Announcement published!");
      closeModal("modal-announcement");
      await loadDashboardStats();
    } else {
      showToast(json.error || "Failed to post announcement", "error");
    }
  } catch (err) {
    showToast("Server error posting announcement", "error");
  }
}

async function deleteAnnouncement(id) {
  if (!confirm("Are you sure you want to delete this notice?")) return;
  try {
    const res = await fetch(`${API_BASE}/api/announcements/${id}`, { method: "DELETE" });
    const json = await res.json();
    if (json.success) {
      showToast("Notice deleted");
      await loadDashboardStats();
    }
  } catch (err) {
    showToast("Error deleting notice", "error");
  }
}

// --- RENDER ACTIVITIES ---
function renderActivitiesTable(activities) {
  const tbody = document.getElementById("activities-table-body");
  if (!activities || activities.length === 0) {
    tbody.innerHTML = '<tr><td colspan="9" style="text-align: center; color: var(--gray-400); padding: 2rem;">No activities found matching criteria.</td></tr>';
    return;
  }

  tbody.innerHTML = activities.map(a => {
    const statusClass = a.status === 'Completed' ? 'badge-completed' : (a.status === 'Planned' ? 'badge-planned' : 'badge-ongoing');
    const isStudentOrGuest = !currentUser || currentUser.role === "Member";

    const attendeesCol = isStudentOrGuest
      ? `<span class="badge badge-category">👥 ${a.attendees_count} Attendees</span>`
      : `<button class="btn btn-secondary btn-sm" onclick="openAttendanceModal(${a.id}, '${escapeHtml(a.title)}', '${escapeHtml(a.club_name)}')">
          👥 ${a.attendees_count} Mark
        </button>`;

    let actionsCol = "";
    if (currentUser && currentUser.role === "Member") {
      const isRsvpd = studentRsvps.includes(a.id);
      if (a.status === 'Completed') {
        actionsCol = `<button class="btn btn-secondary btn-sm" onclick="openCertificate(${a.id})" style="font-size: 0.75rem; padding: 0.25rem 0.5rem; color: #1e3a8a; font-weight: 600;">📜 Certificate</button>`;
      } else {
        actionsCol = isRsvpd
          ? `<button class="btn btn-sm" onclick="toggleRsvp(${a.id})" style="background: #dcfce7; color: #15803d; border: 1px solid #86efac; font-size: 0.75rem; padding: 0.25rem 0.5rem; font-weight: 600;" title="Click to cancel RSVP">✅ Registered</button>`
          : `<button class="btn btn-primary btn-sm" onclick="toggleRsvp(${a.id})" style="font-size: 0.75rem; padding: 0.25rem 0.5rem; font-weight: 600;">🎟️ RSVP</button>`;
      }
    } else if (isStudentOrGuest) {
      actionsCol = `<span style="font-size: 0.8rem; color: var(--gray-400);">View only</span>`;
    } else {
      actionsCol = `<div style="display: flex; gap: 0.35rem; justify-content: flex-end;">
          <button class="btn btn-secondary btn-sm" onclick="editActivity(${a.id})">✏️</button>
          ${currentUser && currentUser.role === 'Admin' ? `<button class="btn btn-secondary btn-sm" onclick="deleteActivity(${a.id})" style="color: var(--danger);">🗑️</button>` : ''}
        </div>`;
    }

    return `
      <tr>
        <td style="font-weight: 600; color: var(--gray-900);">${a.title}</td>
        <td>${a.club_name}</td>
        <td><span class="badge badge-category">${a.category}</span></td>
        <td>${a.date}</td>
        <td>${a.duration_hours} hrs</td>
        <td>${a.location || '—'}</td>
        <td><span class="badge ${statusClass}">${a.status}</span></td>
        <td>${attendeesCol}</td>
        <td style="text-align: right;">${actionsCol}</td>
      </tr>
    `;
  }).join("");
}

function filterActivities() {
  const searchTerm = document.getElementById("activity-search").value.toLowerCase();
  const clubId = document.getElementById("activity-club-filter").value;
  const status = document.getElementById("activity-status-filter").value;

  const filtered = activitiesData.filter(a => {
    const matchesSearch = !searchTerm || a.title.toLowerCase().includes(searchTerm) || (a.location && a.location.toLowerCase().includes(searchTerm));
    const matchesClub = !clubId || String(a.club_id) === String(clubId);
    const matchesStatus = !status || a.status === status;
    return matchesSearch && matchesClub && matchesStatus;
  });

  renderActivitiesTable(filtered);
}

// --- RENDER MEMBERS ---
function renderMembersTable(members) {
  const tbody = document.getElementById("members-table-body");
  if (!members || members.length === 0) {
    tbody.innerHTML = '<tr><td colspan="9" style="text-align: center; color: var(--gray-400); padding: 2rem;">No members found matching criteria.</td></tr>';
    return;
  }

  tbody.innerHTML = members.map(m => {
    const isStudentOrGuest = !currentUser || currentUser.role === "Member";
    const actionsHtml = isStudentOrGuest
      ? `<span class="badge badge-category" style="font-size: 0.75rem;">Verified Member</span>`
      : `<div style="display: flex; gap: 0.35rem; justify-content: flex-end;">
          <button class="btn btn-secondary btn-sm" onclick="editMember(${m.id})">✏️</button>
          ${currentUser && currentUser.role === 'Admin' ? `<button class="btn btn-secondary btn-sm" onclick="deleteMember(${m.id})" style="color: var(--danger);">🗑️</button>` : ''}
        </div>`;

    return `
      <tr>
        <td style="font-weight: 600; color: var(--gray-900);">${m.name}</td>
        <td>${m.club_name}</td>
        <td><span class="badge badge-role">${m.role}</span></td>
        <td>${m.email || '—'}</td>
        <td>${m.join_date || '—'}</td>
        <td style="font-weight: 600; color: var(--primary);">${m.total_hours} hrs</td>
        <td>${m.attended_count} events</td>
        <td><span class="badge ${m.status === 'Active' ? 'badge-completed' : 'badge-category'}">${m.status}</span></td>
        <td style="text-align: right;">${actionsHtml}</td>
      </tr>
    `;
  }).join("");
}

function filterMembers() {
  const searchTerm = document.getElementById("member-search").value.toLowerCase();
  const clubId = document.getElementById("member-club-filter").value;

  const filtered = membersData.filter(m => {
    const matchesSearch = !searchTerm || m.name.toLowerCase().includes(searchTerm) || (m.email && m.email.toLowerCase().includes(searchTerm));
    const matchesClub = !clubId || String(m.club_id) === String(clubId);
    return matchesSearch && matchesClub;
  });

  renderMembersTable(filtered);
}

// --- RENDER CLUBS ---
function renderClubsList(clubs) {
  const container = document.getElementById("clubs-grid-container");
  if (!clubs || clubs.length === 0) {
    container.innerHTML = '<p style="color: var(--gray-400); font-size: 0.9rem;">No clubs registered yet. Click "+ Create New Club" above.</p>';
    return;
  }

  container.innerHTML = clubs.map(c => {
    const isStudentOrGuest = !currentUser || currentUser.role === "Member";
    const clubActions = isStudentOrGuest
      ? `<span class="badge badge-category" style="font-size: 0.75rem;">Registered</span>`
      : `<div style="display: flex; gap: 0.35rem;">
          <button class="btn btn-secondary btn-sm" onclick="editClub(${c.id})">✏️</button>
          ${currentUser && currentUser.role === 'Admin' ? `<button class="btn btn-secondary btn-sm" onclick="deleteClub(${c.id})" style="color: var(--danger);">🗑️</button>` : ''}
        </div>`;

    return `
      <div class="club-card">
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
          <h3 class="club-card-title">${c.name}</h3>
          <span class="badge badge-category">${c.category}</span>
        </div>
        <p style="font-size: 0.85rem; color: var(--gray-500); margin-bottom: 0.75rem;">
          Lead: <strong>${c.lead_name || 'Unassigned'}</strong>
        </p>
        <p class="club-card-desc">${c.description || 'No description provided.'}</p>
        <div class="club-card-footer">
          <div style="display: flex; gap: 1rem;">
            <span class="club-meta-pill">👥 ${c.member_count} Members</span>
            <span class="club-meta-pill">🎯 ${c.activity_count} Events</span>
          </div>
          ${clubActions}
        </div>
      </div>
    `;
  }).join("");
}

// --- MODAL CONTROLS ---
function openModal(modalId) {
  const el = document.getElementById(modalId);
  if (el) el.classList.add("show");
}

function closeModal(modalId) {
  const el = document.getElementById(modalId);
  if (el) el.classList.remove("show");
}

// --- ACTIVITY CRUD ---
function openActivityModal() {
  document.getElementById("activity-modal-title").textContent = "Log Club Activity";
  document.getElementById("activity-form").reset();
  document.getElementById("act-id").value = "";
  document.getElementById("act-date").value = new Date().toISOString().split("T")[0];
  openModal("modal-activity");
  updateLiveActivityPrediction();
}

function editActivity(id) {
  const act = activitiesData.find(a => a.id === id);
  if (!act) return;

  document.getElementById("activity-modal-title").textContent = "Edit Club Activity";
  document.getElementById("act-id").value = act.id;
  document.getElementById("act-club").value = act.club_id;
  document.getElementById("act-title").value = act.title;
  document.getElementById("act-category").value = act.category;
  document.getElementById("act-date").value = act.date;
  document.getElementById("act-duration").value = act.duration_hours;
  document.getElementById("act-location").value = act.location || "";
  document.getElementById("act-status").value = act.status;
  document.getElementById("act-desc").value = act.description || "";

  openModal("modal-activity");
  updateLiveActivityPrediction();
}

async function saveActivity(event) {
  event.preventDefault();
  const id = document.getElementById("act-id").value;
  const payload = {
    club_id: document.getElementById("act-club").value,
    title: document.getElementById("act-title").value,
    category: document.getElementById("act-category").value,
    date: document.getElementById("act-date").value,
    duration_hours: document.getElementById("act-duration").value,
    location: document.getElementById("act-location").value,
    status: document.getElementById("act-status").value,
    description: document.getElementById("act-desc").value
  };

  try {
    const url = id ? `${API_BASE}/api/activities/${id}` : `${API_BASE}/api/activities`;
    const method = id ? "PUT" : "POST";
    const res = await fetch(url, {
      method,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const json = await res.json();
    if (json.success) {
      showToast(id ? "Activity updated successfully!" : "New activity logged!");
      closeModal("modal-activity");
      await fetchActivities();
      await loadDashboardStats();
    } else {
      showToast(json.error || "Failed to save activity", "error");
    }
  } catch (err) {
    showToast("Server error saving activity", "error");
  }
}

async function deleteActivity(id) {
  if (!confirm("Are you sure you want to delete this activity and its attendance records?")) return;
  try {
    const res = await fetch(`${API_BASE}/api/activities/${id}`, { method: "DELETE" });
    const json = await res.json();
    if (json.success) {
      showToast("Activity deleted");
      await fetchActivities();
      await loadDashboardStats();
    }
  } catch (err) {
    showToast("Error deleting activity", "error");
  }
}

// --- MEMBER CRUD ---
function openMemberModal() {
  document.getElementById("member-modal-title").textContent = "Add Member";
  document.getElementById("member-form").reset();
  document.getElementById("member-id").value = "";
  openModal("modal-member");
}

function editMember(id) {
  const m = membersData.find(mem => mem.id === id);
  if (!m) return;

  document.getElementById("member-modal-title").textContent = "Edit Member";
  document.getElementById("member-id").value = m.id;
  document.getElementById("member-club").value = m.club_id;
  document.getElementById("member-name").value = m.name;
  document.getElementById("member-email").value = m.email || "";
  document.getElementById("member-role").value = m.role || "Member";
  document.getElementById("member-status").value = m.status || "Active";

  openModal("modal-member");
}

async function saveMember(event) {
  event.preventDefault();
  const id = document.getElementById("member-id").value;
  const payload = {
    club_id: document.getElementById("member-club").value,
    name: document.getElementById("member-name").value,
    email: document.getElementById("member-email").value,
    role: document.getElementById("member-role").value,
    status: document.getElementById("member-status").value
  };

  try {
    const url = id ? `${API_BASE}/api/members/${id}` : `${API_BASE}/api/members`;
    const method = id ? "PUT" : "POST";
    const res = await fetch(url, {
      method,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const json = await res.json();
    if (json.success) {
      showToast(id ? "Member updated successfully!" : "Member added!");
      closeModal("modal-member");
      await fetchMembers();
      await fetchClubs();
      await loadDashboardStats();
    } else {
      showToast(json.error || "Failed to save member", "error");
    }
  } catch (err) {
    showToast("Server error saving member", "error");
  }
}

async function deleteMember(id) {
  if (!confirm("Are you sure you want to remove this member?")) return;
  try {
    const res = await fetch(`${API_BASE}/api/members/${id}`, { method: "DELETE" });
    const json = await res.json();
    if (json.success) {
      showToast("Member removed");
      await fetchMembers();
      await fetchClubs();
      await loadDashboardStats();
    }
  } catch (err) {
    showToast("Error removing member", "error");
  }
}

// --- CLUB CRUD ---
function openClubModal() {
  document.getElementById("club-modal-title").textContent = "Create New Club";
  document.getElementById("club-form").reset();
  document.getElementById("club-id").value = "";
  openModal("modal-club");
}

function editClub(id) {
  const c = clubsData.find(club => club.id === id);
  if (!c) return;

  document.getElementById("club-modal-title").textContent = "Edit Club";
  document.getElementById("club-id").value = c.id;
  document.getElementById("club-name").value = c.name;
  document.getElementById("club-category").value = c.category;
  document.getElementById("club-lead").value = c.lead_name || "";
  document.getElementById("club-desc").value = c.description || "";

  openModal("modal-club");
}

async function saveClub(event) {
  event.preventDefault();
  const id = document.getElementById("club-id").value;
  const payload = {
    name: document.getElementById("club-name").value,
    category: document.getElementById("club-category").value,
    lead_name: document.getElementById("club-lead").value,
    description: document.getElementById("club-desc").value
  };

  try {
    const url = id ? `${API_BASE}/api/clubs/${id}` : `${API_BASE}/api/clubs`;
    const method = id ? "PUT" : "POST";
    const res = await fetch(url, {
      method,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const json = await res.json();
    if (json.success) {
      showToast(id ? "Club updated!" : "New club created!");
      closeModal("modal-club");
      await fetchClubs();
      await loadDashboardStats();
    } else {
      showToast(json.error || "Failed to save club", "error");
    }
  } catch (err) {
    showToast("Server error saving club", "error");
  }
}

async function deleteClub(id) {
  if (!confirm("Are you sure? Deleting a club also deletes all its members and activities!")) return;
  try {
    const res = await fetch(`${API_BASE}/api/clubs/${id}`, { method: "DELETE" });
    const json = await res.json();
    if (json.success) {
      showToast("Club deleted");
      await fetchClubs();
      await fetchActivities();
      await fetchMembers();
      await loadDashboardStats();
    }
  } catch (err) {
    showToast("Error deleting club", "error");
  }
}

// --- ATTENDANCE & ROLL CALL ---
async function openAttendanceModal(activityId, title, clubName) {
  currentAttendanceActivityId = activityId;
  document.getElementById("attendance-modal-sub").textContent = `${title} • ${clubName}`;

  try {
    const res = await fetch(`${API_BASE}/api/activities/${activityId}/attendance`);
    const json = await res.json();
    if (json.success) {
      currentAttendanceRecords = json.data;
      document.getElementById("attendance-count").textContent = currentAttendanceRecords.length;
      renderAttendanceRows(currentAttendanceRecords);
      openModal("modal-attendance");
    }
  } catch (err) {
    showToast("Could not load attendance roster", "error");
  }
}

function renderAttendanceRows(records) {
  const tbody = document.getElementById("attendance-table-body");
  if (!records || records.length === 0) {
    tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; color: var(--gray-400); padding: 1.5rem;">No members registered in this club yet.</td></tr>';
    return;
  }

  tbody.innerHTML = records.map((r, i) => {
    return `
      <tr data-member-id="${r.member_id}">
        <td style="font-weight: 600;">
          ${escapeHtml(r.member_name)}
          ${r.status === 'RSVP' ? '<span class="badge" style="background: #fef3c7; color: #92400e; font-size: 0.72rem; margin-left: 0.4rem;">🎟️ RSVP</span>' : ''}
        </td>
        <td><span class="badge badge-role">${r.role}</span></td>
        <td>
          <div class="status-toggle-group">
            <button type="button" class="status-toggle-btn present ${r.status === 'Present' ? 'active' : ''}" onclick="setAttendanceStatus(${i}, 'Present')">Present</button>
            <button type="button" class="status-toggle-btn absent ${r.status === 'Absent' ? 'active' : ''}" onclick="setAttendanceStatus(${i}, 'Absent')">Absent</button>
            <button type="button" class="status-toggle-btn excused ${r.status === 'Excused' ? 'active' : ''}" onclick="setAttendanceStatus(${i}, 'Excused')">Excused</button>
          </div>
        </td>
        <td>
          <input type="number" step="0.5" min="0" max="24" class="form-control" style="width: 85px; padding: 0.35rem 0.5rem;" value="${r.hours_credited}" onchange="setAttendanceHours(${i}, this.value)">
        </td>
        <td>
          <input type="text" class="form-control" style="padding: 0.35rem 0.5rem;" placeholder="Optional note..." value="${escapeHtml(r.notes || '')}" onchange="setAttendanceNotes(${i}, this.value)">
        </td>
      </tr>
    `;
  }).join("");
}

function setAttendanceStatus(index, status) {
  currentAttendanceRecords[index].status = status;
  // If Absent, set hours to 0 by default, otherwise keep original or credited
  if (status === "Absent") {
    currentAttendanceRecords[index].hours_credited = 0;
  }
  renderAttendanceRows(currentAttendanceRecords);
}

function setAttendanceHours(index, hours) {
  currentAttendanceRecords[index].hours_credited = parseFloat(hours) || 0;
}

function setAttendanceNotes(index, notes) {
  currentAttendanceRecords[index].notes = notes;
}

function markAllAttendance(status) {
  currentAttendanceRecords.forEach(r => {
    r.status = status;
    if (status === "Absent") r.hours_credited = 0;
  });
  renderAttendanceRows(currentAttendanceRecords);
}

async function submitAttendance() {
  if (!currentAttendanceActivityId) return;

  try {
    const res = await fetch(`${API_BASE}/api/activities/${currentAttendanceActivityId}/attendance`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ attendance: currentAttendanceRecords })
    });
    const json = await res.json();
    if (json.success) {
      showToast("Attendance roll call saved!");
      closeModal("modal-attendance");
      await fetchActivities();
      await fetchMembers();
      await loadDashboardStats();
    } else {
      showToast("Failed to save attendance", "error");
    }
  } catch (err) {
    showToast("Error updating attendance", "error");
  }
}

// --- CSV EXPORT ---
function exportData(type) {
  window.open(`${API_BASE}/api/export/${type}`, "_blank");
}

// --- SEED SAMPLE DATA ---
async function seedSampleData() {
  if (!confirm("This will reload sample clubs and activity records. Continue?")) return;
  try {
    const res = await fetch(`${API_BASE}/api/seed`, { method: "POST" });
    const json = await res.json();
    if (json.success) {
      showToast("Sample data loaded successfully!");
      await loadInitialData();
    }
  } catch (err) {
    showToast("Error reloading data", "error");
  }
}

// Helper utility
function escapeHtml(text) {
  if (!text) return "";
  return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
}

// =========================================================================
// 8. CALENDAR ENGINE
// =========================================================================
function setActivitiesView(mode) {
  activitiesViewMode = mode;
  const tableCont = document.getElementById("activities-table-container");
  const calCont = document.getElementById("activities-calendar-container");
  const btnTable = document.getElementById("btn-view-table");
  const btnCal = document.getElementById("btn-view-calendar");

  if (mode === "calendar") {
    if (tableCont) tableCont.style.display = "none";
    if (calCont) calCont.style.display = "block";
    if (btnTable) btnTable.classList.remove("active");
    if (btnCal) btnCal.classList.add("active");
    renderCalendar();
  } else {
    if (tableCont) tableCont.style.display = "block";
    if (calCont) calCont.style.display = "none";
    if (btnTable) btnTable.classList.add("active");
    if (btnCal) btnCal.classList.remove("active");
  }
}

function changeCalendarMonth(delta) {
  currentCalMonth += delta;
  if (currentCalMonth < 0) {
    currentCalMonth = 11;
    currentCalYear -= 1;
  } else if (currentCalMonth > 11) {
    currentCalMonth = 0;
    currentCalYear += 1;
  }
  renderCalendar();
}

function resetCalendarToCurrentMonth() {
  const d = new Date();
  currentCalYear = d.getFullYear();
  currentCalMonth = d.getMonth();
  renderCalendar();
}

function renderCalendar() {
  const grid = document.getElementById("calendar-days-grid");
  const title = document.getElementById("calendar-month-title");
  if (!grid) return;

  const monthNames = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
  ];

  if (title) {
    title.textContent = `${monthNames[currentCalMonth]} ${currentCalYear}`;
  }

  const firstDay = new Date(currentCalYear, currentCalMonth, 1).getDay();
  const totalDays = new Date(currentCalYear, currentCalMonth + 1, 0).getDate();
  const prevMonthTotalDays = new Date(currentCalYear, currentCalMonth, 0).getDate();
  const todayStr = new Date().toISOString().split("T")[0];

  let cellsHtml = "";

  for (let i = firstDay - 1; i >= 0; i--) {
    const dayNum = prevMonthTotalDays - i;
    cellsHtml += `
      <div class="calendar-day-cell other-month">
        <div class="cal-day-header"><span class="cal-day-num">${dayNum}</span></div>
      </div>
    `;
  }

  for (let d = 1; d <= totalDays; d++) {
    const monthFormatted = String(currentCalMonth + 1).padStart(2, "0");
    const dayFormatted = String(d).padStart(2, "0");
    const dateStr = `${currentCalYear}-${monthFormatted}-${dayFormatted}`;
    const isToday = (dateStr === todayStr);

    const dayActivities = activitiesData.filter(a => a.date === dateStr);

    let eventsHtml = "";
    if (dayActivities.length > 0) {
      eventsHtml = dayActivities.map(act => {
        let pillClass = "pill-default";
        if (act.category.includes("Workshop")) pillClass = "pill-workshop";
        else if (act.category.includes("Competition") || act.category.includes("Hackathon")) pillClass = "pill-competition";
        else if (act.category.includes("Social")) pillClass = "pill-social";
        else if (act.category.includes("Meeting")) pillClass = "pill-meeting";
        else if (act.category.includes("Volunteer")) pillClass = "pill-volunteer";

        return `
          <div class="cal-event-pill ${pillClass}" onclick="openCalendarEvent(${act.id})" title="${escapeHtml(act.title)} (${escapeHtml(act.club_name)})">
            ${escapeHtml(act.title)}
          </div>
        `;
      }).join("");
    }

    cellsHtml += `
      <div class="calendar-day-cell ${isToday ? 'today' : ''}">
        <div class="cal-day-header">
          <span class="cal-day-num">${d}</span>
          ${dayActivities.length > 0 ? `<span style="font-size: 0.65rem; color: var(--gray-400); font-weight: 600;">${dayActivities.length}</span>` : ''}
        </div>
        <div class="cal-events-list">
          ${eventsHtml}
        </div>
      </div>
    `;
  }

  const totalRendered = firstDay + totalDays;
  const remainingDays = (7 - (totalRendered % 7)) % 7;
  for (let n = 1; n <= remainingDays; n++) {
    cellsHtml += `
      <div class="calendar-day-cell other-month">
        <div class="cal-day-header"><span class="cal-day-num">${n}</span></div>
      </div>
    `;
  }

  grid.innerHTML = cellsHtml;
}

function openCalendarEvent(activityId) {
  const act = activitiesData.find(a => a.id === activityId);
  if (!act) return;

  const title = document.getElementById("event-detail-title");
  const body = document.getElementById("event-detail-body");
  const footer = document.getElementById("event-detail-footer");

  if (title) title.textContent = act.title;
  
  const isStudent = currentUser && currentUser.role === "Member";
  const isRsvpd = studentRsvps.includes(act.id);
  const statusClass = act.status === 'Completed' ? 'badge-completed' : (act.status === 'Planned' ? 'badge-planned' : 'badge-ongoing');

  let rsvpBtnHtml = "";
  if (isStudent) {
    if (act.status === 'Completed') {
      rsvpBtnHtml = `<button class="btn btn-primary" onclick="closeModal('modal-event-detail'); openCertificate(${act.id});">📜 View Certificate of Participation</button>`;
    } else {
      rsvpBtnHtml = isRsvpd
        ? `<button class="btn" onclick="toggleRsvp(${act.id}); closeModal('modal-event-detail');" style="background: #fee2e2; color: #dc2626; border: 1px solid #fca5a5; font-weight: 600;">❌ Cancel RSVP</button>`
        : `<button class="btn btn-primary" onclick="toggleRsvp(${act.id}); closeModal('modal-event-detail');" style="font-weight: 600;">🎟️ Register / RSVP for Event</button>`;
    }
  } else if (currentUser && (currentUser.role === 'Admin' || currentUser.role === 'Officer')) {
    rsvpBtnHtml = `<button class="btn btn-primary" onclick="closeModal('modal-event-detail'); openAttendanceModal(${act.id}, '${escapeHtml(act.title)}', '${escapeHtml(act.club_name)}');">👥 Mark Roll Call</button>`;
  }

  if (body) {
    body.innerHTML = `
      <div style="display: flex; gap: 0.5rem; margin-bottom: 1rem; align-items: center; flex-wrap: wrap;">
        <span class="badge badge-category">${act.category}</span>
        <span class="badge ${statusClass}">${act.status}</span>
        <span style="font-size: 0.85rem; color: var(--gray-600); font-weight: 600;">🏛️ ${escapeHtml(act.club_name)}</span>
      </div>
      <div style="background: var(--gray-50); border: 1px solid var(--gray-200); border-radius: var(--radius-md); padding: 1rem; margin-bottom: 1rem;">
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; font-size: 0.88rem;">
          <div>📅 <strong>Date:</strong> ${act.date}</div>
          <div>⏱️ <strong>Duration:</strong> ${act.duration_hours} hrs</div>
          <div>📍 <strong>Venue:</strong> ${escapeHtml(act.location || 'Campus Center')}</div>
          <div>👥 <strong>Attendance:</strong> ${act.attendees_count} recorded</div>
        </div>
      </div>
      <p style="font-size: 0.9rem; color: var(--gray-700); line-height: 1.5; margin-bottom: 1rem;">
        ${escapeHtml(act.description || 'No detailed description provided.')}
      </p>
    `;
  }

  if (footer) {
    footer.innerHTML = `
      <button type="button" class="btn btn-secondary" onclick="closeModal('modal-event-detail')">Close</button>
      ${rsvpBtnHtml}
    `;
  }

  openModal("modal-event-detail");
}

// =========================================================================
// 9. STUDENT RSVP ENGINE
// =========================================================================
async function fetchStudentRsvps() {
  if (!currentUser) return;
  const memberId = 49;
  try {
    const res = await fetch(`${API_BASE}/api/student/${memberId}/rsvps`);
    const json = await res.json();
    if (json.success) {
      studentRsvps = json.data || [];
    }
  } catch (e) {
    // ignore
  }
}

async function toggleRsvp(activityId) {
  if (!currentUser) {
    showToast("Please sign in as a student to RSVP", "error");
    return;
  }
  const memberId = 49;
  const isRsvpd = studentRsvps.includes(activityId);

  try {
    if (isRsvpd) {
      const res = await fetch(`${API_BASE}/api/activities/${activityId}/rsvp?member_id=${memberId}`, {
        method: "DELETE"
      });
      const json = await res.json();
      if (json.success) {
        studentRsvps = studentRsvps.filter(id => id !== activityId);
        showToast("RSVP cancelled successfully.");
        await fetchActivities();
      }
    } else {
      const res = await fetch(`${API_BASE}/api/activities/${activityId}/rsvp`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ member_id: memberId })
      });
      const json = await res.json();
      if (json.success) {
        studentRsvps.push(activityId);
        showToast("🎟️ Successfully registered for event!");
        await fetchActivities();
      }
    }
  } catch (err) {
    showToast("Error updating RSVP", "error");
  }
}

// =========================================================================
// 10. AI EVENT TURNOUT PREDICTOR
// =========================================================================
async function updateLiveActivityPrediction() {
  const clubId = document.getElementById("act-club")?.value;
  const category = document.getElementById("act-category")?.value || "Workshop";
  const duration = parseFloat(document.getElementById("act-duration")?.value || "1.5");
  const date = document.getElementById("act-date")?.value || "";

  const predCount = document.getElementById("live-pred-count");
  const predBadge = document.getElementById("live-pred-badge");
  const predConf = document.getElementById("live-pred-confidence");
  const predTip = document.getElementById("live-pred-tip");

  if (!predCount) return;

  try {
    const res = await fetch(`${API_BASE}/api/predict-attendance`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ club_id: clubId, category, duration_hours: duration, date })
    });
    const json = await res.json();
    if (json.success && json.data) {
      const p = json.data;
      predCount.textContent = `~${p.predicted_attendance} Attendees`;
      if (predBadge) {
        predBadge.textContent = p.demand_level;
        predBadge.style.color = p.demand_color;
      }
      if (predConf) {
        predConf.textContent = `${p.confidence_score}% Confidence`;
      }
      if (predTip && p.insights && p.insights[0]) {
        predTip.textContent = p.insights[0];
      }
    }
  } catch (e) {
    // fallback
  }
}

function openPredictorModal() {
  const simClub = document.getElementById("sim-club");
  if (simClub && clubsData.length > 0) {
    simClub.innerHTML = '<option value="">All Clubs Baseline</option>' +
      clubsData.map(c => `<option value="${c.id}">${c.name}</option>`).join("");
  }
  const today = new Date().toISOString().split("T")[0];
  const simDate = document.getElementById("sim-date");
  if (simDate && !simDate.value) simDate.value = today;

  openModal("modal-predictor");
  runSimulation();
}

async function runSimulation() {
  const clubId = document.getElementById("sim-club")?.value || null;
  const category = document.getElementById("sim-category")?.value || "Workshop";
  const date = document.getElementById("sim-date")?.value || "";
  const duration = parseFloat(document.getElementById("sim-duration")?.value || "2.5");

  try {
    const res = await fetch(`${API_BASE}/api/predict-attendance`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ club_id: clubId, category, duration_hours: duration, date })
    });
    const json = await res.json();
    if (json.success && json.data) {
      const p = json.data;
      document.getElementById("sim-res-count").textContent = `~${p.predicted_attendance}`;
      document.getElementById("sim-res-range").textContent = `Range: ${p.range}`;
      const demandEl = document.getElementById("sim-res-demand");
      if (demandEl) {
        demandEl.textContent = p.demand_level;
        demandEl.style.color = p.demand_color;
      }
      document.getElementById("sim-res-day").textContent = `${p.day_name} Schedule`;
      document.getElementById("sim-res-conf").textContent = `${p.confidence_score}%`;

      const list = document.getElementById("sim-res-insights");
      if (list && p.insights) {
        list.innerHTML = p.insights.map(item => `<li>${item}</li>`).join("");
      }
    }
  } catch (err) {
    console.error("Simulation error", err);
  }
}

function applySimulationToNewActivity() {
  closeModal("modal-predictor");
  openActivityModal();
  const simClub = document.getElementById("sim-club")?.value;
  const simCat = document.getElementById("sim-category")?.value;
  const simDate = document.getElementById("sim-date")?.value;
  const simDur = document.getElementById("sim-duration")?.value;

  if (simClub) document.getElementById("act-club").value = simClub;
  if (simCat) document.getElementById("act-category").value = simCat;
  if (simDate) document.getElementById("act-date").value = simDate;
  if (simDur) document.getElementById("act-duration").value = simDur;

  updateLiveActivityPrediction();
}

// =========================================================================
// 11. VERIFIED PARTICIPATION CERTIFICATES
// =========================================================================
async function openCertificatesListModal() {
  const memberId = 49;
  const container = document.getElementById("student-certs-list");
  if (!container) return;

  container.innerHTML = '<p style="text-align: center; color: var(--gray-400); padding: 1.5rem;">Loading verified certificates...</p>';
  openModal("modal-student-certificates");

  try {
    const res = await fetch(`${API_BASE}/api/student/${memberId}/certificates`);
    const json = await res.json();
    if (json.success && json.data && json.data.length > 0) {
      container.innerHTML = json.data.map(cert => `
        <div style="background: white; border: 1px solid var(--gray-200); border-radius: var(--radius-md); padding: 1rem; display: flex; justify-content: space-between; align-items: center; gap: 1rem; flex-wrap: wrap;">
          <div>
            <div style="display: flex; gap: 0.5rem; align-items: center; margin-bottom: 0.25rem;">
              <h4 style="margin: 0; font-size: 0.95rem; font-weight: 700; color: var(--gray-900);">${escapeHtml(cert.activity_title)}</h4>
              <span class="badge badge-category">${cert.category}</span>
            </div>
            <div style="font-size: 0.8rem; color: var(--gray-500);">
              <span>${escapeHtml(cert.club_name)}</span> • <span>${cert.activity_date}</span> • <span style="font-weight: 600; color: var(--primary);">${cert.hours_credited} hrs credited</span>
            </div>
          </div>
          <button class="btn btn-primary btn-sm" onclick="closeModal('modal-student-certificates'); openCertificate(${cert.activity_id}, ${cert.member_id});" style="font-weight: 600;">
            📜 View & Print
          </button>
        </div>
      `).join("");
    } else {
      container.innerHTML = `
        <div style="text-align: center; padding: 2rem; color: var(--gray-500);">
          <div style="font-size: 2rem; margin-bottom: 0.5rem;">📜</div>
          <p>No completed activities attended yet. Attend an event or log participation hours to unlock your verified certificates!</p>
        </div>
      `;
    }
  } catch (err) {
    container.innerHTML = '<p style="color: var(--danger); text-align: center;">Error loading certificates.</p>';
  }
}

async function openCertificate(activityId, memberId = 49) {
  try {
    const res = await fetch(`${API_BASE}/api/certificate/${activityId}/${memberId}`);
    const json = await res.json();
    if (json.success && json.data) {
      const cert = json.data;
      document.getElementById("cert-student-name").textContent = cert.member_name;
      document.getElementById("cert-activity-title").textContent = cert.activity_title;
      document.getElementById("cert-club-name").textContent = cert.club_name;
      document.getElementById("cert-date").textContent = cert.activity_date;
      document.getElementById("cert-hours").textContent = `${cert.hours_credited} Co-Curricular & Volunteer Hours`;
      document.getElementById("cert-club-lead").textContent = cert.lead_name || "Club Coordinator";
      document.getElementById("cert-serial-id").textContent = cert.cert_serial;

      openModal("modal-certificate");
    } else {
      showToast(json.error || "Certificate not found for this activity", "error");
    }
  } catch (err) {
    showToast("Error generating certificate", "error");
  }
}

function printCertificate() {
  window.print();
}

// =========================================================================
// 12. DATABASE OVERVIEW & AUDIT LOGS
// =========================================================================
async function fetchDatabaseOverview() {
  const tbodyLogs = document.getElementById("db-login-logs-tbody");
  const tbodyUsers = document.getElementById("db-users-tbody");

  try {
    const res = await fetch(`${API_BASE}/api/database/overview`);
    const json = await res.json();
    if (!json.success || !json.data) return;

    const data = json.data;

    // 1. Database Info & Storage Banner
    const filenameEl = document.getElementById("db-filename");
    const filepathEl = document.getElementById("db-filepath");
    const filesizeEl = document.getElementById("db-filesize");
    const engineEl = document.getElementById("db-engine");

    if (filenameEl) filenameEl.textContent = data.db_file;
    if (filepathEl) filepathEl.textContent = data.db_path;
    if (filesizeEl) filesizeEl.textContent = `${data.file_size_kb} KB`;
    if (engineEl) engineEl.textContent = `SQLite ${data.sqlite_version}`;

    // Table Counts
    if (data.table_counts) {
      Object.keys(data.table_counts).forEach(key => {
        const el = document.getElementById(`count-${key}`);
        if (el) el.textContent = data.table_counts[key];
      });
    }

    // 2. Render Login & Audit Logs Table
    if (tbodyLogs) {
      if (data.recent_logs && data.recent_logs.length > 0) {
        tbodyLogs.innerHTML = data.recent_logs.map(log => {
          let statusBadge = "";
          if (log.status === "SUCCESS") {
            statusBadge = '<span class="badge" style="background: #dcfce7; color: #15803d; font-weight: 700;">🟢 SUCCESS (Signed In)</span>';
          } else if (log.status === "FAILED_PASSWORD") {
            statusBadge = '<span class="badge" style="background: #fee2e2; color: #b91c1c; font-weight: 700;">🔴 FAILED (Wrong Password)</span>';
          } else if (log.status === "FAILED_ROLE_MISMATCH") {
            statusBadge = '<span class="badge" style="background: #fef3c7; color: #b45309; font-weight: 700;">🟠 BLOCKED (Wrong Section)</span>';
          } else if (log.status === "LOGOUT") {
            statusBadge = '<span class="badge" style="background: #f1f5f9; color: #475569; font-weight: 600;">🚪 LOGOUT (Signed Out)</span>';
          } else if (log.status === "REGISTERED") {
            statusBadge = '<span class="badge" style="background: #ede9fe; color: #6d28d9; font-weight: 700;">✨ REGISTERED (New Account)</span>';
          } else {
            statusBadge = `<span class="badge badge-category">${log.status}</span>`;
          }

          const clientShort = (log.user_agent || "Browser").includes("Mac") ? "🍎 Mac OS" : (log.user_agent || "Browser").includes("Windows") ? "🪟 Windows" : "📱 Web Client";

          return `
            <tr>
              <td style="font-family: monospace; font-size: 0.8rem; color: var(--gray-600);">${log.timestamp || "Just now"}</td>
              <td style="font-weight: 700; color: var(--primary);">${escapeHtml(log.username)}</td>
              <td>
                <div style="font-weight: 600; font-size: 0.88rem;">${escapeHtml(log.full_name || log.username)}</div>
                <div style="font-size: 0.75rem; color: var(--gray-500);">${log.role || "Unauthenticated"}</div>
              </td>
              <td>
                <span class="badge" style="background: #e2e8f0; color: #334155; font-size: 0.76rem;">${escapeHtml(log.portal || "General")}</span>
              </td>
              <td>${statusBadge}</td>
              <td style="font-family: monospace; font-size: 0.8rem;">${escapeHtml(log.ip_address || "127.0.0.1")}</td>
              <td style="font-size: 0.8rem; color: var(--gray-500);" title="${escapeHtml(log.user_agent || '')}">${clientShort}</td>
            </tr>
          `;
        }).join("");
      } else {
        tbodyLogs.innerHTML = `
          <tr>
            <td colspan="7" style="text-align: center; color: var(--gray-400); padding: 2rem;">No login logs recorded yet. Sign in or switch users to see live logs!</td>
          </tr>
        `;
      }
    }

    // 3. Render Registered Users Directory Table
    if (tbodyUsers) {
      if (data.users && data.users.length > 0) {
        tbodyUsers.innerHTML = data.users.map(u => {
          let roleColor = u.role === 'Admin' ? 'background: #ede9fe; color: #6d28d9;' : u.role === 'Officer' ? 'background: #fef3c7; color: #b45309;' : 'background: #dbeafe; color: #1e40af;';
          const avIcon = u.avatar && (u.avatar.startsWith('data:image') || u.avatar.startsWith('http'))
            ? `<span style="display:inline-block; width:22px; height:22px; border-radius:50%; background-image:url('${u.avatar}'); background-size:cover; background-position:center; vertical-align:middle; margin-right:6px; border:1px solid #cbd5e1;"></span>`
            : `<span style="font-size:1.15rem; vertical-align:middle; margin-right:6px;">${u.avatar || '👤'}</span>`;

          return `
            <tr>
              <td style="font-family: monospace; font-weight: 700; color: var(--gray-500);">#${u.id}</td>
              <td style="font-weight: 700; color: var(--gray-900);">${avIcon}${escapeHtml(u.username)}</td>
              <td style="font-weight: 600;">${escapeHtml(u.name)}</td>
              <td><span class="badge" style="${roleColor} font-weight: 700;">${u.role}</span></td>
              <td style="font-size: 0.85rem; color: var(--gray-600);">${escapeHtml(u.club_name || "All Campus")}</td>
              <td><span style="font-size: 0.78rem; background: #f1f5f9; color: #475569; padding: 0.2rem 0.5rem; border-radius: 4px; font-family: monospace;">🔒 SHA-256 Hashed</span></td>
              <td style="font-size: 0.8rem; color: var(--gray-500);">${u.created_at || "Pre-seeded"}</td>
              <td style="font-size: 0.8rem; font-weight: 600; color: ${u.last_login ? 'var(--success)' : 'var(--gray-400)'};">
                ${u.last_login ? `🟢 ${u.last_login}` : 'Never'}
              </td>
            </tr>
          `;
        }).join("");
      } else {
        tbodyUsers.innerHTML = `
          <tr>
            <td colspan="8" style="text-align: center; color: var(--gray-400); padding: 2rem;">No users found.</td>
          </tr>
        `;
      }
    }
  } catch (err) {
    console.error("Error fetching database overview", err);
    if (tbodyLogs) tbodyLogs.innerHTML = `<tr><td colspan="7" style="color: var(--danger); text-align: center;">Error loading logs from server.</td></tr>`;
    if (tbodyUsers) tbodyUsers.innerHTML = `<tr><td colspan="8" style="color: var(--danger); text-align: center;">Error loading users from server.</td></tr>`;
  }
}

async function clearLoginLogs() {
  if (!confirm("Are you sure you want to clear the login audit logs?")) return;
  try {
    const res = await fetch(`${API_BASE}/api/database/clear-logs`, { method: "POST" });
    const json = await res.json();
    if (json.success) {
      showToast("Login audit trail cleared.");
      fetchDatabaseOverview();
    } else {
      showToast(json.error || "Failed to clear logs", "error");
    }
  } catch (err) {
    showToast("Error clearing logs", "error");
  }
}

// =========================================================================
// 13. USER PROFILE & CUSTOM DP MANAGEMENT
// =========================================================================

async function openProfileModal() {
  if (!currentUser) {
    showToast("Please log in to edit your profile", "error");
    return;
  }

  // Refresh latest profile details from server
  try {
    const res = await fetch(`${API_BASE}/api/user/profile?user_id=${currentUser.id}`);
    const json = await res.json();
    if (json.success && json.data) {
      currentUser = { ...currentUser, ...json.data };
      localStorage.setItem("club_tracker_user", JSON.stringify(currentUser));
    }
  } catch (err) {
    console.error("Could not refresh profile from server", err);
  }

  // Header Elements
  const titleName = document.getElementById("modal-profile-title-name");
  const subtitle = document.getElementById("modal-profile-subtitle");
  const roleBadge = document.getElementById("modal-profile-role-badge");
  const avatarVal = document.getElementById("profile-avatar-val");

  if (titleName) titleName.textContent = currentUser.name || currentUser.username;
  if (subtitle) subtitle.textContent = `@${currentUser.username} • ${currentUser.department || currentUser.role || 'Member'}`;
  if (roleBadge) {
    roleBadge.textContent = currentUser.role || "Member";
    roleBadge.style.background = currentUser.role === "Admin" ? "#7c3aed" : currentUser.role === "Officer" ? "#d97706" : "#2563eb";
  }

  const initialAvatar = currentUser.avatar || "🎓";
  if (avatarVal) avatarVal.value = initialAvatar;
  renderProfileModalAvatar(initialAvatar);

  // Form Fields
  const setVal = (id, val) => {
    const el = document.getElementById(id);
    if (el) el.value = val || "";
  };

  setVal("profile-name", currentUser.name);
  setVal("profile-username", currentUser.username);
  setVal("profile-email", currentUser.email);
  setVal("profile-phone", currentUser.phone);
  setVal("profile-bio", currentUser.bio);
  setVal("profile-dept", currentUser.department);
  setVal("profile-studentid", currentUser.student_id);
  setVal("profile-year", currentUser.year);
  setVal("profile-club", currentUser.club_name || "General / All Campus");
  setVal("profile-skills", currentUser.skills);
  setVal("profile-linkedin", currentUser.linkedin);
  setVal("profile-github", currentUser.github);
  setVal("profile-new-pwd", "");

  // Update preset avatar selection highlight
  document.querySelectorAll(".preset-avatar-btn").forEach(btn => {
    if (btn.textContent.trim() === initialAvatar) btn.classList.add("active");
    else btn.classList.remove("active");
  });

  openModal("modal-profile");
}

function renderProfileModalAvatar(avatar) {
  const dpPreview = document.getElementById("modal-profile-dp-preview");
  if (!dpPreview) return;

  if (avatar && (avatar.startsWith("data:image") || avatar.startsWith("http"))) {
    dpPreview.textContent = "";
    dpPreview.style.backgroundImage = `url('${avatar}')`;
  } else if (avatar) {
    dpPreview.textContent = avatar;
    dpPreview.style.backgroundImage = "none";
  } else {
    dpPreview.textContent = "🎓";
    dpPreview.style.backgroundImage = "none";
  }
}

function selectPresetAvatar(emoji) {
  const avatarVal = document.getElementById("profile-avatar-val");
  if (avatarVal) avatarVal.value = emoji;
  renderProfileModalAvatar(emoji);

  document.querySelectorAll(".preset-avatar-btn").forEach(btn => {
    if (btn.textContent.trim() === emoji) btn.classList.add("active");
    else btn.classList.remove("active");
  });
}

function handleCustomAvatarUpload(event) {
  const file = event.target.files && event.target.files[0];
  if (!file) return;

  if (!file.type.startsWith("image/")) {
    showToast("Please select a valid image file (PNG, JPG, WebP)", "error");
    return;
  }

  const reader = new FileReader();
  reader.onload = function(e) {
    const img = new Image();
    img.onload = function() {
      // Resize to compact 260x260 square for fast loading & efficient database storage
      const canvas = document.createElement("canvas");
      const maxDim = 260;
      let width = img.width;
      let height = img.height;

      if (width > height) {
        if (width > maxDim) {
          height = Math.round((height * maxDim) / width);
          width = maxDim;
        }
      } else {
        if (height > maxDim) {
          width = Math.round((width * maxDim) / height);
          height = maxDim;
        }
      }

      canvas.width = width;
      canvas.height = height;
      const ctx = canvas.getContext("2d");
      ctx.drawImage(img, 0, 0, width, height);

      const optimizedDataUrl = canvas.toDataURL("image/jpeg", 0.85);

      const avatarVal = document.getElementById("profile-avatar-val");
      if (avatarVal) avatarVal.value = optimizedDataUrl;
      renderProfileModalAvatar(optimizedDataUrl);

      // Remove preset button active highlights
      document.querySelectorAll(".preset-avatar-btn").forEach(btn => btn.classList.remove("active"));
      showToast("Custom DP loaded! Click 'Save Profile Changes' to save.");
    };
    img.src = e.target.result;
  };
  reader.readAsDataURL(file);
}

async function saveUserProfile(event) {
  if (event) event.preventDefault();
  if (!currentUser) return;

  const btnSave = document.getElementById("btn-save-profile");
  if (btnSave) {
    btnSave.disabled = true;
    btnSave.innerHTML = `<span>⏳</span> <span>Saving Changes...</span>`;
  }

  const payload = {
    user_id: currentUser.id,
    name: (document.getElementById("profile-name")?.value || "").trim(),
    avatar: document.getElementById("profile-avatar-val")?.value || currentUser.avatar || "🎓",
    email: (document.getElementById("profile-email")?.value || "").trim(),
    phone: (document.getElementById("profile-phone")?.value || "").trim(),
    bio: (document.getElementById("profile-bio")?.value || "").trim(),
    department: (document.getElementById("profile-dept")?.value || "").trim(),
    student_id: (document.getElementById("profile-studentid")?.value || "").trim(),
    year: (document.getElementById("profile-year")?.value || "").trim(),
    skills: (document.getElementById("profile-skills")?.value || "").trim(),
    linkedin: (document.getElementById("profile-linkedin")?.value || "").trim(),
    github: (document.getElementById("profile-github")?.value || "").trim()
  };

  const newPwd = document.getElementById("profile-new-pwd")?.value;
  if (newPwd && newPwd.trim().length >= 4) {
    payload.new_password = newPwd.trim();
  }

  try {
    const res = await fetch(`${API_BASE}/api/user/profile`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const json = await res.json();

    if (json.success && json.user) {
      currentUser = json.user;
      localStorage.setItem("club_tracker_user", JSON.stringify(currentUser));
      updateUserUI();

      // If user is a student, update student welcome banner display
      const studentNameDisplay = document.getElementById("student-name-display");
      if (studentNameDisplay) studentNameDisplay.textContent = currentUser.name;

      // If database tab is active, refresh it
      if (currentTab === "database") {
        fetchDatabaseOverview();
      }

      closeModal("modal-profile");
      showToast("Profile and custom DP updated successfully! ✨", "success");
    } else {
      showToast(json.error || "Failed to update profile", "error");
    }
  } catch (err) {
    console.error("Profile save error", err);
    showToast("Server error while updating profile", "error");
  } finally {
    if (btnSave) {
      btnSave.disabled = false;
      btnSave.innerHTML = `<span>💾</span> <span>Save Profile Changes</span>`;
    }
  }
}
