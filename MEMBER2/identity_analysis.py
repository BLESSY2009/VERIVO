from text_similarity import (
    username_similarity,
    display_name_similarity,
    bio_similarity
)

from images_similarity import calculate_image_similarity


def analyze_identity(
    genuine_username,
    suspicious_username,
    genuine_name,
    suspicious_name,
    genuine_bio,
    suspicious_bio,
    genuine_image,
    suspicious_image
):
    """
    Combine text and image similarity analysis.

    Returns a dictionary containing all similarity scores,
    overall identity similarity, impersonation status,
    and explanation reasons.
    """

    # -----------------------------
    # TEXT ANALYSIS
    # -----------------------------

    username_score = username_similarity(
        genuine_username,
        suspicious_username
    )

    name_score = display_name_similarity(
        genuine_name,
        suspicious_name
    )

    bio_score = bio_similarity(
        genuine_bio,
        suspicious_bio
    )

    # -----------------------------
    # IMAGE ANALYSIS
    # -----------------------------

    image_score = calculate_image_similarity(
        genuine_image,
        suspicious_image
    )

    # -----------------------------
    # OVERALL SCORE
    # -----------------------------

    overall_score = (
        username_score +
        name_score +
        bio_score +
        image_score
    ) / 4

    overall_score = round(overall_score, 2)

    # -----------------------------
    # DETERMINE IMPERSONATION
    # -----------------------------

    reasons = []

    if username_score >= 80:
        reasons.append(
            "Username is highly similar to the reference profile."
        )

    elif username_score >= 60:
        reasons.append(
            "Username shows moderate similarity."
        )

    if name_score >= 80:
        reasons.append(
            "Display name is highly similar to the reference profile."
        )

    elif name_score >= 60:
        reasons.append(
            "Display name shows moderate similarity."
        )

    if bio_score >= 80:
        reasons.append(
            "Bio is highly similar to the reference profile."
        )

    elif bio_score >= 60:
        reasons.append(
            "Bio shows moderate similarity."
        )

    if image_score >= 85:
        reasons.append(
            "Profile images have high visual similarity."
        )

    elif image_score >= 60:
        reasons.append(
            "Profile images have moderate visual similarity."
        )

    # Possible impersonation if overall similarity is high
    if overall_score >= 75:
        impersonation = True
    else:
        impersonation = False

    return {
        "username_similarity": username_score,
        "display_name_similarity": name_score,
        "bio_similarity": bio_score,
        "image_similarity": image_score,
        "overall_identity_similarity": overall_score,
        "possible_impersonation": impersonation,
        "reasons": reasons
    }


# -----------------------------------------
# TEST THE COMPLETE MEMBER 4 MODULE
# -----------------------------------------

if __name__ == "__main__":

    result = analyze_identity(

        # Genuine profile
        genuine_username="@rahulkumar",

        # Suspicious profile
        suspicious_username="@rahulkumar_official",

        # Genuine name
        genuine_name="Rahul Kumar",

        # Suspicious name
        suspicious_name="Rahul Kumar Official",

        # Genuine bio
        genuine_bio="Student Photographer Coimbatore",

        # Suspicious bio
        suspicious_bio="Student Photographer Coimbatore",

        # Genuine profile image
        genuine_image="images/genuine.jpg",

        # Suspicious profile image
        suspicious_image="images/suspicious.jpg"
    )

    print("\n==============================================")
    print("       FAKEGUARD IDENTITY ANALYSIS")
    print("==============================================")

    print(
        f"\nUsername Similarity: "
        f"{result['username_similarity']}%"
    )

    print(
        f"Display Name Similarity: "
        f"{result['display_name_similarity']}%"
    )

    print(
        f"Bio Similarity: "
        f"{result['bio_similarity']}%"
    )

    print(
        f"Image Similarity: "
        f"{result['image_similarity']}%"
    )

    print(
        f"\nOverall Identity Similarity: "
        f"{result['overall_identity_similarity']}%"
    )

    if result["possible_impersonation"]:
        print(
            "\nPossible Impersonation: YES"
        )
    else:
        print(
            "\nPossible Impersonation: NO"
        )

    print("\nReasons:")

    if result["reasons"]:
        for reason in result["reasons"]:
            print(f"  - {reason}")
    else:
        print("  - No strong identity indicators detected.")

    print("\n==============================================")