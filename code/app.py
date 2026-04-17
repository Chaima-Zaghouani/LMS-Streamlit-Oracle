import streamlit as st
import pandas as pd
import oracledb
from datetime import date
from contextlib import contextmanager

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Library Management System",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# FIXED ORACLE DSN
# ============================================================
DEFAULT_DSN = "oracle.csep.umflint.edu:1521/csep"

# ============================================================
# DESIGN SYSTEM & CSS
# ============================================================
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Syne:wght@400;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">

<style>
/* ── TOKENS ──────────────────────────────────────────────── */
:root {
    --bg:           #080d14;
    --bg-mesh:      radial-gradient(ellipse 90% 60% at 60% -5%, rgba(234,179,8,0.07) 0%, transparent 65%),
                    radial-gradient(ellipse 50% 40% at 10% 80%, rgba(59,130,246,0.05) 0%, transparent 55%);
    --surface:      #0f1824;
    --surface-2:    #162030;
    --surface-3:    #1d2a3d;
    --border:       rgba(255,255,255,0.06);
    --border-hover: rgba(255,255,255,0.12);
    --gold:         #eab308;
    --gold-dim:     rgba(234,179,8,0.10);
    --gold-glow:    rgba(234,179,8,0.25);
    --blue:         #3b82f6;
    --blue-dim:     rgba(59,130,246,0.10);
    --teal:         #14b8a6;
    --emerald:      #10b981;
    --rose:         #f43f5e;
    --violet:       #8b5cf6;
    --text:         #f8fafc;
    --text-2:       #cbd5e1;
    --text-3:       #94a3b8;
    --radius-sm:    10px;
    --radius:       16px;
    --radius-lg:    22px;
    --radius-xl:    28px;
    --shadow:       0 4px 24px rgba(0,0,0,0.4);
    --shadow-lg:    0 12px 48px rgba(0,0,0,0.5);
    --ease:         cubic-bezier(0.16,1,0.3,1);
    --dur:          240ms;
}

/* ── BASE ────────────────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; }

html, body, [class*="css"] {
    font-family: 'Syne', sans-serif !important;
    color: var(--text) !important;
}

.stApp {
    background: var(--bg) !important;
    background-image: var(--bg-mesh) !important;
}

/* grain overlay */
.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)' opacity='0.025'/%3E%3C/svg%3E");
    pointer-events: none;
    z-index: 0;
    opacity: 0.6;
}

[data-testid="stHeader"] { background: transparent !important; height: 0 !important; }

.block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 3rem !important;
    max-width: 1440px !important;
    position: relative;
    z-index: 1;
}

/* ── SIDEBAR ─────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
    min-width: 300px !important;
    max-width: 300px !important;
}

[data-testid="stSidebar"] > div {
    padding: 1.5rem 1.25rem !important;
}

.sidebar-brand {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 1.5rem;
}

.sidebar-logo {
    width: 44px; height: 44px;
    background: linear-gradient(135deg, var(--gold), #d97706);
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.3rem;
    box-shadow: 0 6px 20px var(--gold-glow);
    flex-shrink: 0;
}

.sidebar-brand-text { line-height: 1.2; }

.sidebar-brand-name {
    font-family: 'Playfair Display', serif;
    font-size: 1.05rem;
    font-weight: 900;
    color: var(--text) !important;
}

.sidebar-brand-sub {
    font-size: 0.72rem;
    color: #7c93a8 !important;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}

.sidebar-divider {
    height: 1px;
    background: var(--border);
    margin: 1rem 0;
}

.conn-status-connected {
    display: flex; align-items: center; gap: 0.6rem;
    padding: 0.65rem 1rem;
    background: rgba(16,185,129,0.08);
    border: 1px solid rgba(16,185,129,0.2);
    border-radius: var(--radius-sm);
    font-size: 0.82rem; font-weight: 700;
    color: var(--emerald) !important;
    margin-bottom: 0.75rem;
}

.conn-dot {
    width: 7px; height: 7px;
    background: var(--emerald);
    border-radius: 50%;
    animation: pulse-dot 2s ease-in-out infinite;
}

@keyframes pulse-dot {
    0%,100% { box-shadow: 0 0 0 0 rgba(16,185,129,0.5); }
    50%      { box-shadow: 0 0 0 5px rgba(16,185,129,0); }
}

.nav-section-label {
    font-size: 0.68rem;
    font-weight: 800;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #7c93a8 !important;
    padding: 0.9rem 0 0.4rem;
}

/* ── TYPOGRAPHY ──────────────────────────────────────────── */
h1, h2, h3 {
    font-family: 'Playfair Display', serif !important;
    color: var(--text) !important;
    letter-spacing: -0.01em;
}

h2 { font-size: 1.7rem !important; font-weight: 900 !important; }
h3 { font-size: 1.25rem !important; }

.section-note {
    color: #b0bfcf !important;
    font-size: 0.95rem !important;
    font-weight: 600;
    margin: -0.25rem 0 1.25rem;
    line-height: 1.6;
}

/* ── HERO ────────────────────────────────────────────────── */
.hero-wrap {
    position: relative;
    background: linear-gradient(135deg, rgba(234,179,8,0.08) 0%, rgba(59,130,246,0.04) 100%);
    border: 1px solid rgba(234,179,8,0.18);
    border-radius: var(--radius-xl);
    padding: 1.75rem 2rem;
    display: flex;
    align-items: center;
    gap: 1.5rem;
    overflow: hidden;
    margin-bottom: 1.25rem;
    animation: fadeUp 0.55s var(--ease) both;
}

.hero-wrap::before {
    content: '';
    position: absolute;
    top: -40px; right: -40px;
    width: 200px; height: 200px;
    background: radial-gradient(circle, rgba(234,179,8,0.08), transparent 70%);
    pointer-events: none;
}

.hero-icon {
    font-size: 3.25rem;
    line-height: 1;
    filter: drop-shadow(0 0 20px var(--gold-glow));
    animation: float 5s ease-in-out infinite;
    flex-shrink: 0;
}

@keyframes float {
    0%,100% { transform: translateY(0) rotate(-2deg); }
    50%      { transform: translateY(-8px) rotate(2deg); }
}

.hero-eyebrow {
    font-size: 0.72rem;
    font-weight: 800;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--gold) !important;
    margin-bottom: 0.3rem;
}

.hero-title {
    font-family: 'Playfair Display', serif;
    font-size: 2.1rem;
    font-weight: 900;
    color: var(--text) !important;
    line-height: 1.05;
    margin-bottom: 0.4rem;
}

.hero-sub {
    color: #b8cad9 !important;
    font-size: 0.95rem;
    font-weight: 500;
    line-height: 1.65;
    max-width: 560px;
}

.hero-live {
    margin-left: auto;
    display: flex; align-items: center; gap: 0.5rem;
    padding: 0.5rem 1rem;
    background: rgba(16,185,129,0.08);
    border: 1px solid rgba(16,185,129,0.2);
    border-radius: 999px;
    font-size: 0.78rem; font-weight: 800;
    color: var(--emerald) !important;
    white-space: nowrap;
    flex-shrink: 0;
}

.live-dot {
    width: 6px; height: 6px;
    background: var(--emerald); border-radius: 50%;
    animation: pulse-dot 2s ease-in-out infinite;
}

/* ── METRIC CARDS ────────────────────────────────────────── */
.metric-card {
    position: relative;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 1.35rem 1.25rem 1.15rem;
    overflow: hidden;
    transition: transform var(--dur) var(--ease), box-shadow var(--dur) var(--ease), border-color var(--dur);
    animation: fadeUp 0.5s var(--ease) both;
}

.metric-card:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow-lg), 0 0 0 1px var(--mc-color);
    border-color: var(--mc-color);
}

.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 2px;
    background: var(--mc-color);
    border-radius: var(--radius-lg) var(--radius-lg) 0 0;
}

.metric-card::after {
    content: '';
    position: absolute;
    bottom: -30px; right: -30px;
    width: 80px; height: 80px;
    background: radial-gradient(circle, color-mix(in srgb, var(--mc-color) 15%, transparent), transparent 70%);
    pointer-events: none;
}

.mc-icon { font-size: 1.4rem; margin-bottom: 0.6rem; }

.mc-label {
    font-size: 0.78rem !important;
    font-weight: 800;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #94a3b8 !important;
    margin-bottom: 0.35rem;
}

.mc-value {
    font-family: 'JetBrains Mono', monospace !important;
    font-size: 2.2rem !important;
    font-weight: 700 !important;
    color: var(--text) !important;
    line-height: 1;
}

/* ── MODULE GRID ─────────────────────────────────────────── */
.module-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
    margin-top: 1.25rem;
}

.module-card {
    background: var(--surface-2);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 1.2rem 1.1rem;
    transition: all var(--dur) var(--ease);
    cursor: default;
}

.module-card:hover {
    border-color: var(--border-hover);
    background: var(--surface-3);
    transform: translateY(-2px);
}

.module-icon { font-size: 1.5rem; margin-bottom: 0.5rem; }

.module-name {
    font-size: 0.92rem;
    font-weight: 800;
    color: var(--text) !important;
    margin-bottom: 0.3rem;
}

.module-desc {
    font-size: 0.82rem;
    color: #a8bbd0 !important;
    line-height: 1.55;
}

/* ── SECTION CARD ────────────────────────────────────────── */
.section-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-xl);
    padding: 1.5rem 1.5rem 1rem;
    margin-top: 0.5rem;
    animation: fadeUp 0.4s var(--ease) 0.1s both;
}

/* ── TOAST NOTIFICATIONS ─────────────────────────────────── */
.toast {
    display: flex; align-items: center; gap: 0.75rem;
    padding: 1rem 1.25rem;
    background: var(--surface-2);
    border: 1px solid var(--border);
    border-left: 3px solid;
    border-radius: var(--radius);
    font-size: 0.92rem; font-weight: 600;
    animation: slideInRight 0.35s var(--ease);
    margin-top: 0.75rem;
}

.toast-icon { font-size: 1.1rem; flex-shrink: 0; }

@keyframes slideInRight {
    from { opacity: 0; transform: translateX(16px); }
    to   { opacity: 1; transform: translateX(0); }
}

/* ── EMPTY STATE ─────────────────────────────────────────── */
.empty-state {
    display: flex; flex-direction: column; align-items: center;
    padding: 3rem 1rem;
    border: 1px dashed rgba(255,255,255,0.08);
    border-radius: var(--radius-lg);
    text-align: center;
    animation: fadeUp 0.4s var(--ease);
}

.empty-emoji { font-size: 2.75rem; margin-bottom: 0.75rem; opacity: 0.5; }

.empty-label {
    font-size: 0.9rem; font-weight: 700;
    color: #94a3b8 !important;
}

/* ── FORM OVERRIDES ──────────────────────────────────────── */
div[data-testid="stForm"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-xl) !important;
    padding: 1.5rem 1.25rem 1rem !important;
    box-shadow: var(--shadow) !important;
}

.stTextInput input,
.stNumberInput input,
.stDateInput input {
    background: var(--surface-2) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text) !important;
    font-family: 'Syne', sans-serif !important;
    font-size: 0.95rem !important;
    transition: border-color var(--dur), box-shadow var(--dur) !important;
}

.stTextInput input:focus,
.stNumberInput input:focus {
    border-color: var(--gold) !important;
    box-shadow: 0 0 0 3px var(--gold-dim) !important;
    outline: none !important;
}

.stTextInput label,
.stNumberInput label,
.stDateInput label,
.stSelectbox label,
.stRadio label {
    color: #a8bbd0 !important;
    font-size: 0.82rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.04em !important;
    text-transform: uppercase !important;
}

.stSelectbox > div > div {
    background: var(--surface-2) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text) !important;
}

/* ── BUTTONS ─────────────────────────────────────────────── */
.stButton > button {
    background: linear-gradient(135deg, var(--gold) 0%, #ca8a04 100%) !important;
    color: #0a0a0a !important;
    border: none !important;
    border-radius: var(--radius) !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 800 !important;
    font-size: 0.92rem !important;
    padding: 0.75rem 1.1rem !important;
    width: 100% !important;
    letter-spacing: 0.02em !important;
    box-shadow: 0 6px 20px var(--gold-glow) !important;
    transition: all var(--dur) var(--ease) !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 10px 28px rgba(234,179,8,0.4) !important;
}

.stButton > button:active {
    transform: translateY(0) !important;
}

/* Connect button — green */
.btn-connect .stButton > button {
    background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%) !important;
    box-shadow: 0 6px 20px rgba(34,197,94,0.3) !important;
}

/* Disconnect button — subtle red */
.btn-disconnect .stButton > button {
    background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%) !important;
    color: white !important;
    box-shadow: 0 6px 20px rgba(239,68,68,0.25) !important;
}

/* ── DATAFRAME ───────────────────────────────────────────── */
div[data-testid="stDataFrame"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-lg) !important;
    overflow: hidden !important;
}

/* ── RADIO / SELECTBOX ───────────────────────────────────── */
.stRadio > div {
    gap: 0.35rem !important;
}

.stRadio > div > label {
    background: var(--surface-2) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    padding: 0.5rem 0.75rem !important;
    transition: all var(--dur) var(--ease) !important;
    color: var(--text) !important;
    font-size: 0.88rem !important;
    font-weight: 600 !important;
    text-transform: none !important;
    letter-spacing: 0 !important;
}

.stRadio > div > label:hover {
    border-color: var(--border-hover) !important;
    background: var(--surface-3) !important;
}

/* ── SELECTBOX ───────────────────────────────────────────── */
.stSelectbox > div[data-baseweb="select"] > div {
    background: var(--surface-2) !important;
    border-color: var(--border) !important;
    color: var(--text) !important;
}

/* ── SIDEBAR INPUTS ──────────────────────────────────────── */
[data-testid="stSidebar"] .stTextInput input,
[data-testid="stSidebar"] .stTextInput input[type="password"] {
    background: var(--surface-2) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text) !important;
}

/* ── ANIMATIONS ──────────────────────────────────────────── */
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(18px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* Stagger main children */
.block-container > div:nth-child(1) { animation: fadeUp 0.45s var(--ease) 0ms both; }
.block-container > div:nth-child(2) { animation: fadeUp 0.45s var(--ease) 60ms both; }
.block-container > div:nth-child(3) { animation: fadeUp 0.45s var(--ease) 120ms both; }
.block-container > div:nth-child(4) { animation: fadeUp 0.45s var(--ease) 180ms both; }
.block-container > div:nth-child(5) { animation: fadeUp 0.45s var(--ease) 240ms both; }

/* ── MISC ────────────────────────────────────────────────── */
hr { border-color: var(--border) !important; margin: 1rem 0; }

::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--surface); }
::-webkit-scrollbar-thumb { background: var(--surface-3); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--text-3); }

p { color: #c0cdd9 !important; }
</style>
""", unsafe_allow_html=True)


# ============================================================
# DB HELPERS
# ============================================================
def get_connection(user: str, password: str, dsn: str):
    return oracledb.connect(user=user, password=password, dsn=dsn)


@contextmanager
def get_cursor(conn):
    cur = conn.cursor()
    try:
        yield cur
    finally:
        cur.close()


def run_select(conn, sql: str, params=None) -> pd.DataFrame:
    with get_cursor(conn) as cur:
        cur.execute(sql, params or {})
        cols = [d[0] for d in cur.description]
        rows = cur.fetchall()
    return pd.DataFrame(rows, columns=cols)


def run_dml(conn, sql: str, params=None) -> None:
    with get_cursor(conn) as cur:
        cur.execute(sql, params or {})
    conn.commit()


def run_multi_dml(conn, statements) -> None:
    with get_cursor(conn) as cur:
        for sql, params in statements:
            cur.execute(sql, params or {})
    conn.commit()


# ============================================================
# SQL
# ============================================================
SQL = {
    "count_readers": "SELECT COUNT(*) AS TOTAL_READERS FROM Readers",
    "count_books": "SELECT COUNT(*) AS TOTAL_BOOKS FROM Books",
    "count_copies": "SELECT COUNT(*) AS TOTAL_COPIES FROM Book_Copies",
    "count_active_borrows": "SELECT COUNT(*) AS ACTIVE_BORROWS FROM Transactions WHERE Status = 'Active'",
    "count_active_reservations": "SELECT COUNT(*) AS ACTIVE_RESERVATIONS FROM Reservations WHERE Status = 'Active'",

    "search_reader": """
        SELECT Member_ID, Name, Email, Phone_Number, Address,
               Membership_Date, Account_Status, Current_Fine_Balance
        FROM Readers WHERE Member_ID = :member_id
    """,
    "search_books_by_title": """
        SELECT Book_ID, ISBN, Title, Author, Edition, Category,
               Language, Publication_Year, Series_ID
        FROM Books WHERE LOWER(Title) LIKE LOWER(:title_keyword) ORDER BY Title
    """,
    "show_copies": """
        SELECT Copy_ID, Status, Acquisition_Date, Shelf_Location, Book_ID
        FROM Book_Copies WHERE Book_ID = :book_id ORDER BY Copy_ID
    """,
    "available_books": """
        SELECT DISTINCT b.Book_ID, b.Title FROM Books b, Book_Copies bc
        WHERE b.Book_ID = bc.Book_ID AND bc.Status = 'Available' ORDER BY b.Title
    """,

    "add_reader": """
        INSERT INTO Readers (Member_ID, Name, Email, Phone_Number, Address,
            Membership_Date, Account_Status, Current_Fine_Balance)
        VALUES (:member_id, :name, :email, :phone_number, :address,
            :membership_date, :account_status, :fine_balance)
    """,
    "add_book": """
        INSERT INTO Books (Book_ID, ISBN, Title, Author, Edition, Category,
            Language, Publication_Year, Series_ID)
        VALUES (:book_id, :isbn, :title, :author, :edition, :category,
            :language, :publication_year, :series_id)
    """,
    "add_copy": """
        INSERT INTO Book_Copies (Copy_ID, Status, Acquisition_Date, Shelf_Location, Book_ID)
        VALUES (:copy_id, :status, :acquisition_date, :shelf_location, :book_id)
    """,

    "insert_transaction": """
        INSERT INTO Transactions (Transaction_ID, Borrow_Date, Due_Date, Return_Date,
            Status, Member_ID, Copy_ID, Staff_ID)
        VALUES (:transaction_id, SYSDATE, SYSDATE + 14, NULL, 'Active',
            :member_id, :copy_id, :staff_id)
    """,
    "mark_copy_borrowed": "UPDATE Book_Copies SET Status = 'Borrowed' WHERE Copy_ID = :copy_id",
    "mark_transaction_returned": """
        UPDATE Transactions SET Return_Date = SYSDATE, Status = 'Returned'
        WHERE Transaction_ID = :transaction_id
    """,
    "mark_copy_available": "UPDATE Book_Copies SET Status = 'Available' WHERE Copy_ID = :copy_id",
    "insert_fine_auto": """
        INSERT INTO Fines (Fine_ID, Fine_Amount, Fine_Date, Payment_Status, Payment_Date, Transaction_ID)
        SELECT :fine_id, ROUND((Return_Date - Due_Date) * 0.5, 2), SYSDATE, 'Unpaid', NULL, Transaction_ID
        FROM Transactions
        WHERE Return_Date > Due_Date AND Transaction_ID = :transaction_id
          AND NOT EXISTS (SELECT 1 FROM Fines f WHERE f.Transaction_ID = Transactions.Transaction_ID)
    """,
    "update_fine_balance": """
        UPDATE Readers r
        SET Current_Fine_Balance = (
            SELECT NVL(SUM(f.Fine_Amount), 0) FROM Transactions t, Fines f
            WHERE t.Transaction_ID = f.Transaction_ID AND t.Member_ID = r.Member_ID
              AND f.Payment_Status = 'Unpaid')
        WHERE r.Member_ID = :member_id
    """,
    "check_suspension": "SELECT Account_Status FROM Readers WHERE Member_ID = :member_id",
    "borrow_limit": "SELECT COUNT(*) AS ACTIVE_BORROWS FROM Transactions WHERE Member_ID = :member_id AND Status = 'Active'",
    "copy_status": "SELECT Status FROM Book_Copies WHERE Copy_ID = :copy_id",
    "transaction_member": "SELECT Member_ID FROM Transactions WHERE Transaction_ID = :transaction_id",

    "place_reservation": """
        INSERT INTO Reservations (Reservation_ID, Reservation_Date, Expiry_Date, Status, Member_ID, Book_ID)
        VALUES (:reservation_id, SYSDATE, SYSDATE + 7, 'Active', :member_id, :book_id)
    """,
    "cancel_reservation": "UPDATE Reservations SET Status = 'Cancelled' WHERE Reservation_ID = :reservation_id",
    "expire_reservations": "UPDATE Reservations SET Status = 'Expired' WHERE Expiry_Date < SYSDATE AND Status = 'Active'",

    "overdue": """
        SELECT t.Transaction_ID, r.Member_ID, r.Name, b.Title,
               t.Borrow_Date, t.Due_Date,
               ROUND(SYSDATE - t.Due_Date) AS Days_Overdue
        FROM Transactions t, Readers r, Book_Copies bc, Books b
        WHERE t.Member_ID = r.Member_ID AND t.Copy_ID = bc.Copy_ID
          AND bc.Book_ID = b.Book_ID AND t.Status = 'Active' AND t.Due_Date < SYSDATE
        ORDER BY Days_Overdue DESC
    """,
    "unpaid_fines": """
        SELECT r.Member_ID, r.Name, SUM(f.Fine_Amount) AS Total_Unpaid
        FROM Readers r, Transactions t, Fines f
        WHERE r.Member_ID = t.Member_ID AND t.Transaction_ID = f.Transaction_ID
          AND f.Payment_Status = 'Unpaid'
        GROUP BY r.Member_ID, r.Name ORDER BY Total_Unpaid DESC
    """,
    "most_borrowed": """
        SELECT b.Title, COUNT(t.Transaction_ID) AS Borrow_Count
        FROM Books b, Book_Copies bc, Transactions t
        WHERE b.Book_ID = bc.Book_ID AND bc.Copy_ID = t.Copy_ID
        GROUP BY b.Title ORDER BY Borrow_Count DESC, b.Title
    """,
    "never_borrowed": """
        SELECT r.Member_ID, r.Name FROM Readers r
        WHERE NOT EXISTS (SELECT 1 FROM Transactions t WHERE t.Member_ID = r.Member_ID)
        ORDER BY r.Member_ID
    """,
    "top_fines": """
        SELECT r.Name, SUM(f.Fine_Amount) AS Total_Fines
        FROM Readers r, Transactions t, Fines f
        WHERE r.Member_ID = t.Member_ID AND t.Transaction_ID = f.Transaction_ID
        GROUP BY r.Name ORDER BY Total_Fines DESC, r.Name
    """,
    "delete_damaged": "DELETE FROM Book_Copies WHERE Status = 'Damaged'",
}


# ============================================================
# UI HELPERS
# ============================================================
def metric_card(label: str, value, icon: str = "●", color: str = "#eab308"):
    st.markdown(f"""
    <div class="metric-card" style="--mc-color:{color}">
        <div class="mc-icon">{icon}</div>
        <div class="mc-label">{label}</div>
        <div class="mc-value">{value:,}</div>
    </div>
    """, unsafe_allow_html=True)


def show_dataframe(df: pd.DataFrame, empty_message: str = "No records found."):
    if df.empty:
        st.markdown(f"""
        <div class="empty-state">
            <div class="empty-emoji">🔍</div>
            <div class="empty-label">{empty_message}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)


def toast(message: str, kind: str = "success"):
    cfg = {
        "success": ("#10b981", "✓"),
        "error":   ("#f43f5e", "✕"),
        "info":    ("#3b82f6", "ℹ"),
        "warn":    ("#f59e0b", "⚠"),
    }.get(kind, ("#10b981", "✓"))
    color, icon = cfg
    st.markdown(f"""
    <div class="toast" style="border-left-color:{color}">
        <span class="toast-icon" style="color:{color}">{icon}</span>
        <span>{message}</span>
    </div>
    """, unsafe_allow_html=True)


def section_header(title: str, note: str = ""):
    st.subheader(title)
    if note:
        st.markdown(f'<div class="section-note">{note}</div>', unsafe_allow_html=True)


def render_hero(connected: bool = False):
    badge = ""
    if connected:
        badge = '<div class="hero-live"><div class="live-dot"></div>ORACLE LIVE</div>'
    st.markdown(f"""
    <div class="hero-wrap">
        <div class="hero-icon">📚</div>
        <div>
            <div class="hero-eyebrow">UM-Flint · CSEP Oracle</div>
            <div class="hero-title">Library Management</div>
            <div class="hero-sub">
                Full-stack Oracle dashboard for readers, books, circulation,
                reservations, fines, analytics, and admin operations.
            </div>
        </div>
        {badge}
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# CONNECTION PANEL
# ============================================================
def ensure_connection():
    # Sidebar branding
    st.sidebar.markdown("""
    <div class="sidebar-brand">
        <div class="sidebar-logo">📚</div>
        <div class="sidebar-brand-text">
            <div class="sidebar-brand-name">LMS Portal</div>
            <div class="sidebar-brand-sub">UM-Flint Oracle</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.sidebar.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
    st.sidebar.markdown('<div class="nav-section-label">Database Connection</div>', unsafe_allow_html=True)

    user = st.sidebar.text_input("Username", placeholder="your_username")
    password = st.sidebar.text_input("Password", type="password", placeholder="••••••••")

    col_a, col_b = st.sidebar.columns(2)
    with col_a:
        st.markdown('<div class="btn-connect">', unsafe_allow_html=True)
        connect_clicked = st.button("Connect", key="btn_connect")
        st.markdown('</div>', unsafe_allow_html=True)
    with col_b:
        st.markdown('<div class="btn-disconnect">', unsafe_allow_html=True)
        disconnect_clicked = st.button("Disconnect", key="btn_disconnect")
        st.markdown('</div>', unsafe_allow_html=True)

    if disconnect_clicked:
        st.session_state.pop("conn_cfg", None)
        st.sidebar.info("Disconnected from database.")

    if connect_clicked:
        if not user or not password:
            st.sidebar.warning("Please enter both username and password.")
        else:
            try:
                test_conn = get_connection(user, password, DEFAULT_DSN)
                test_conn.close()
                st.session_state["conn_cfg"] = {
                    "user": user, "password": password, "dsn": DEFAULT_DSN
                }
                st.sidebar.success("Connected successfully.")
            except Exception as e:
                st.sidebar.error(f"Connection failed: {e}")

    cfg = st.session_state.get("conn_cfg")
    if not cfg:
        render_hero(connected=False)
        st.markdown("""
        <div class="empty-state" style="margin-top:2rem; border-color: rgba(234,179,8,0.15)">
            <div class="empty-emoji" style="opacity:0.7">🔐</div>
            <div class="empty-label" style="font-size:1rem">Enter your Oracle credentials in the sidebar to get started.</div>
        </div>
        """, unsafe_allow_html=True)
        st.stop()

    try:
        return get_connection(**cfg)
    except Exception as e:
        st.error(f"Could not open database connection: {e}")
        st.stop()


# ============================================================
# MAIN
# ============================================================
conn = ensure_connection()

# Render hero (connected state)
render_hero(connected=True)

# Connected status in sidebar
st.sidebar.markdown("""
<div class="conn-status-connected">
    <div class="conn-dot"></div>
    Connected to Oracle
</div>
""", unsafe_allow_html=True)
st.sidebar.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)
st.sidebar.markdown('<div class="nav-section-label">Navigation</div>', unsafe_allow_html=True)

group = st.sidebar.selectbox(
    "Module",
    ["Home Dashboard", "Search & View", "Add Records",
     "Circulation", "Reservations", "Reports & Analytics", "Admin Tools"],
    label_visibility="collapsed",
)

if group == "Home Dashboard":
    operation = "Home"
elif group == "Search & View":
    operation = st.sidebar.radio("Operation", ["Search Reader", "Search Books by Title",
                                       "Show Book Copies", "Available Books"], label_visibility="collapsed")
elif group == "Add Records":
    operation = st.sidebar.radio("Operation", ["Add Reader", "Add Book", "Add Book Copy"], label_visibility="collapsed")
elif group == "Circulation":
    operation = st.sidebar.radio("Operation", ["Borrow Book", "Return Book", "Check Reader Status",
                                       "Check Borrow Limit", "Update Fine Balance"], label_visibility="collapsed")
elif group == "Reservations":
    operation = st.sidebar.radio("Operation", ["Place Reservation", "Cancel Reservation",
                                       "Expire Reservations"], label_visibility="collapsed")
elif group == "Reports & Analytics":
    operation = st.sidebar.radio("Operation", ["Overdue Transactions", "Unpaid Fines",
                                       "Most Borrowed Books", "Never Borrowed Readers",
                                       "Top Fine Payees"], label_visibility="collapsed")
else:
    operation = st.sidebar.radio("Operation", ["Delete Damaged Copies"], label_visibility="collapsed")

# ──────────────────────────────────────────────────────────────
try:

    # ── HOME DASHBOARD ────────────────────────────────────────
    if operation == "Home":
        section_header("Dashboard Overview", "Real-time snapshot of your library database.")

        total_readers    = int(run_select(conn, SQL["count_readers"]).iloc[0, 0])
        total_books      = int(run_select(conn, SQL["count_books"]).iloc[0, 0])
        total_copies     = int(run_select(conn, SQL["count_copies"]).iloc[0, 0])
        active_borrows   = int(run_select(conn, SQL["count_active_borrows"]).iloc[0, 0])
        active_res       = int(run_select(conn, SQL["count_active_reservations"]).iloc[0, 0])

        c1, c2, c3, c4, c5 = st.columns(5)
        with c1: metric_card("Readers",      total_readers,  "👤", "#3b82f6")
        with c2: metric_card("Books",         total_books,    "📖", "#8b5cf6")
        with c3: metric_card("Copies",        total_copies,   "📋", "#14b8a6")
        with c4: metric_card("Active Borrows",active_borrows, "🔄", "#eab308")
        with c5: metric_card("Reservations",  active_res,     "🔖", "#f43f5e")

        st.markdown("""
        <div class="section-card">
            <h3 style="margin-top:0; font-size:1.1rem !important;">Application Modules</h3>
            <div class="module-grid">
                <div class="module-card">
                    <div class="module-icon">🔍</div>
                    <div class="module-name">Search & View</div>
                    <div class="module-desc">Search readers, book titles, copies, and available inventory.</div>
                </div>
                <div class="module-card">
                    <div class="module-icon">➕</div>
                    <div class="module-name">Add Records</div>
                    <div class="module-desc">Insert new readers, books, and physical copies.</div>
                </div>
                <div class="module-card">
                    <div class="module-icon">🔄</div>
                    <div class="module-name">Circulation</div>
                    <div class="module-desc">Borrow, return, validate suspension, enforce limits and update fines.</div>
                </div>
                <div class="module-card">
                    <div class="module-icon">🔖</div>
                    <div class="module-name">Reservations</div>
                    <div class="module-desc">Place, cancel, and auto-expire book reservations.</div>
                </div>
                <div class="module-card">
                    <div class="module-icon">📊</div>
                    <div class="module-name">Reports & Analytics</div>
                    <div class="module-desc">Overdues, fines, most borrowed books, inactive readers.</div>
                </div>
                <div class="module-card">
                    <div class="module-icon">🛠️</div>
                    <div class="module-name">Admin Tools</div>
                    <div class="module-desc">Remove damaged copies from active inventory.</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── SEARCH & VIEW ─────────────────────────────────────────
    elif operation == "Search Reader":
        section_header("Search Reader", "Retrieve complete reader account information by Member ID.")
        with st.container(border=True):
            c1, c2 = st.columns([2, 1])
            with c1: member_id = st.number_input("Member ID", min_value=1, step=1)
            with c2:
                st.write(""); st.write("")
                run_btn = st.button("Search Reader")
        if run_btn:
            df = run_select(conn, SQL["search_reader"], {"member_id": int(member_id)})
            show_dataframe(df, "No reader found for this Member ID.")

    elif operation == "Search Books by Title":
        section_header("Search Books by Title", "Search the catalog using a title keyword.")
        with st.container(border=True):
            c1, c2 = st.columns([3, 1])
            with c1: title_keyword = st.text_input("Title keyword", placeholder="e.g. Oracle, Python, Design…")
            with c2:
                st.write(""); st.write("")
                run_btn = st.button("Search Books")
        if run_btn:
            df = run_select(conn, SQL["search_books_by_title"], {"title_keyword": f"%{title_keyword}%"})
            show_dataframe(df, "No books found with that keyword.")

    elif operation == "Show Book Copies":
        section_header("Book Copies", "All physical copies associated with a given Book ID.")
        with st.container(border=True):
            c1, c2 = st.columns([2, 1])
            with c1: book_id = st.number_input("Book ID", min_value=1, step=1)
            with c2:
                st.write(""); st.write("")
                run_btn = st.button("Load Copies")
        if run_btn:
            df = run_select(conn, SQL["show_copies"], {"book_id": int(book_id)})
            show_dataframe(df, "No copies found for this Book ID.")

    elif operation == "Available Books":
        section_header("Available Books", "Books that currently have at least one available copy.")
        if st.button("Load Available Books"):
            df = run_select(conn, SQL["available_books"])
            show_dataframe(df, "No available books found.")

    # ── ADD RECORDS ───────────────────────────────────────────
    elif operation == "Add Reader":
        section_header("Register New Reader", "Insert a new library member into the system.")
        with st.form("add_reader_form"):
            c1, c2 = st.columns(2)
            with c1:
                member_id       = st.number_input("Member ID", min_value=1, step=1)
                name            = st.text_input("Full Name")
                email           = st.text_input("Email")
                phone_number    = st.text_input("Phone Number")
            with c2:
                address         = st.text_input("Address")
                membership_date = st.date_input("Membership Date", value=date.today())
                account_status  = st.selectbox("Account Status", ["Active", "Suspended"])
                fine_balance    = st.number_input("Fine Balance", min_value=0.0, step=0.5)
            submitted = st.form_submit_button("Add Reader")
        if submitted:
            run_dml(conn, SQL["add_reader"], {
                "member_id": int(member_id), "name": name, "email": email,
                "phone_number": phone_number, "address": address,
                "membership_date": membership_date, "account_status": account_status,
                "fine_balance": float(fine_balance),
            })
            toast("Reader added successfully.", "success")

    elif operation == "Add Book":
        section_header("Add New Book", "Insert a new bibliographic record into the catalog.")
        with st.form("add_book_form"):
            c1, c2 = st.columns(2)
            with c1:
                book_id          = st.number_input("Book ID", min_value=1, step=1)
                isbn             = st.text_input("ISBN")
                title            = st.text_input("Title")
                author           = st.text_input("Author")
                edition          = st.text_input("Edition")
            with c2:
                category         = st.text_input("Category")
                language         = st.text_input("Language")
                publication_year = st.number_input("Publication Year", min_value=0, step=1)
                series_id        = st.number_input("Series ID", min_value=1, step=1)
            submitted = st.form_submit_button("Add Book")
        if submitted:
            run_dml(conn, SQL["add_book"], {
                "book_id": int(book_id), "isbn": isbn, "title": title,
                "author": author, "edition": edition, "category": category,
                "language": language, "publication_year": int(publication_year),
                "series_id": int(series_id),
            })
            toast("Book added successfully.", "success")

    elif operation == "Add Book Copy":
        section_header("Add Book Copy", "Insert a new physical copy for an existing book.")
        with st.form("add_copy_form"):
            c1, c2 = st.columns(2)
            with c1:
                copy_id          = st.number_input("Copy ID", min_value=1, step=1)
                status           = st.selectbox("Status", ["Available", "Borrowed", "Reserved", "Damaged"])
            with c2:
                acquisition_date = st.date_input("Acquisition Date", value=date.today())
                shelf_location   = st.text_input("Shelf Location")
            book_id = st.number_input("Book ID", min_value=1, step=1)
            submitted = st.form_submit_button("Add Book Copy")
        if submitted:
            run_dml(conn, SQL["add_copy"], {
                "copy_id": int(copy_id), "status": status,
                "acquisition_date": acquisition_date,
                "shelf_location": shelf_location, "book_id": int(book_id),
            })
            toast("Book copy added successfully.", "success")

    # ── CIRCULATION ───────────────────────────────────────────
    elif operation == "Borrow Book":
        section_header("Borrow a Book", "Create a borrow transaction with full eligibility validation.")
        with st.form("borrow_form"):
            c1, c2 = st.columns(2)
            with c1:
                transaction_id = st.number_input("Transaction ID", min_value=1, step=1)
                member_id      = st.number_input("Member ID", min_value=1, step=1)
            with c2:
                copy_id  = st.number_input("Copy ID", min_value=1, step=1)
                staff_id = st.number_input("Staff ID", min_value=1, step=1)
            submitted = st.form_submit_button("Borrow Book")

        if submitted:
            status_df = run_select(conn, SQL["check_suspension"], {"member_id": int(member_id)})
            if status_df.empty:
                toast("Reader not found.", "error")
            elif str(status_df.iloc[0, 0]) == "Suspended":
                toast("Borrow denied — this reader's account is suspended.", "error")
            else:
                borrow_df = run_select(conn, SQL["borrow_limit"], {"member_id": int(member_id)})
                if int(borrow_df.iloc[0, 0]) >= 5:
                    toast("Borrow denied — reader already has 5 active borrows.", "warn")
                else:
                    copy_df = run_select(conn, SQL["copy_status"], {"copy_id": int(copy_id)})
                    if copy_df.empty:
                        toast("Copy not found.", "error")
                    elif str(copy_df.iloc[0, 0]) != "Available":
                        toast(f"Borrow denied — copy status is '{copy_df.iloc[0, 0]}', not Available.", "warn")
                    else:
                        run_multi_dml(conn, [
                            (SQL["insert_transaction"], {
                                "transaction_id": int(transaction_id), "member_id": int(member_id),
                                "copy_id": int(copy_id), "staff_id": int(staff_id),
                            }),
                            (SQL["mark_copy_borrowed"], {"copy_id": int(copy_id)}),
                        ])
                        toast("Borrow transaction created — copy marked as Borrowed.", "success")

    elif operation == "Return Book":
        section_header("Return a Book", "Close a transaction, update copy status, auto-generate late fines.")
        with st.form("return_form"):
            c1, c2, c3 = st.columns(3)
            with c1: transaction_id = st.number_input("Transaction ID", min_value=1, step=1)
            with c2: copy_id        = st.number_input("Copy ID", min_value=1, step=1)
            with c3: fine_id        = st.number_input("Fine ID (if late)", min_value=1, step=1)
            submitted = st.form_submit_button("Return Book")

        if submitted:
            run_multi_dml(conn, [
                (SQL["mark_transaction_returned"], {"transaction_id": int(transaction_id)}),
                (SQL["mark_copy_available"],       {"copy_id": int(copy_id)}),
                (SQL["insert_fine_auto"],           {"fine_id": int(fine_id), "transaction_id": int(transaction_id)}),
            ])
            tx_member = run_select(conn, SQL["transaction_member"], {"transaction_id": int(transaction_id)})
            if not tx_member.empty:
                run_dml(conn, SQL["update_fine_balance"], {"member_id": int(tx_member.iloc[0, 0])})
            toast("Return processed — fine logic applied and balance updated.", "success")

    elif operation == "Check Reader Status":
        section_header("Check Reader Status", "Verify whether a reader is Active or Suspended.")
        member_id = st.number_input("Member ID", min_value=1, step=1)
        if st.button("Check Status"):
            df = run_select(conn, SQL["check_suspension"], {"member_id": int(member_id)})
            show_dataframe(df, "No reader found.")

    elif operation == "Check Borrow Limit":
        section_header("Check Borrow Limit", "View a reader's active borrow count (max 5).")
        member_id = st.number_input("Member ID", min_value=1, step=1, key="limit_member")
        if st.button("Check Borrow Limit"):
            df = run_select(conn, SQL["borrow_limit"], {"member_id": int(member_id)})
            show_dataframe(df, "No borrowing records found.")

    elif operation == "Update Fine Balance":
        section_header("Update Fine Balance", "Recalculate a reader's outstanding fine balance from unpaid fines.")
        member_id = st.number_input("Member ID", min_value=1, step=1, key="fine_bal_member")
        if st.button("Update Fine Balance"):
            run_dml(conn, SQL["update_fine_balance"], {"member_id": int(member_id)})
            toast("Reader fine balance updated.", "success")

    # ── RESERVATIONS ──────────────────────────────────────────
    elif operation == "Place Reservation":
        section_header("Place Reservation", "Create a new reservation for a reader and book.")
        with st.form("place_res_form"):
            c1, c2, c3 = st.columns(3)
            with c1: reservation_id = st.number_input("Reservation ID", min_value=1, step=1)
            with c2: member_id      = st.number_input("Member ID", min_value=1, step=1)
            with c3: book_id        = st.number_input("Book ID", min_value=1, step=1)
            submitted = st.form_submit_button("Place Reservation")
        if submitted:
            run_dml(conn, SQL["place_reservation"], {
                "reservation_id": int(reservation_id),
                "member_id": int(member_id), "book_id": int(book_id),
            })
            toast("Reservation placed successfully.", "success")

    elif operation == "Cancel Reservation":
        section_header("Cancel Reservation", "Update an existing reservation status to Cancelled.")
        reservation_id = st.number_input("Reservation ID", min_value=1, step=1)
        if st.button("Cancel Reservation"):
            run_dml(conn, SQL["cancel_reservation"], {"reservation_id": int(reservation_id)})
            toast("Reservation cancelled.", "info")

    elif operation == "Expire Reservations":
        section_header("Auto-Expire Reservations", "Mark all past-expiry active reservations as Expired.")
        if st.button("Run Expiration Process"):
            run_dml(conn, SQL["expire_reservations"])
            toast("Expired reservations updated successfully.", "success")

    # ── REPORTS & ANALYTICS ───────────────────────────────────
    elif operation == "Overdue Transactions":
        section_header("Overdue Transactions", "Active borrows whose due date has already passed.")
        if st.button("Load Overdue Transactions"):
            df = run_select(conn, SQL["overdue"])
            show_dataframe(df, "No overdue transactions — all clear! ✓")

    elif operation == "Unpaid Fines":
        section_header("Unpaid Fines", "Readers with outstanding fine balances.")
        if st.button("Load Unpaid Fines"):
            df = run_select(conn, SQL["unpaid_fines"])
            show_dataframe(df, "No unpaid fines found.")

    elif operation == "Most Borrowed Books":
        section_header("Most Borrowed Books", "Top titles ranked by total borrow count.")
        if st.button("Load Most Borrowed Books"):
            df = run_select(conn, SQL["most_borrowed"])
            show_dataframe(df, "No borrowing history found.")

    elif operation == "Never Borrowed Readers":
        section_header("Never Borrowed Readers", "Members who have never borrowed a book.")
        if st.button("Load Never Borrowed Readers"):
            df = run_select(conn, SQL["never_borrowed"])
            show_dataframe(df, "Every reader has at least one borrow on record.")

    elif operation == "Top Fine Payees":
        section_header("Top Fine Payees", "Readers who have accumulated the highest total fines.")
        if st.button("Load Top Fine Payees"):
            df = run_select(conn, SQL["top_fines"])
            show_dataframe(df, "No fine records found.")

    # ── ADMIN ─────────────────────────────────────────────────
    elif operation == "Delete Damaged Copies":
        section_header("Remove Damaged Copies", "Permanently delete all copies marked as Damaged from inventory.")
        st.markdown("""
        <div class="toast" style="border-left-color:#f43f5e; margin-bottom:1rem">
            <span class="toast-icon" style="color:#f43f5e">⚠</span>
            <span>This operation is <strong>irreversible</strong>. All copies with status <strong>Damaged</strong> will be permanently deleted.</span>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Delete Damaged Copies"):
            run_dml(conn, SQL["delete_damaged"])
            toast("Damaged copies removed from inventory.", "success")

except Exception as e:
    st.markdown(f"""
    <div class="toast" style="border-left-color:#f43f5e; margin-top:1rem">
        <span class="toast-icon" style="color:#f43f5e">✕</span>
        <span><strong>Operation failed:</strong> {e}</span>
    </div>
    """, unsafe_allow_html=True)

finally:
    try:
        conn.close()
    except Exception:
        pass
