

import time
from datetime import datetime

import streamlit as st
from detector import analyze_profile
from predict import predict_profile
from risk_engine import calculate_behaviour_risk
from identity_analysis import analyze_identity

st.set_page_config(
    page_title="Verivo | Verify. Detect. Protect.",
    page_icon="✦",
    layout="centered",
)

# ---------------- Brand tokens (from Verivo logo) ----------------
CREAM = "#FAF6F2"
INK = "#242034"
PURPLE_DARK = "#6E5A9C"
PURPLE_LIGHT = "#A99BD1"
GOLD_ACCENT = "#B99B6B"

st.markdown(f"""
    <style>
    .stApp {{
        background-color: {CREAM};
    }}
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;700;900&family=Jost:wght@300;400;500;600&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Jost', sans-serif;
        color: {INK};
    }}

    .verivo-word {{
        font-family: 'Playfair Display', serif;
        font-size: 4.2rem;
        text-align: center;
        letter-spacing: 0.35rem;
        color: {INK};
        margin-bottom: 0;
        font-weight: 500;
    }}
    .verivo-tagline {{
        text-align: center;
        letter-spacing: 0.28rem;
        font-size: 0.85rem;
        color: {PURPLE_DARK};
        text-transform: uppercase;
        margin-top: -4px;
        margin-bottom: 2.5rem;
    }}
    .verivo-tagline .accent {{ color: {INK}; }}

    .section-title {{
        font-family: 'Playfair Display', serif;
        font-size: 1.6rem;
        color: {INK};
        margin-bottom: 0.3rem;
    }}
    .section-sub {{
        color: #6b647f;
        margin-bottom: 1.5rem;
        font-size: 0.95rem;
    }}

    div.stButton > button {{
        background-color: {INK};
        color: {CREAM};
        border-radius: 30px;
        padding: 0.55rem 1.8rem;
        border: none;
        font-family: 'Jost', sans-serif;
        letter-spacing: 0.08rem;
        font-weight: 500;
        width: 100%;
    }}
    div.stButton > button:hover {{
        background-color: {PURPLE_DARK};
        color: white;
    }}

    .verivo-card {{
        background-color: white;
        border-radius: 18px;
        padding: 1.6rem 1.8rem;
        border: 1px solid #ECE4F4;
        margin-bottom: 1.2rem;
    }}

    .fake-badge {{ color: #B3413A; font-weight: 600; }}
    .suspicious-badge {{ color: {GOLD_ACCENT}; font-weight: 600; }}
    .real-badge {{ color: #4C8863; font-weight: 600; }}

    .reason-item {{ padding: 5px 0px; color: {INK}; }}

    .verivo-footer {{
        text-align: center;
        color: #b3aac2;
        font-size: 0.78rem;
        letter-spacing: 0.1rem;
        margin-top: 3rem;
    }}
    </style>
""", unsafe_allow_html=True)


# ---------------- Session state / page router ----------------
if "step" not in st.session_state:
    st.session_state.step = "home"
if "profile" not in st.session_state:
    st.session_state.profile = {}
if "result" not in st.session_state:
    st.session_state.result = None


def go_to(step: str):
    st.session_state.step = step


def brand_header():
    st.markdown('<p class="verivo-word">verivo</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="verivo-tagline">verify <span class="accent">•</span> detect '
        '<span class="accent">•</span> protect</p>',
        unsafe_allow_html=True,
    )


# ==========================================================
# STEP 1: HOME
# ==========================================================
if st.session_state.step == "home":
    brand_header()
    st.markdown(
        f"""
        <div class="verivo-card" style="text-align:center;">
            <p class="section-title">Fake Profile Detection</p>
            <p class="section-sub">
                Verivo checks a social media profile's public signals — followers,
                activity, account age and more — and flags the patterns real
                accounts don't usually have.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    col1, col2, col3 = st.columns([1, 1.4, 1])
    with col2:
        if st.button("Get Started →"):
            go_to("input")
    st.markdown('<p class="verivo-footer">HACKATHON PROJECT · V1.0</p>', unsafe_allow_html=True)


# ==========================================================
# STEP 2: PROFILE INPUT
# ==========================================================
elif st.session_state.step == "input":
    brand_header()
    st.markdown('<p class="section-title">Profile Input</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-sub">Enter the profile\'s details to begin analysis.</p>', unsafe_allow_html=True)

    with st.form("profile_form"):
        col1, col2 = st.columns(2)
        with col1:
            username = st.text_input("Username", placeholder="e.g. john_doe_123456")
            full_name = st.text_input("Display Name", placeholder="e.g. John Doe")
            followers = st.number_input("Followers count", min_value=0, value=100)
            following = st.number_input("Following count", min_value=0, value=100)
            posts = st.number_input("Number of posts", min_value=0, value=10)
            likes = st.number_input("Average likes", min_value=0, value=10)
            comments = st.number_input("Average comments", min_value=0, value=2)
        with col2:
            account_age_days = st.number_input("Account age (in days)", min_value=0, value=180)
            has_profile_pic = st.checkbox("Has a profile picture", value=True)
            has_bio = st.checkbox("Has a bio", value=True)
            is_verified = st.checkbox("Verified account", value=False)
            bio_text = st.text_area("Bio text (optional)", placeholder="Paste bio here...")
            reference_username = st.text_input("Reference Username",placeholder="e.g. genuine_user")
            reference_name = st.text_input("Reference Display Name",placeholder="e.g. Genuine User")

            reference_bio = st.text_area("Reference Bio",placeholder="Enter genuine profile bio...")

            submitted = st.form_submit_button("Analyse Profile →")

    if submitted:
        st.session_state.profile = {
            "username": username,
            "full_name": full_name,
            "followers": followers,
            "following": following,
            "posts": posts,
            "likes": likes,
            "comments": comments,
            "account_age_days": account_age_days,
            "has_profile_pic": has_profile_pic,
            "has_bio": has_bio,
            "is_verified": is_verified,
            "bio_text": bio_text,
        }
        go_to("analyse")
        st.rerun()

    if st.button("← Back to Home"):
        go_to("home")


# ==========================================================
# STEP 3: ANALYSE (confirmation / trigger screen)
# ==========================================================
elif st.session_state.step == "analyse":
    brand_header()
    p = st.session_state.profile
    st.markdown('<p class="section-title">Ready to Analyse</p>', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="verivo-card">
            <b>@{p.get('username') or 'unknown'}</b><br>
            {p.get('followers', 0)} followers · {p.get('following', 0)} following ·
            {p.get('posts', 0)} posts · {p.get('account_age_days', 0)} days old
        </div>
        """,
        unsafe_allow_html=True,
    )
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Edit Details"):
            go_to("input")
    with col2:
        if st.button("Start Analysis →"):
            go_to("loading")
            st.rerun()


# ==========================================================
# STEP 4: LOADING
# ==========================================================
elif st.session_state.step == "loading":
    brand_header()
    st.markdown('<p class="section-title">Analysing Profile…</p>', unsafe_allow_html=True)
    progress_bar = st.progress(0)
    steps = [
        "Checking username pattern...",
        "Evaluating follower/following ratio...",
        "Reviewing account age vs activity...",
        "Scanning bio for spam signals...",
        "Compiling results...",
    ]
    status = st.empty()
    for i, msg in enumerate(steps):
        status.markdown(f"<p class='section-sub'>{msg}</p>", unsafe_allow_html=True)
        progress_bar.progress(int((i + 1) / len(steps) * 100))
        time.sleep(0.4)

    ml_result = predict_profile(
        account_age_days=st.session_state.profile["account_age_days"],
        followers=st.session_state.profile["followers"],
        following=st.session_state.profile["following"],
        posts=st.session_state.profile["posts"],
        engagement_rate=0.2,
    )
    behaviour_score, behaviour_level, behaviour_reasons = calculate_behaviour_risk(
    st.session_state.profile["followers"],
    st.session_state.profile["following"],
    st.session_state.profile["posts"],
    st.session_state.profile["likes"],
    st.session_state.profile["comments"],
)

    st.session_state.result = {
    "fake_score": ml_result["risk_score"],
    "behaviour_score": behaviour_score,
    "behaviour_level": behaviour_level,
    "behaviour_reasons": behaviour_reasons,
        "label": (
            "Likely Fake"
            if ml_result["risk_score"] >= 60
            else "Suspicious"
            if ml_result["risk_score"] >= 30
            else "Likely Real"
        ),
        "reasons": [
            indicator["message"]
            for indicator in ml_result["indicators"]
        ],
    }

    go_to("result")
    st.rerun()
    go_to("result")
    st.rerun()


# ==========================================================
# STEP 5: RESULT DASHBOARD
# ==========================================================
elif st.session_state.step == "result":
    brand_header()
    result = st.session_state.result
    p = st.session_state.profile

    score = result["fake_score"]
    label = result["label"]
    reasons = result["reasons"]
    behaviour_score = result.get("behaviour_score", 0)
    behaviour_level = result.get("behaviour_level", "LOW")
    behaviour_reasons = result.get("behaviour_reasons", [])

    badge_class = "fake-badge" if label == "Likely Fake" else (
        "suspicious-badge" if label == "Suspicious" else "real-badge"
    )

    st.markdown('<p class="section-title">Result Dashboard</p>', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="verivo-card" style="text-align:center;">
            <p style="color:#6b647f; margin-bottom:4px;">@{p.get('username') or 'unknown'}</p>
            <p class="{badge_class}" style="font-size:1.7rem; margin:0;">{label}</p>
            <p style="color:{INK}; font-size:0.95rem;">Fake Probability Score: <b>{score}/100</b></p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.progress(score / 100)
    st.markdown(
    f"**Behaviour Risk:** {behaviour_score}/100  |  **Level:** {behaviour_level}"
    )

    st.markdown('<div class="verivo-card">', unsafe_allow_html=True)
    st.markdown('<p class="section-title" style="font-size:1.2rem;">Analysis Breakdown</p>', unsafe_allow_html=True)
    if reasons:
        for r in reasons:
            st.markdown(f'<div class="reason-item">• {r}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="reason-item">No red flags detected. Profile looks fairly normal.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Analyse Another Profile"):
            go_to("input")
            st.rerun()
    with col2:
        if st.button("Generate Report →"):
            go_to("report")
            st.rerun()


# ==========================================================
# STEP 6: GENERATE REPORT
# ==========================================================
elif st.session_state.step == "report":
    brand_header()
    result = st.session_state.result
    p = st.session_state.profile
    score = result["fake_score"]
    label = result["label"]
    reasons = result["reasons"]

    st.markdown('<p class="section-title">Generate Report</p>', unsafe_allow_html=True)
    st.markdown('<p class="section-sub">Download a summary of this analysis.</p>', unsafe_allow_html=True)

    report_text = f"""VERIVO — VERIFY · DETECT · PROTECT
Fake Profile Analysis Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

Profile: @{p.get('username') or 'unknown'}
Display Name: {p.get('full_name') or '-'}

--- Stats ---
Followers: {p.get('followers', 0)}
Following: {p.get('following', 0)}
Posts: {p.get('posts', 0)}
Account Age: {p.get('account_age_days', 0)} days
Verified: {'Yes' if p.get('is_verified') else 'No'}

--- Result ---
Verdict: {label}
Fake Probability Score: {score}/100

--- Reasons ---
""" + ("\n".join(f"- {r}" for r in reasons) if reasons else "- No red flags detected.")

    st.markdown('<div class="verivo-card">', unsafe_allow_html=True)
    st.text(report_text)
    st.markdown('</div>', unsafe_allow_html=True)

    st.download_button(
        label="⬇ Download Report (.txt)",
        data=report_text,
        file_name=f"verivo_report_{p.get('username') or 'profile'}.txt",
        mime="text/plain",
    )

    if st.button("← Back to Dashboard"):
        go_to("result")
        st.rerun()

st.markdown('<p class="verivo-footer">VERIVO © 2026</p>', unsafe_allow_html=True)