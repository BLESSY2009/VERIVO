from pathlib import Path
import time
from datetime import datetime

import streamlit as st

from predict import predict_profile
from risk_engine import calculate_behaviour_risk


# ============================================================
# VERIVO — VERIFY • DETECT • PROTECT
# ============================================================

st.set_page_config(
    page_title="Verivo | Fake Profile Detection",
    page_icon="✦",
    layout="centered",
)


# ============================================================
# BRAND COLORS
# ============================================================

CREAM = "#FAF6F2"
INK = "#242034"
PURPLE_DARK = "#6E5A9C"
PURPLE_LIGHT = "#A99BD1"
GOLD = "#B99B6B"


# ============================================================
# STYLING
# ============================================================

st.markdown(
    f"""
    <style>

    .stApp {{
        background-color: {CREAM};
    }}

    .verivo-word {{
        font-family: Georgia, serif;
        font-size: 4rem;
        text-align: center;
        letter-spacing: 0.3rem;
        color: {INK};
        margin-bottom: 0;
    }}

    .tagline {{
        text-align: center;
        color: {PURPLE_DARK};
        letter-spacing: 0.2rem;
        margin-bottom: 2rem;
    }}

    .card {{
        background: white;
        padding: 1.5rem;
        border-radius: 18px;
        border: 1px solid #ECE4F4;
        margin-bottom: 1rem;
    }}

    .title {{
        font-family: Georgia, serif;
        font-size: 1.6rem;
        color: {INK};
    }}

    .sub {{
        color: #6b647f;
    }}

    .real {{
        color: #4C8863;
        font-weight: bold;
    }}

    .suspicious {{
        color: {GOLD};
        font-weight: bold;
    }}

    .fake {{
        color: #B3413A;
        font-weight: bold;
    }}

    .footer {{
        text-align: center;
        color: #aaa0b5;
        font-size: 0.75rem;
        margin-top: 3rem;
    }}

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SESSION STATE
# ============================================================

if "page" not in st.session_state:
    st.session_state.page = "home"

if "profile" not in st.session_state:
    st.session_state.profile = {}

if "result" not in st.session_state:
    st.session_state.result = None


def go_to(page):
    st.session_state.page = page


# ============================================================
# HEADER
# ============================================================
def header():

    logo_path = Path(__file__).resolve().parent / "verivo_logo.png"

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:

        if logo_path.exists():
            st.image(
                str(logo_path),
                use_container_width=True
            )
        else:
            st.markdown(
                '<div class="verivo-word">verivo</div>',
                unsafe_allow_html=True
            )

    st.markdown(
        '<div class="tagline">VERIFY • DETECT • PROTECT</div>',
        unsafe_allow_html=True,
    )

# ============================================================
# HOME PAGE
# ============================================================

if st.session_state.page == "home":

    header()

    st.markdown(
        """
        <div class="card" style="text-align:center;">

        <div class="title">
        Fake Social Media Profile Detection
        </div>

        <p class="sub">
        Verivo analyses publicly supplied profile signals such as
        account age, followers, following, posts and engagement.
        </p>

        <p class="sub">
        The system estimates <b>risk</b>.
        It does not prove that an account is fake.
        </p>

        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button(
        "Get Started →",
        use_container_width=True,
    ):

        go_to("input")
        st.rerun()

    st.markdown(
        '<div class="footer">HACKATHON PROJECT • VERIVO V1.0</div>',
        unsafe_allow_html=True,
    )


# ============================================================
# PROFILE INPUT PAGE
# ============================================================

elif st.session_state.page == "input":

    header()

    st.markdown(
        '<div class="title">Profile Input</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="sub">Enter the available public profile information.</div>',
        unsafe_allow_html=True,
    )

    with st.form("profile_form"):

        st.markdown("### Basic Information")

        username = st.text_input(
            "Username",
            placeholder="e.g. genuine_user"
        )

        full_name = st.text_input(
            "Display Name",
            placeholder="e.g. Genuine User"
        )

        bio_text = st.text_area(
            "Bio",
            placeholder="Enter profile bio if available..."
        )

        st.markdown("### Profile Statistics")

        col1, col2 = st.columns(2)

        with col1:

            followers = st.number_input(
                "Followers",
                min_value=0,
                value=213,
                step=1,
            )

            posts = st.number_input(
                "Posts",
                min_value=0,
                value=25,
                step=1,
            )

            likes = st.number_input(
                "Average Likes",
                min_value=0,
                value=20,
                step=1,
            )

        with col2:

            following = st.number_input(
                "Following",
                min_value=0,
                value=210,
                step=1,
            )

            account_age_days = st.number_input(
                "Account Age (days)",
                min_value=0,
                value=500,
                step=1,
            )

            comments = st.number_input(
                "Average Comments",
                min_value=0,
                value=3,
                step=1,
            )

        st.markdown("### Optional Profile Signals")

        col3, col4 = st.columns(2)

        with col3:

            has_profile_pic = st.checkbox(
                "Has Profile Picture",
                value=True,
            )

        with col4:

            is_verified = st.checkbox(
                "Verified Account",
                value=False,
            )

        has_bio = len(bio_text.strip()) > 0

        st.caption(
            "A missing profile picture or bio is NOT automatically treated as evidence of a fake account."
        )

        submitted = st.form_submit_button(
            "Analyse Profile →",
            use_container_width=True,
        )

    if submitted:

        st.session_state.profile = {

            "username": username.strip(),

            "full_name": full_name.strip(),

            "bio_text": bio_text.strip(),

            "followers": int(followers),

            "following": int(following),

            "posts": int(posts),

            "likes": int(likes),

            "comments": int(comments),

            "account_age_days": int(account_age_days),

            "has_profile_pic": has_profile_pic,

            "has_bio": has_bio,

            "is_verified": is_verified,

        }

        go_to("analyse")
        st.rerun()

    if st.button(
        "← Back to Home",
        use_container_width=True,
    ):

        go_to("home")
        st.rerun()


# ============================================================
# ANALYSE CONFIRMATION PAGE
# ============================================================

elif st.session_state.page == "analyse":

    header()

    p = st.session_state.profile

    st.markdown(
        '<div class="title">Ready to Analyse</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="card">

        <b>@{p.get("username") or "unknown"}</b>

        <br><br>

        {p.get("followers", 0):,} followers •
        {p.get("following", 0):,} following •
        {p.get("posts", 0):,} posts

        <br>

        Account age:
        {p.get("account_age_days", 0):,} days

        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "← Edit",
            use_container_width=True,
        ):

            go_to("input")
            st.rerun()

    with col2:

        if st.button(
            "Start Analysis →",
            use_container_width=True,
        ):

            go_to("loading")
            st.rerun()


# ============================================================
# LOADING / ANALYSIS PAGE
# ============================================================

elif st.session_state.page == "loading":

    header()

    st.markdown(
        '<div class="title">Analysing Profile...</div>',
        unsafe_allow_html=True,
    )

    progress = st.progress(0)

    status = st.empty()

    analysis_steps = [

        "Checking account information...",

        "Evaluating follower/following pattern...",

        "Evaluating account age and activity...",

        "Evaluating engagement behaviour...",

        "Running VERIVO AI risk analysis...",

        "Preparing risk assessment...",

    ]

    for i, message in enumerate(analysis_steps):

        status.write(message)

        progress.progress(
            int((i + 1) / len(analysis_steps) * 100)
        )

        time.sleep(0.25)

    p = st.session_state.profile

    try:

        # ----------------------------------------------------
        # FAKEGUARD ML
        # ----------------------------------------------------

        ml_result = predict_profile(

            account_age_days=p["account_age_days"],

            followers=p["followers"],

            following=p["following"],

            posts=p["posts"],

            # Temporary engagement value.
            # This can be replaced with calculated engagement
            # later when the model is redesigned.
            engagement_rate=(
                (
                    p["likes"] + p["comments"]
                )
                / max(p["followers"], 1)
            ) * 100,

        )

        # ----------------------------------------------------
        # BEHAVIOUR ANALYSIS
        # ----------------------------------------------------

        behaviour_score, behaviour_level, behaviour_reasons = (
            calculate_behaviour_risk(

                p["followers"],

                p["following"],

                p["posts"],

                p["likes"],

                p["comments"],

            )
        )

        # ----------------------------------------------------
        # COMBINED RISK
        # ----------------------------------------------------

        ml_score = float(
            ml_result["risk_score"]
        )

        combined_score = round(
            (ml_score * 0.60)
            +
            (behaviour_score * 0.40),
            2,
        )

        # ----------------------------------------------------
        # IMPORTANT:
        # Missing DP / missing bio are NOT added here.
        # ----------------------------------------------------

        if combined_score >= 70:

            label = "High Suspicion"

        elif combined_score >= 40:

            label = "Moderate Suspicion"

        else:

            label = "Low Suspicion"

        # ----------------------------------------------------
        # Combine explanations
        # ----------------------------------------------------

        reasons = []

        for indicator in ml_result.get(
            "indicators",
            []
        ):

            reasons.append(
                indicator["message"]
            )

        for reason in behaviour_reasons:

            if reason not in reasons:

                reasons.append(reason)

        # ----------------------------------------------------
        # SAVE RESULT
        # ----------------------------------------------------

        st.session_state.result = {

            "ml_score": ml_score,

            "behaviour_score": behaviour_score,

            "behaviour_level": behaviour_level,

            "combined_score": combined_score,

            "label": label,

            "reasons": reasons,

        }

        go_to("result")
        st.rerun()

    except Exception as error:

        st.error(
            "Analysis could not be completed."
        )

        st.exception(error)

        if st.button(
            "← Back to Profile",
            use_container_width=True,
        ):

            go_to("input")
            st.rerun()


# ============================================================
# RESULT PAGE
# ============================================================

elif st.session_state.page == "result":

    header()

    p = st.session_state.profile

    result = st.session_state.result

    combined_score = result["combined_score"]

    ml_score = result["ml_score"]

    behaviour_score = result["behaviour_score"]

    label = result["label"]

    reasons = result["reasons"]

    # --------------------------------------------------------
    # Badge
    # --------------------------------------------------------

    if combined_score >= 70:

        badge_class = "fake"

    elif combined_score >= 40:

        badge_class = "suspicious"

    else:

        badge_class = "real"

    st.markdown(
        '<div class="title">Result Dashboard</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="card" style="text-align:center;">

        <div style="color:#6b647f;">
        @{p.get("username") or "unknown"}
        </div>

        <div class="{badge_class}"
             style="font-size:1.8rem;margin-top:10px;">

        {label}

        </div>

        <div style="font-size:1.1rem;margin-top:10px;">

        Overall Risk Score:
        <b>{combined_score}/100</b>

        </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    st.progress(
        min(combined_score / 100, 1.0)
    )

    # --------------------------------------------------------
    # Risk components
    # --------------------------------------------------------

    st.markdown(
        '<div class="card">',
        unsafe_allow_html=True,
    )

    st.markdown(
        "### Risk Breakdown"
    )

    st.write(
        f"**AI Risk Score:** {ml_score}/100"
    )

    st.write(
        f"**Behaviour Risk:** {behaviour_score}/100"
    )

    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # Reasons
    # --------------------------------------------------------

    st.markdown(
        '<div class="card">',
        unsafe_allow_html=True,
    )

    st.markdown(
        "### Analysis Signals"
    )

    if reasons:

        for reason in reasons:

            st.write(
                f"• {reason}"
            )

    else:

        st.success(
            "No major suspicious behavioural signals were detected."
        )

    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )

    # --------------------------------------------------------
    # Important disclaimer
    # --------------------------------------------------------

    st.info(
        "VERIVO provides an AI-assisted risk assessment. "
        "A high or low score does not prove whether an account "
        "is genuinely fake or real. Missing profile pictures, "
        "missing bios, low followers, or low post counts alone "
        "should not be treated as proof of a fake account."
    )

    # --------------------------------------------------------
    # Buttons
    # --------------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "← Analyse Another",
            use_container_width=True,
        ):

            st.session_state.profile = {}

            st.session_state.result = None

            go_to("input")

            st.rerun()

    with col2:

        if st.button(
            "Generate Report →",
            use_container_width=True,
        ):

            go_to("report")

            st.rerun()


# ============================================================
# REPORT PAGE
# ============================================================

elif st.session_state.page == "report":

    header()

    p = st.session_state.profile

    result = st.session_state.result

    report_text = f"""
VERIVO — VERIFY • DETECT • PROTECT

FAKE SOCIAL MEDIA PROFILE RISK REPORT
--------------------------------------

Generated:
{datetime.now().strftime("%Y-%m-%d %H:%M")}

PROFILE
-------
Username: @{p.get("username") or "unknown"}
Display Name: {p.get("full_name") or "-"}

STATISTICS
----------
Followers: {p.get("followers", 0)}
Following: {p.get("following", 0)}
Posts: {p.get("posts", 0)}
Account Age: {p.get("account_age_days", 0)} days

RESULT
------
Overall Risk Score: {result["combined_score"]}/100
Verdict: {result["label"]}

AI Risk Score: {result["ml_score"]}/100
Behaviour Risk: {result["behaviour_score"]}/100

ANALYSIS SIGNALS
----------------
"""

    if result["reasons"]:

        for reason in result["reasons"]:

            report_text += f"- {reason}\n"

    else:

        report_text += "- No major suspicious signals detected.\n"

    report_text += """

DISCLAIMER
----------
This report provides an AI-assisted risk assessment.
It does not prove that an account is fake or genuine.
Missing profile pictures, missing bios, follower count,
following count, or post count alone should not be treated
as proof that an account is fake.
"""

    st.markdown(
        '<div class="title">Generate Report</div>',
        unsafe_allow_html=True,
    )

    st.text_area(
        "Report Preview",
        report_text,
        height=500,
    )

    st.download_button(
        "⬇ Download Report",
        data=report_text,
        file_name="verivo_report.txt",
        mime="text/plain",
        use_container_width=True,
    )

    if st.button(
        "← Back to Dashboard",
        use_container_width=True,
    ):

        go_to("result")

        st.rerun()


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    '<div class="footer">VERIVO © 2026 • AI-ASSISTED RISK ASSESSMENT</div>',
    unsafe_allow_html=True,
)
