"""
FakeGuard ML Engine
-------------------
Member 1 - Machine Learning Module

Responsibilities:
1. Load the trained FakeGuard model
2. Validate profile input
3. Perform feature engineering
4. Predict suspicious-profile risk
5. Generate human-readable explanations
6. Return structured results for backend integration

IMPORTANT:
The model estimates risk/suspicion.
It does NOT prove that an account is fake.
"""

from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = BASE_DIR / "models" / "fakeguard_model.joblib"


# These MUST match the features used during training.
FEATURE_NAMES = [
    "account_age_days",
    "followers",
    "following",
    "posts",
    "engagement_rate",
    "followers_following_ratio",
]


# ============================================================
# MODEL LOADING
# ============================================================

_model = None


_model = None

def load_model():
    global _model

    if _model is not None:
        return _model

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Trained model was not found at:\n{MODEL_PATH}\n\n"
            "Run train_model.py first."
        )

    _model = joblib.load(MODEL_PATH)

    if isinstance(_model, dict):
        _model = _model["model"]

    return _model


# ============================================================
# INPUT VALIDATION
# ============================================================

def validate_profile(
    account_age_days: Any,
    followers: Any,
    following: Any,
    posts: Any,
    engagement_rate: Any,
):
    """
    Validate profile information before sending it to the model.
    """

    values = {
        "account_age_days": account_age_days,
        "followers": followers,
        "following": following,
        "posts": posts,
        "engagement_rate": engagement_rate,
    }

    for name, value in values.items():

        if value is None:
            raise ValueError(f"{name} cannot be empty.")

        try:
            numeric_value = float(value)
        except (TypeError, ValueError):
            raise ValueError(
                f"{name} must be a numeric value."
            )

        if not np.isfinite(numeric_value):
            raise ValueError(
                f"{name} must be a valid finite number."
            )

        if numeric_value < 0:
            raise ValueError(
                f"{name} cannot be negative."
            )

    if float(engagement_rate) > 100:
        raise ValueError(
            "engagement_rate should normally be between 0 and 100."
        )


# ============================================================
# FEATURE ENGINEERING
# ============================================================

def calculate_ratio(followers: float, following: float) -> float:
    """
    Calculate followers/following ratio safely.
    """

    if following == 0:
        return float(followers)

    return float(followers) / float(following)


def build_features(
    account_age_days: float,
    followers: float,
    following: float,
    posts: float,
    engagement_rate: float,
):
    """
    Convert raw profile information into ML features.
    """

    ratio = calculate_ratio(
        followers,
        following
    )

    features = [
        float(account_age_days),
        float(followers),
        float(following),
        float(posts),
        float(engagement_rate),
        float(ratio),
    ]

    return pd.DataFrame([features],
     columns=FEATURE_NAMES)


# ============================================================
# RULE-BASED INDICATORS
# ============================================================

def detect_indicators(
    account_age_days: float,
    followers: float,
    following: float,
    posts: float,
    engagement_rate: float,
):
    """
    Generate understandable indicators.

    These are NOT replacing the ML model.

    They explain patterns that contributed to suspicion.
    """

    indicators = []

    ratio = calculate_ratio(
        followers,
        following
    )

    # --------------------------------------------------------
    # Account age
    # --------------------------------------------------------

    if account_age_days <= 30:
        indicators.append({
            "severity": "high",
            "feature": "account_age",
            "message": (
                f"Account is only {int(account_age_days)} "
                "days old."
            )
        })

    elif account_age_days <= 90:
        indicators.append({
            "severity": "medium",
            "feature": "account_age",
            "message": (
                f"Account is relatively new "
                f"({int(account_age_days)} days old)."
            )
        })


    # --------------------------------------------------------
    # Followers / Following
    # --------------------------------------------------------

    if following >= 1000 and followers <= 100:
        indicators.append({
            "severity": "high",
            "feature": "network_ratio",
            "message": (
                f"Following {int(following):,} accounts "
                f"but has only {int(followers):,} followers."
            )
        })

    elif following > 0 and ratio < 0.05:
        indicators.append({
            "severity": "medium",
            "feature": "network_ratio",
            "message": (
                "Follower/following ratio is unusually low."
            )
        })


    # --------------------------------------------------------
    # Posting activity
    # --------------------------------------------------------

    if account_age_days <= 30 and posts <= 3:
        indicators.append({
            "severity": "high",
            "feature": "posting_activity",
            "message": (
                "Very limited posting activity for the "
                "observed account age."
            )
        })

    elif posts <= 5:
        indicators.append({
            "severity": "medium",
            "feature": "posting_activity",
            "message": (
                "The profile has relatively few posts."
            )
        })


    # --------------------------------------------------------
    # Engagement
    # --------------------------------------------------------

    if engagement_rate < 0.5:
        indicators.append({
            "severity": "medium",
            "feature": "engagement",
            "message": (
                f"Very low engagement rate "
                f"({engagement_rate:.2f}%)."
            )
        })


    # --------------------------------------------------------
    # Extreme following behaviour
    # --------------------------------------------------------

    if following >= 3000:
        indicators.append({
            "severity": "high",
            "feature": "following_activity",
            "message": (
                f"Very high following count "
                f"({int(following):,})."
            )
        })


    return indicators


# ============================================================
# RISK LEVEL
# ============================================================

def get_risk_level(score: float) -> str:
    """
    Convert numerical risk score into a human-readable level.
    """

    if score >= 75:
        return "HIGH"

    if score >= 45:
        return "MEDIUM"

    return "LOW"


# ============================================================
# MAIN PREDICTION FUNCTION
# ============================================================

def predict_profile(
    account_age_days: float,
    followers: float,
    following: float,
    posts: float,
    engagement_rate: float,
):
    """
    Main function used by the backend.

    Returns a dictionary containing:

    - risk score
    - risk level
    - prediction
    - explanation indicators
    - input features
    """

    # --------------------------------------------------------
    # 1. Validate
    # --------------------------------------------------------

    validate_profile(
        account_age_days,
        followers,
        following,
        posts,
        engagement_rate,
    )


    # --------------------------------------------------------
    # 2. Build ML features
    # --------------------------------------------------------

    X = build_features(
        account_age_days,
        followers,
        following,
        posts,
        engagement_rate,
    )


    # --------------------------------------------------------
    # 3. Load model
    # --------------------------------------------------------

    model = load_model()


    # --------------------------------------------------------
    # 4. Generate probability
    # --------------------------------------------------------

    probabilities = model.predict_proba(X)[0]

    classes = list(model.classes_)


    # Find probability of suspicious/fake class.
    #
    # We support common encodings:
    # 0 = genuine
    # 1 = fake
    #
    # If labels are strings, we also handle them.

    fake_probability = None

    for class_value, probability in zip(
        classes,
        probabilities
    ):

        class_text = str(class_value).lower()

        if class_text in {
            "1",
            "fake",
            "suspicious",
            "true",
        }:
            fake_probability = float(probability)

    # Fallback for binary 0/1 models.
    if fake_probability is None and len(probabilities) == 2:
        fake_probability = float(probabilities[-1])

    if fake_probability is None:
        raise ValueError(
            "Unable to determine the suspicious-class probability."
        )


    # --------------------------------------------------------
    # 5. Convert to score
    # --------------------------------------------------------

    risk_score = round(
        fake_probability * 100,
        2
    )


    # --------------------------------------------------------
    # 6. Risk category
    # --------------------------------------------------------

    risk_level = get_risk_level(
        risk_score
    )


    # --------------------------------------------------------
    # 7. Human-readable explanation
    # --------------------------------------------------------

    indicators = detect_indicators(
        account_age_days,
        followers,
        following,
        posts,
        engagement_rate,
    )


    # --------------------------------------------------------
    # 8. Final result
    # --------------------------------------------------------

    result = {
        "model": "FakeGuard ML Engine",

        "risk_score": risk_score,

        "risk_level": risk_level,

        "prediction": (
            "SUSPICIOUS"
            if risk_score >= 50
            else "LOW_SUSPICION"
        ),

        "indicators": indicators,

        "features": {
            "account_age_days": float(account_age_days),
            "followers": int(followers),
            "following": int(following),
            "posts": int(posts),
            "engagement_rate": float(
                engagement_rate
            ),
            "followers_following_ratio": round(
                calculate_ratio(
                    followers,
                    following
                ),
                4
            ),
        },

        "disclaimer": (
            "This result is an AI-assisted risk assessment "
            "based on the supplied profile features. "
            "It does not prove that an account is fake."
        ),
    }

    return result


# ============================================================
# COMMAND-LINE TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("FAKEGUARD ML ENGINE")
    print("=" * 60)

    try:

        result = predict_profile(
            account_age_days=12,
            followers=45,
            following=3500,
            posts=2,
            engagement_rate=0.2,
        )

        print("\nRisk Score:")
        print(f"{result['risk_score']}%")

        print("\nRisk Level:")
        print(result["risk_level"])

        print("\nPrediction:")
        print(result["prediction"])

        print("\nWhy is it suspicious?")

        if result["indicators"]:

            for indicator in result["indicators"]:

                print(
                    f"- [{indicator['severity'].upper()}] "
                    f"{indicator['message']}"
                )

        else:

            print("- No major rule-based indicators detected.")

    except Exception as error:

        print("\nERROR:")
        print(error)