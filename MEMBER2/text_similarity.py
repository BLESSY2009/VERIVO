from rapidfuzz import fuzz


def normalize_text(text):
    """
    Clean text before comparison.
    """

    if text is None:
        return ""

    return " ".join(str(text).lower().strip().split())


def calculate_similarity(text1, text2):
    """
    Calculate similarity between two text values.

    Returns a percentage from 0 to 100.
    """

    text1 = normalize_text(text1)
    text2 = normalize_text(text2)

    if not text1 or not text2:
        return 0.0

    score = fuzz.ratio(text1, text2)

    return round(float(score), 2)


def username_similarity(username1, username2):
    """
    Compare two usernames.
    """

    username1 = username1.replace("@", "")
    username2 = username2.replace("@", "")

    return calculate_similarity(username1, username2)


def display_name_similarity(name1, name2):
    """
    Compare two display names.
    """

    return calculate_similarity(name1, name2)


def bio_similarity(bio1, bio2):
    """
    Compare two profile bios.
    """

    return calculate_similarity(bio1, bio2)


# Test the module
if __name__ == "__main__":

    genuine_username = "@rahulkumar"
    suspicious_username = "@rahulkumar_official"

    genuine_name = "Rahul Kumar"
    suspicious_name = "Rahul Kumar Official"

    genuine_bio = "Student Photographer Coimbatore"
    suspicious_bio = "Student Photographer Coimbatore"

    print("\n===== FAKEGUARD TEXT SIMILARITY =====\n")

    print(
        "Username Similarity:",
        username_similarity(
            genuine_username,
            suspicious_username
        ),
        "%"
    )

    print(
        "Display Name Similarity:",
        display_name_similarity(
            genuine_name,
            suspicious_name
        ),
        "%"
    )

    print(
        "Bio Similarity:",
        bio_similarity(
            genuine_bio,
            suspicious_bio
        ),
        "%"
    )