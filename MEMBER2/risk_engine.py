from difflib import SequenceMatcher


def similarity(text1, text2):
    text1 = text1.lower().strip()
    text2 = text2.lower().strip()

    return round(SequenceMatcher(None, text1, text2).ratio() * 100)


def calculate_risk(
    account_age,
    followers,
    following,
    posts,
    username="",
    reference_username="",
    bio="",
    reference_bio=""
):
    score = 0
    reasons = []

    # 1. Account age
    if account_age < 30:
        score += 25
        reasons.append("Account is very new")

    # 2. Follower / following ratio
    if following > 1000 and followers < 100:
        score += 30
        reasons.append("Abnormal follower/following ratio")

    # 3. Post activity
    if posts < 5:
        score += 20
        reasons.append("Very low posting activity")

    # 4. Following count
    if following > 2000:
        score += 15
        reasons.append("Very high following count")

    # 5. Username similarity
    username_similarity = 0

    if username and reference_username:
        username_similarity = similarity(
            username,
            reference_username
        )

        if username_similarity >= 80:
            score += 5
            reasons.append("Username closely resembles reference profile")

    # 6. Bio similarity
    bio_similarity = 0

    if bio and reference_bio:
        bio_similarity = similarity(
            bio,
            reference_bio
        )

        if bio_similarity >= 80:
            score += 5
            reasons.append("Bio closely resembles reference profile")

    # Maximum score
    if score > 100:
        score = 100

    # Risk level
    if score >= 70:
        risk_level = "HIGH"
    elif score >= 40:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    return (
        score,
        risk_level,
        reasons,
        username_similarity,
        bio_similarity
    )

def calculate_behaviour_risk(followers, following, posts, likes, comments):

    score = 0
    reasons = []

    if following > 2000:
        score += 30
        reasons.append("Very high following activity")

    if followers < 100:
        score += 20
        reasons.append("Very low follower count")

    if posts < 5:
        score += 20
        reasons.append("Very low posting activity")

    if likes < 5 and comments < 2:
        score += 30
        reasons.append("Very low engagement")

    if score > 100:
        score = 100

    if score >= 70:
        level = "HIGH"
    elif score >= 40:
        level = "MEDIUM"
    else:
        level = "LOW"

    return score, level, reasons