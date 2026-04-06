from flask import Flask, request, redirect, url_for, render_template_string
import sqlite3
import os

app = Flask(__name__)
DB_PATH = os.path.join(os.path.expanduser("~"), "students.db")

# ─── Database Setup ────────────────────────────────────────────────────────────
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name   TEXT    NOT NULL,
            email       TEXT    NOT NULL UNIQUE,
            phone       TEXT    NOT NULL,
            dob         TEXT    NOT NULL,
            gender      TEXT    NOT NULL,
            department  TEXT    NOT NULL,
            year        TEXT    NOT NULL,
            address     TEXT,
            created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ─── HTML Templates ────────────────────────────────────────────────────────────

REGISTER_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>EduPortal — Student Registration</title>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet"/>
<style>
  :root {
    --ink:    #0d0d0d;
    --cream:  #f5f0e8;
    --gold:   #c9a84c;
    --rust:   #b84c2b;
    --teal:   #1a5f5e;
    --mist:   #e8ede9;
    --card:   #fffdf8;
  }

  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    font-family: 'DM Sans', sans-serif;
    background: var(--cream);
    min-height: 100vh;
    color: var(--ink);
    overflow-x: hidden;
  }

  /* ── Animated Background ── */
  body::before {
    content: '';
    position: fixed; inset: 0;
    background:
      radial-gradient(ellipse 80% 50% at 10% 20%, rgba(201,168,76,0.12) 0%, transparent 60%),
      radial-gradient(ellipse 60% 60% at 85% 70%, rgba(26,95,94,0.10) 0%, transparent 55%),
      radial-gradient(ellipse 50% 40% at 50% 100%, rgba(184,76,43,0.08) 0%, transparent 50%);
    z-index: -1;
    animation: bgShift 12s ease-in-out infinite alternate;
  }
  @keyframes bgShift {
    0%   { opacity: 0.7; }
    100% { opacity: 1; }
  }

  /* ── Header ── */
  header {
    padding: 2rem 3rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid rgba(201,168,76,0.3);
    animation: slideDown 0.6s ease both;
  }
  @keyframes slideDown { from { transform: translateY(-30px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }

  .logo {
    font-family: 'Playfair Display', serif;
    font-size: 1.6rem;
    font-weight: 900;
    color: var(--teal);
    letter-spacing: -0.02em;
  }
  .logo span { color: var(--gold); }

  .nav-link {
    font-size: 0.85rem;
    font-weight: 500;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--teal);
    text-decoration: none;
    padding: 0.55rem 1.4rem;
    border: 1.5px solid var(--teal);
    border-radius: 40px;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
  }
  .nav-link::before {
    content: '';
    position: absolute; inset: 0;
    background: var(--teal);
    transform: translateX(-100%);
    transition: transform 0.3s ease;
    z-index: -1;
  }
  .nav-link:hover { color: var(--cream); }
  .nav-link:hover::before { transform: translateX(0); }

  /* ── Hero ── */
  .hero {
    text-align: center;
    padding: 3.5rem 2rem 2rem;
    animation: fadeUp 0.7s 0.2s ease both;
  }
  @keyframes fadeUp { from { transform: translateY(30px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }

  .badge {
    display: inline-block;
    background: var(--gold);
    color: var(--cream);
    font-size: 0.7rem;
    font-weight: 500;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    padding: 0.35rem 1rem;
    border-radius: 40px;
    margin-bottom: 1rem;
  }

  h1 {
    font-family: 'Playfair Display', serif;
    font-size: clamp(2.2rem, 5vw, 3.5rem);
    font-weight: 900;
    line-height: 1.1;
    color: var(--ink);
    margin-bottom: 0.8rem;
  }
  h1 em { color: var(--teal); font-style: normal; }

  .subtitle {
    color: #555;
    font-size: 1rem;
    font-weight: 300;
    max-width: 420px;
    margin: 0 auto;
  }

  /* ── Flash Messages ── */
  .flash {
    max-width: 760px;
    margin: 1rem auto;
    padding: 0.9rem 1.4rem;
    border-radius: 10px;
    font-size: 0.9rem;
    font-weight: 500;
    animation: fadeUp 0.4s ease both;
  }
  .flash.error   { background: #fde8e8; color: var(--rust); border: 1px solid rgba(184,76,43,0.25); }
  .flash.success { background: #e6f4f1; color: var(--teal); border: 1px solid rgba(26,95,94,0.25); }

  /* ── Form Card ── */
  .form-wrapper {
    max-width: 820px;
    margin: 1.5rem auto 4rem;
    padding: 0 1.5rem;
    animation: fadeUp 0.8s 0.3s ease both;
  }

  .card {
    background: var(--card);
    border-radius: 24px;
    padding: 2.8rem 3rem;
    box-shadow: 0 8px 40px rgba(0,0,0,0.07), 0 1px 2px rgba(0,0,0,0.04);
    border: 1px solid rgba(201,168,76,0.15);
    position: relative;
    overflow: hidden;
  }
  .card::after {
    content: '';
    position: absolute;
    top: 0; right: 0;
    width: 200px; height: 200px;
    background: radial-gradient(circle, rgba(201,168,76,0.08) 0%, transparent 70%);
    border-radius: 50%;
    transform: translate(30%, -30%);
    pointer-events: none;
  }

  .section-title {
    font-family: 'Playfair Display', serif;
    font-size: 1rem;
    font-weight: 700;
    color: var(--teal);
    letter-spacing: 0.05em;
    text-transform: uppercase;
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin-bottom: 1.4rem;
    padding-bottom: 0.6rem;
    border-bottom: 1px solid rgba(201,168,76,0.2);
  }
  .section-title::before {
    content: '';
    display: block;
    width: 18px; height: 3px;
    background: var(--gold);
    border-radius: 2px;
  }

  .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 1.2rem; }
  .grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1.2rem; }
  .span-2 { grid-column: span 2; }
  .spacer { margin-top: 1.6rem; }

  /* ── Form Fields ── */
  .field { display: flex; flex-direction: column; gap: 0.4rem; }

  label {
    font-size: 0.78rem;
    font-weight: 500;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: #666;
  }

  input, select, textarea {
    width: 100%;
    padding: 0.75rem 1rem;
    border: 1.5px solid rgba(0,0,0,0.1);
    border-radius: 10px;
    font-family: 'DM Sans', sans-serif;
    font-size: 0.95rem;
    color: var(--ink);
    background: #fff;
    transition: border-color 0.25s, box-shadow 0.25s, transform 0.15s;
    outline: none;
    -webkit-appearance: none;
  }

  input:focus, select:focus, textarea:focus {
    border-color: var(--teal);
    box-shadow: 0 0 0 4px rgba(26,95,94,0.1);
    transform: translateY(-1px);
  }
  input:hover, select:hover, textarea:hover {
    border-color: rgba(26,95,94,0.4);
  }

  textarea { resize: vertical; min-height: 80px; }

  select {
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='8' viewBox='0 0 12 8'%3E%3Cpath d='M1 1l5 5 5-5' stroke='%231a5f5e' stroke-width='1.5' fill='none' stroke-linecap='round'/%3E%3C/svg%3E");
    background-repeat: no-repeat;
    background-position: right 1rem center;
    padding-right: 2.5rem;
    cursor: pointer;
  }

  /* ── Radio / Gender ── */
  .radio-group {
    display: flex;
    gap: 0.8rem;
    flex-wrap: wrap;
  }

  .radio-option {
    flex: 1;
    min-width: 90px;
    position: relative;
  }
  .radio-option input[type="radio"] {
    position: absolute;
    opacity: 0;
    pointer-events: none;
  }
  .radio-option label {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.4rem;
    padding: 0.7rem 1rem;
    border: 1.5px solid rgba(0,0,0,0.1);
    border-radius: 10px;
    cursor: pointer;
    font-size: 0.85rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #666;
    transition: all 0.25s;
    background: #fff;
    user-select: none;
  }
  .radio-option input:checked + label {
    border-color: var(--teal);
    background: rgba(26,95,94,0.07);
    color: var(--teal);
    font-weight: 500;
    box-shadow: 0 0 0 3px rgba(26,95,94,0.1);
  }
  .radio-option label:hover { border-color: rgba(26,95,94,0.4); }

  /* ── Submit Button ── */
  .submit-area {
    margin-top: 2rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 1rem;
  }

  .hint { font-size: 0.8rem; color: #999; }
  .hint strong { color: var(--rust); }

  .btn-submit {
    display: inline-flex;
    align-items: center;
    gap: 0.6rem;
    background: var(--teal);
    color: var(--cream);
    border: none;
    padding: 0.9rem 2.4rem;
    border-radius: 50px;
    font-family: 'DM Sans', sans-serif;
    font-size: 0.9rem;
    font-weight: 500;
    letter-spacing: 0.05em;
    cursor: pointer;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
  }
  .btn-submit::before {
    content: '';
    position: absolute; inset: 0;
    background: linear-gradient(135deg, rgba(255,255,255,0.15), transparent);
    opacity: 0;
    transition: opacity 0.3s;
  }
  .btn-submit:hover {
    background: #174f4e;
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(26,95,94,0.35);
  }
  .btn-submit:hover::before { opacity: 1; }
  .btn-submit:active { transform: translateY(0); box-shadow: none; }

  .btn-submit svg {
    transition: transform 0.3s ease;
  }
  .btn-submit:hover svg { transform: translateX(4px); }

  /* ── Progress Dots ── */
  .progress {
    display: flex;
    gap: 0.5rem;
    justify-content: center;
    margin: 0 0 2rem;
  }
  .dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    background: rgba(26,95,94,0.2);
  }
  .dot.active { background: var(--teal); width: 24px; border-radius: 4px; }

  /* ── Footer ── */
  footer {
    text-align: center;
    padding: 2rem;
    font-size: 0.8rem;
    color: #aaa;
    border-top: 1px solid rgba(0,0,0,0.06);
  }

  @media (max-width: 640px) {
    header { padding: 1.2rem 1.5rem; }
    .card  { padding: 2rem 1.5rem; }
    .grid-2, .grid-3 { grid-template-columns: 1fr; }
    .span-2 { grid-column: span 1; }
    .submit-area { flex-direction: column-reverse; align-items: stretch; }
    .btn-submit { justify-content: center; }
  }
</style>
</head>
<body>

<header>
  <div class="logo">Edu<span>Portal</span></div>
  <a href="/students" class="nav-link">View Records &rarr;</a>
</header>

<section class="hero">
  <div class="badge">✦ Academic Year 2024–25</div>
  <h1>Student <em>Registration</em></h1>
  <p class="subtitle">Fill in the details below to enrol in your chosen programme.</p>
</section>

{% if error %}
<div class="flash error">⚠ {{ error }}</div>
{% endif %}
{% if success %}
<div class="flash success">✓ {{ success }}</div>
{% endif %}

<div class="form-wrapper">
  <div class="card">
    <form method="POST" action="/register" id="regForm">

      <!-- Section 1: Personal -->
      <div class="section-title">Personal Information</div>
      <div class="grid-2">
        <div class="field">
          <label for="full_name">Full Name *</label>
          <input type="text" id="full_name" name="full_name" placeholder="e.g. Rohan Mehta" required/>
        </div>
        <div class="field">
          <label for="dob">Date of Birth *</label>
          <input type="date" id="dob" name="dob" required/>
        </div>
      </div>

      <div class="spacer"></div>
      <div class="field">
        <label>Gender *</label>
        <div class="radio-group">
          <div class="radio-option">
            <input type="radio" id="male" name="gender" value="Male" required/>
            <label for="male">♂ Male</label>
          </div>
          <div class="radio-option">
            <input type="radio" id="female" name="gender" value="Female"/>
            <label for="female">♀ Female</label>
          </div>
          <div class="radio-option">
            <input type="radio" id="other" name="gender" value="Other"/>
            <label for="other">⚧ Other</label>
          </div>
        </div>
      </div>

      <!-- Section 2: Contact -->
      <div class="section-title spacer">Contact Details</div>
      <div class="grid-2">
        <div class="field">
          <label for="email">Email Address *</label>
          <input type="email" id="email" name="email" placeholder="you@example.com" required/>
        </div>
        <div class="field">
          <label for="phone">Phone Number *</label>
          <input type="tel" id="phone" name="phone" placeholder="+91 98765 43210" required/>
        </div>
      </div>
      <div class="spacer">
        <div class="field">
          <label for="address">Residential Address</label>
          <textarea id="address" name="address" placeholder="Flat / Street / City / PIN"></textarea>
        </div>
      </div>

      <!-- Section 3: Academic -->
      <div class="section-title spacer">Academic Details</div>
      <div class="grid-2">
        <div class="field">
          <label for="department">Department *</label>
          <select id="department" name="department" required>
            <option value="" disabled selected>Select department…</option>
            <option>Computer Science &amp; Engineering</option>
            <option>Information Technology</option>
            <option>Electronics &amp; Communication</option>
            <option>Mechanical Engineering</option>
            <option>Civil Engineering</option>
            <option>Business Administration</option>
            <option>Data Science &amp; AI</option>
            <option>Biotechnology</option>
          </select>
        </div>
        <div class="field">
          <label for="year">Year of Study *</label>
          <select id="year" name="year" required>
            <option value="" disabled selected>Select year…</option>
            <option>1st Year</option>
            <option>2nd Year</option>
            <option>3rd Year</option>
            <option>4th Year</option>
          </select>
        </div>
      </div>

      <div class="submit-area">
        <p class="hint"><strong>*</strong> Required fields</p>
        <button type="submit" class="btn-submit">
          Register Now
          <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M17 8l4 4m0 0l-4 4m4-4H3"/>
          </svg>
        </button>
      </div>

    </form>
  </div>
</div>

<footer>EduPortal &copy; 2025 &mdash; Built with Flask &amp; SQLite</footer>

<script>
  // Animate inputs on focus
  document.querySelectorAll('input, select, textarea').forEach(el => {
    el.addEventListener('focus', () => el.closest('.field')?.classList.add('focused'));
    el.addEventListener('blur',  () => el.closest('.field')?.classList.remove('focused'));
  });

  // Submit button ripple effect
  document.querySelector('.btn-submit').addEventListener('click', function(e) {
    const btn = this;
    btn.style.transform = 'scale(0.97)';
    setTimeout(() => btn.style.transform = '', 150);
  });
</script>
</body>
</html>
"""


STUDENTS_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>EduPortal — Student Records</title>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=DM+Sans:wght@300;400;500&display=swap" rel="stylesheet"/>
<style>
  :root {
    --ink:   #0d0d0d;
    --cream: #f5f0e8;
    --gold:  #c9a84c;
    --rust:  #b84c2b;
    --teal:  #1a5f5e;
    --card:  #fffdf8;
  }

  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    font-family: 'DM Sans', sans-serif;
    background: var(--cream);
    color: var(--ink);
    min-height: 100vh;
  }

  body::before {
    content: '';
    position: fixed; inset: 0;
    background:
      radial-gradient(ellipse 70% 50% at 90% 10%, rgba(201,168,76,0.1) 0%, transparent 60%),
      radial-gradient(ellipse 50% 50% at 10% 80%, rgba(26,95,94,0.08) 0%, transparent 55%);
    z-index: -1;
  }

  header {
    padding: 2rem 3rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid rgba(201,168,76,0.3);
    animation: slideDown 0.5s ease both;
  }
  @keyframes slideDown { from { transform: translateY(-20px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }

  .logo {
    font-family: 'Playfair Display', serif;
    font-size: 1.6rem;
    font-weight: 900;
    color: var(--teal);
    letter-spacing: -0.02em;
  }
  .logo span { color: var(--gold); }

  .nav-link {
    font-size: 0.85rem;
    font-weight: 500;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--rust);
    text-decoration: none;
    padding: 0.55rem 1.4rem;
    border: 1.5px solid var(--rust);
    border-radius: 40px;
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
  }
  .nav-link::before {
    content: '';
    position: absolute; inset: 0;
    background: var(--rust);
    transform: translateX(-100%);
    transition: transform 0.3s ease;
    z-index: -1;
  }
  .nav-link:hover { color: #fff; }
  .nav-link:hover::before { transform: translateX(0); }

  /* ── Stats Bar ── */
  .stats-bar {
    max-width: 1200px;
    margin: 2rem auto 1.5rem;
    padding: 0 2rem;
    display: flex;
    gap: 1rem;
    flex-wrap: wrap;
    animation: fadeUp 0.6s 0.1s ease both;
  }
  @keyframes fadeUp { from { transform: translateY(20px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }

  .stat-card {
    background: var(--card);
    border: 1px solid rgba(201,168,76,0.2);
    border-radius: 16px;
    padding: 1.2rem 1.8rem;
    flex: 1;
    min-width: 160px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.05);
    transition: transform 0.2s, box-shadow 0.2s;
  }
  .stat-card:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(0,0,0,0.08); }

  .stat-label {
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #888;
    margin-bottom: 0.3rem;
  }
  .stat-value {
    font-family: 'Playfair Display', serif;
    font-size: 2rem;
    font-weight: 900;
    color: var(--teal);
    line-height: 1;
  }

  /* ── Table Section ── */
  .table-wrapper {
    max-width: 1200px;
    margin: 0 auto 4rem;
    padding: 0 2rem;
    animation: fadeUp 0.7s 0.2s ease both;
  }

  .table-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.2rem;
    flex-wrap: wrap;
    gap: 1rem;
  }

  .table-title {
    font-family: 'Playfair Display', serif;
    font-size: 1.5rem;
    font-weight: 900;
    color: var(--ink);
  }

  .search-box {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    background: var(--card);
    border: 1.5px solid rgba(0,0,0,0.1);
    border-radius: 40px;
    padding: 0.5rem 1.2rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    transition: border-color 0.25s, box-shadow 0.25s;
  }
  .search-box:focus-within {
    border-color: var(--teal);
    box-shadow: 0 0 0 4px rgba(26,95,94,0.1);
  }
  .search-box input {
    border: none;
    outline: none;
    background: transparent;
    font-family: 'DM Sans', sans-serif;
    font-size: 0.9rem;
    color: var(--ink);
    width: 220px;
  }
  .search-box svg { color: #999; flex-shrink: 0; }

  .scroll-table {
    overflow-x: auto;
    border-radius: 20px;
    box-shadow: 0 8px 40px rgba(0,0,0,0.07);
    border: 1px solid rgba(201,168,76,0.15);
  }

  table {
    width: 100%;
    border-collapse: collapse;
    background: var(--card);
    min-width: 900px;
  }

  thead {
    background: var(--teal);
    color: var(--cream);
    position: sticky;
    top: 0;
    z-index: 5;
  }
  thead th {
    padding: 1rem 1.2rem;
    font-size: 0.72rem;
    font-weight: 500;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    text-align: left;
    white-space: nowrap;
    cursor: pointer;
    user-select: none;
    transition: background 0.2s;
  }
  thead th:hover { background: rgba(255,255,255,0.1); }
  thead th:first-child { border-radius: 20px 0 0 0; }
  thead th:last-child  { border-radius: 0 20px 0 0; }

  tbody tr {
    border-bottom: 1px solid rgba(0,0,0,0.05);
    transition: background 0.2s, transform 0.15s;
  }
  tbody tr:last-child { border-bottom: none; }
  tbody tr:hover {
    background: rgba(26,95,94,0.04);
  }
  tbody tr:nth-child(even) { background: rgba(201,168,76,0.03); }
  tbody tr:nth-child(even):hover { background: rgba(26,95,94,0.04); }

  td {
    padding: 0.95rem 1.2rem;
    font-size: 0.88rem;
    color: #333;
    vertical-align: middle;
    white-space: nowrap;
  }

  .id-badge {
    display: inline-block;
    background: rgba(26,95,94,0.1);
    color: var(--teal);
    font-size: 0.75rem;
    font-weight: 600;
    padding: 0.2rem 0.6rem;
    border-radius: 6px;
    font-family: monospace;
  }

  .dept-chip {
    display: inline-block;
    background: rgba(201,168,76,0.12);
    color: #8a6a20;
    font-size: 0.75rem;
    padding: 0.25rem 0.7rem;
    border-radius: 20px;
    font-weight: 500;
    max-width: 200px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .year-chip {
    display: inline-block;
    background: rgba(184,76,43,0.1);
    color: var(--rust);
    font-size: 0.75rem;
    padding: 0.25rem 0.7rem;
    border-radius: 20px;
    font-weight: 500;
  }

  .gender-chip {
    display: inline-block;
    font-size: 0.75rem;
    padding: 0.25rem 0.7rem;
    border-radius: 20px;
    font-weight: 500;
  }
  .gender-male   { background: rgba(26,95,94,0.08); color: var(--teal); }
  .gender-female { background: rgba(201,168,76,0.12); color: #8a6a20; }
  .gender-other  { background: rgba(184,76,43,0.08); color: var(--rust); }

  /* ── Empty State ── */
  .empty {
    text-align: center;
    padding: 5rem 2rem;
    background: var(--card);
    border-radius: 20px;
    border: 1px dashed rgba(26,95,94,0.25);
  }
  .empty-icon { font-size: 3rem; margin-bottom: 1rem; }
  .empty h2 {
    font-family: 'Playfair Display', serif;
    font-size: 1.4rem;
    color: var(--teal);
    margin-bottom: 0.5rem;
  }
  .empty p { color: #888; font-size: 0.9rem; margin-bottom: 1.5rem; }
  .empty a {
    display: inline-block;
    background: var(--teal);
    color: var(--cream);
    text-decoration: none;
    padding: 0.7rem 1.8rem;
    border-radius: 40px;
    font-size: 0.85rem;
    font-weight: 500;
    transition: all 0.3s;
  }
  .empty a:hover { background: #174f4e; transform: translateY(-2px); box-shadow: 0 8px 20px rgba(26,95,94,0.3); }

  footer {
    text-align: center;
    padding: 2rem;
    font-size: 0.8rem;
    color: #aaa;
    border-top: 1px solid rgba(0,0,0,0.06);
  }

  @media (max-width: 640px) {
    header { padding: 1.2rem 1.5rem; }
    .stats-bar, .table-wrapper { padding: 0 1rem; }
  }
</style>
</head>
<body>

<header>
  <div class="logo">Edu<span>Portal</span></div>
  <a href="/" class="nav-link">&larr; Register Student</a>
</header>

<div class="stats-bar">
  <div class="stat-card">
    <div class="stat-label">Total Students</div>
    <div class="stat-value">{{ students|length }}</div>
  </div>
  {% set depts = students|map(attribute='department')|list|unique|list %}
  <div class="stat-card">
    <div class="stat-label">Departments</div>
    <div class="stat-value">{{ depts|length }}</div>
  </div>
  {% set latest = students[0].created_at[:10] if students else '—' %}
  <div class="stat-card">
    <div class="stat-label">Latest Entry</div>
    <div class="stat-value" style="font-size:1.1rem; padding-top:0.5rem;">{{ latest }}</div>
  </div>
</div>

<div class="table-wrapper">
  <div class="table-header">
    <h2 class="table-title">Registered Students</h2>
    <div class="search-box">
      <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
        <circle cx="11" cy="11" r="8"/><path stroke-linecap="round" d="M21 21l-4.35-4.35"/>
      </svg>
      <input type="text" id="searchInput" placeholder="Search name, email, dept…"/>
    </div>
  </div>

  {% if students %}
  <div class="scroll-table">
    <table id="studentTable">
      <thead>
        <tr>
          <th onclick="sortTable(0)">#</th>
          <th onclick="sortTable(1)">Name ↕</th>
          <th onclick="sortTable(2)">Email</th>
          <th onclick="sortTable(3)">Phone</th>
          <th onclick="sortTable(4)">DOB</th>
          <th onclick="sortTable(5)">Gender</th>
          <th onclick="sortTable(6)">Department ↕</th>
          <th onclick="sortTable(7)">Year ↕</th>
          <th onclick="sortTable(8)">Registered</th>
        </tr>
      </thead>
      <tbody id="tableBody">
        {% for s in students %}
        <tr>
          <td><span class="id-badge">{{ '%03d' % s.id }}</span></td>
          <td><strong>{{ s.full_name }}</strong></td>
          <td>{{ s.email }}</td>
          <td>{{ s.phone }}</td>
          <td>{{ s.dob }}</td>
          <td>
            <span class="gender-chip gender-{{ s.gender|lower }}">{{ s.gender }}</span>
          </td>
          <td><span class="dept-chip">{{ s.department }}</span></td>
          <td><span class="year-chip">{{ s.year }}</span></td>
          <td>{{ s.created_at[:10] }}</td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
  </div>
  {% else %}
  <div class="empty">
    <div class="empty-icon">📋</div>
    <h2>No students registered yet</h2>
    <p>Be the first to add a student record to the portal.</p>
    <a href="/">Register First Student</a>
  </div>
  {% endif %}
</div>

<footer>EduPortal &copy; 2025 &mdash; {{ students|length }} record(s) in database</footer>

<script>
  // ── Live Search ──
  document.getElementById('searchInput').addEventListener('input', function() {
    const q = this.value.toLowerCase();
    document.querySelectorAll('#tableBody tr').forEach(row => {
      row.style.display = row.textContent.toLowerCase().includes(q) ? '' : 'none';
    });
  });

  // ── Column Sort ──
  let sortDir = {};
  function sortTable(col) {
    const tbody = document.getElementById('tableBody');
    const rows  = Array.from(tbody.querySelectorAll('tr'));
    sortDir[col] = !sortDir[col];
    rows.sort((a, b) => {
      const va = a.cells[col].textContent.trim().toLowerCase();
      const vb = b.cells[col].textContent.trim().toLowerCase();
      return sortDir[col] ? va.localeCompare(vb) : vb.localeCompare(va);
    });
    rows.forEach(r => tbody.appendChild(r));
  }

  // ── Row hover sparkle ──
  document.querySelectorAll('#tableBody tr').forEach((row, i) => {
    row.style.animationDelay = (i * 0.04) + 's';
    row.style.animation = 'fadeUp 0.4s ease both';
  });
</script>
</body>
</html>
"""


# ─── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template_string(REGISTER_HTML)


@app.route("/register", methods=["POST"])
def register():
    data = {
        "full_name":  request.form.get("full_name", "").strip(),
        "email":      request.form.get("email", "").strip().lower(),
        "phone":      request.form.get("phone", "").strip(),
        "dob":        request.form.get("dob", "").strip(),
        "gender":     request.form.get("gender", "").strip(),
        "department": request.form.get("department", "").strip(),
        "year":       request.form.get("year", "").strip(),
        "address":    request.form.get("address", "").strip(),
    }

    missing = [k for k, v in data.items() if k != "address" and not v]
    if missing:
        return render_template_string(REGISTER_HTML,
            error="Please fill in all required fields: " + ", ".join(missing))

    try:
        conn = get_db()
        conn.execute("""
            INSERT INTO students (full_name, email, phone, dob, gender, department, year, address)
            VALUES (:full_name, :email, :phone, :dob, :gender, :department, :year, :address)
        """, data)
        conn.commit()
        conn.close()
    except sqlite3.IntegrityError:
        return render_template_string(REGISTER_HTML,
            error="A student with this email is already registered.")
    except Exception as e:
        return render_template_string(REGISTER_HTML,
            error=f"Database error: {str(e)}")

    return render_template_string(REGISTER_HTML,
        success=f"🎉 {data['full_name']} has been successfully registered!")


@app.route("/students")
def students():
    conn = get_db()
    rows = conn.execute("SELECT * FROM students ORDER BY id DESC").fetchall()
    conn.close()
    return render_template_string(STUDENTS_HTML, students=rows)


# ─── Main ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    init_db()
    print("\n" + "="*55)
    print("  🎓  EduPortal is running!")
    print("  ➜   Registration : http://127.0.0.1:5000/")
    print("  ➜   View Records  : http://127.0.0.1:5000/students")
    print("="*55 + "\n")
    app.run(host="0.0.0.0", port=5000)
