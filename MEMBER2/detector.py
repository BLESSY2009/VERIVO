"""
detector.py
------------
Core heuristic engine for fake profile detection.
Each rule adds/subtracts points from a 0-100 "fake score".
This is a rule-based baseline — swap `analyze_profile` internals
with an ML model later (e.g. sklearn classifier) without changing app.py.
"""

import re


def analyze_profile(profile: dict) -> dict:
    score = 0
    reasons = []

    username = profile.get("username", "") or ""
    full_name = profile.get("full_name", "") or ""
    followers = profile.get("followers", 0) or 0
    following = profile.get("following", 0) or 0
    posts = profile.get("posts", 0) or 0
    account_age_days = profile.get("account_age_days", 0) or 0
    has_profile_pic = profile.get("has_profile_pic", True)
    has_bio = profile.get("has_bio", True)
    is_verified = profile.get("is_verified", False)
    bio_text = profile.get("bio_text", "") or ""

    # --- Rule 1: Username has many trailing digits (bot-like pattern) ---
    digit_suffix = re.search(r"\d{4,}$", username)
    if digit_suffix:
        score += 15
        reasons.append("Username ends with a long numeric sequence (common in auto-generated bot accounts).")

    # --- Rule 2: No profile picture ---
    if not has_profile_pic:
        score += 15
        reasons.append("No profile picture set.")

    # --- Rule 3: No bio ---
    if not has_bio or len(bio_text.strip()) == 0:
        score += 10
        reasons.append("Bio is empty.")

    # --- Rule 4: Following >> Followers (mass-follow bot pattern) ---
    if following > 0:
        ratio = following / max(followers, 1)
        if ratio > 5 and following > 200:
            score += 20
            reasons.append(f"Following/Followers ratio is very high ({ratio:.1f}x) — typical of spam/bot accounts.")
        elif ratio > 2 and following > 100:
            score += 10
            reasons.append(f"Following/Followers ratio is somewhat high ({ratio:.1f}x).")

    # --- Rule 5: Very new account with high activity ---
    if account_age_days < 30 and posts > 50:
        score += 20
        reasons.append("Account is very new (<30 days) but already has unusually high post activity.")
    elif account_age_days < 7:
        score += 10
        reasons.append("Account was created very recently (<7 days ago).")

    # --- Rule 6: Zero posts but high following ---
    if posts == 0 and following > 50:
        score += 15
        reasons.append("Account has zero posts but follows many accounts (common bot pattern).")

    # --- Rule 7: Followers count suspiciously round / inflated with low posts ---
    if followers > 10000 and posts < 5:
        score += 15
        reasons.append("Very high follower count despite almost no posts — possible bought followers.")

    # --- Rule 8: Verified accounts get trust boost ---
    if is_verified:
        score -= 30
        reasons.append("Account is verified — strong signal of authenticity.")

    # --- Rule 9: Full name looks like random characters ---
    if full_name and re.search(r"\d{3,}", full_name):
        score += 10
        reasons.append("Display name contains an unusual number of digits.")

    # --- Rule 10: Bio contains spammy keywords ---
    spam_keywords = ["click here", "free followers", "make money fast", "dm for promo", "earn from home"]
    lowered_bio = bio_text.lower()
    if any(k in lowered_bio for k in spam_keywords):
        score += 20
        reasons.append("Bio contains spam/promotional keywords.")

    # Clamp score between 0-100
    score = max(0, min(100, score))

    if score >= 60:
        label = "Likely Fake"
    elif score >= 30:
        label = "Suspicious"
    else:
        label = "Likely Real"

    return {
        "fake_score": score,
        "label": label,
        "reasons": reasons,
    }