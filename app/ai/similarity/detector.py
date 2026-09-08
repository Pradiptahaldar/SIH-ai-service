from app.ai.semantic.model import model
import numpy as np

def calculate_similarity(challenge_a: str, challenge_b: str):
    """
    Calculate semantic similarity between two text representations.
    """

    if not challenge_a or not challenge_b:
        return 0.0

    embeddings = model.encode(
        [challenge_a, challenge_b],
        normalize_embeddings=True
    )

    similarity = np.dot(
        embeddings[0],
        embeddings[1]
    )

    return round(float(similarity), 4)


def detect_similarity(challenge: str, existing_challenges: list):
    if not challenge or not existing_challenges:
        return {
            "duplicate": False,
            "similar": False,
            "similarity_score": 0.0,
            "matched_challenge": None
        }

    best_score = -1.0
    best_challenge = None

    for existing in existing_challenges:
        score = calculate_similarity(challenge, existing)

        if score > best_score:
            best_score = score
            best_challenge = existing

    if best_score >= 0.95:
        duplicate = True
        similar = True
    elif best_score >= 0.70:
        duplicate = False
        similar = True
    else:
        duplicate = False
        similar = False

    return {
        "duplicate": duplicate,
        "similar": similar,
        "similarity_score": best_score,
        "matched_challenge": best_challenge
    }


def image_to_text(image_result):
    """
    Convert the existing image-analysis result into
    a semantic text representation for similarity comparison.
    """

    if not image_result:
        return ""

    analysis = image_result.get("analysis")

    if not isinstance(analysis, dict):
        return ""

    category = analysis.get("category")

    if not category:
        return ""

    return f"Image represents a societal challenge related to {category}."