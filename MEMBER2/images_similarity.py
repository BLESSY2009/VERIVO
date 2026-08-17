from pathlib import Path

from PIL import Image
import imagehash


def calculate_image_similarity(image1_path, image2_path):
    """
    Compare two images using perceptual hashing.

    Returns a similarity percentage from 0 to 100.
    """

    image1_path = Path(image1_path)
    image2_path = Path(image2_path)

    # Check whether files exist
    if not image1_path.exists():
        raise FileNotFoundError(
            f"Image not found: {image1_path}"
        )

    if not image2_path.exists():
        raise FileNotFoundError(
            f"Image not found: {image2_path}"
        )

    # Open images
    image1 = Image.open(image1_path)
    image2 = Image.open(image2_path)

    # Generate perceptual hashes
    hash1 = imagehash.phash(image1)
    hash2 = imagehash.phash(image2)

    # Calculate hash difference
    distance = hash1 - hash2

    # Maximum possible difference
    max_distance = hash1.hash.size

    # Convert difference into similarity
    similarity = (
        1 - (distance / max_distance)
    ) * 100

    # Keep score between 0 and 100
    similarity = max(
        0,
        min(100, similarity)
    )

    return round(float(similarity), 2)


def get_similarity_level(score):
    """
    Convert similarity score into a readable level.
    """

    if score >= 85:
        return "HIGH"

    elif score >= 60:
        return "MEDIUM"

    else:
        return "LOW"


if __name__ == "__main__":

    # Reference/genuine profile picture
    reference_image = "images/genuine.jpg"

    # Suspicious profile picture
    suspicious_image = "images/suspicious.jpg"

    # Calculate similarity
    score = calculate_image_similarity(
        reference_image,
        suspicious_image
    )

    # Determine risk level
    level = get_similarity_level(score)

    print("\n==========================================")
    print("       FAKEGUARD IMAGE ANALYSIS")
    print("==========================================")

    print(
        f"\nImage Similarity: {score}%"
    )

    print(
        f"Similarity Level: {level}"
    )

    if score >= 85:

        print(
            "\nWARNING: High visual similarity detected."
        )

    elif score >= 60:

        print(
            "\nWARNING: Moderate visual similarity detected."
        )

    else:

        print(
            "\nLow visual similarity detected."
        )

    print("\n==========================================")