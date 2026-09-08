import numpy as np
from app.ai.semantic.model import model
CATEGORIES = {
    "disaster_management": {
        "label": "Disaster Management",
        "prototypes": [
            "natural disasters, floods, droughts, lightning and disaster response",
            "emergency management, rescue operations and disaster preparedness",
            "fire accidents, road accidents and emergency response systems",
        ],
    },

    "agriculture": {
        "label": "Agriculture & Food Security",
        "prototypes": [
            "farming, agriculture, crops and agricultural productivity",
            "farmers, irrigation, agricultural technology and rural farming",
            "food security, crop production and agricultural supply chains",
        ],
    },

    "health": {
        "label": "Health & Medical",
        "prototypes": [
            "healthcare, hospitals, doctors and medical services",
            "access to healthcare and medical facilities in rural areas",
            "disease prevention, medicines and public health",
        ],
    },

    "education": {
        "label": "Education",
        "prototypes": [
            "schools, students, teachers and education",
            "access to quality education and learning resources",
            "digital education, classrooms and educational infrastructure",
        ],
    },

    "water_sanitation": {
        "label": "Water & Sanitation",
        "prototypes": [
            "drinking water supply and access to clean water",
            "sanitation, toilets, sewage and wastewater management",
            "water resources, water quality and rural water supply",
        ],
    },

    "infrastructure": {
        "label": "Roads & Infrastructure",
        "prototypes": [
            "roads, bridges and transportation infrastructure",
            "public infrastructure and connectivity",
            "poor roads, damaged infrastructure and transportation problems",
        ],
    },

    "environment": {
        "label": "Environment & Forest",
        "prototypes": [
            "environmental pollution, waste management and climate problems",
            "forests, forest fires and environmental conservation",
            "land degradation, pollution and environmental protection",
        ],
    },

    "mining": {
        "label": "Mining & Industrial Safety",
        "prototypes": [
            "mining operations and mining safety",
            "industrial accidents, chemical hazards and workplace safety",
            "coal mining, mine workers and industrial risk management",
        ],
    },

    "tribal_welfare": {
        "label": "Tribal & Social Welfare",
        "prototypes": [
            "tribal communities and tribal welfare",
            "social welfare programs for disadvantaged communities",
            "support for vulnerable and socially marginalized communities",
        ],
    },

    "employment": {
        "label": "Employment & Skill Development",
        "prototypes": [
            "employment opportunities and unemployment",
            "job creation, vocational training and skill development",
            "workforce development and livelihood opportunities",
        ],
    },

    "urban_development": {
        "label": "Urban Development & Housing",
        "prototypes": [
            "urban development, cities and municipal services",
            "housing, urban planning and city infrastructure",
            "traffic, urban flooding and problems caused by rapid urbanization",
        ],
    },
    "energy": {
    "label": "Energy",
    "prototypes": [
        "problems related to energy and electricity",
        "challenges involving solar power and renewable energy",
        "issues with electricity access and power supply",
        "problems with solar panels and energy generation",
        "challenges involving renewable energy infrastructure",
        "energy shortages and unreliable electricity",
        "problems with installation and maintenance of energy systems"
    ]
},
}


# Encode all category prototypes once when the service starts.
PROTOTYPE_EMBEDDINGS = {}

for category, data in CATEGORIES.items():
    embeddings = model.encode(
        data["prototypes"],
        normalize_embeddings=True
    )

    PROTOTYPE_EMBEDDINGS[category] = embeddings


def classify_semantic(challenge: str, top_k: int = 3):
    """
    Classify a challenge using semantic similarity.

    Returns:
        category
        category_label
        confidence
        top_predictions
        uncertain
    """

    if not challenge or not challenge.strip():
        return {
            "category": "other",
            "category_label": "Other",
            "confidence": 0.0,
            "top_predictions": [],
            "uncertain": True,
        }

    challenge_embedding = model.encode(
        challenge,
        normalize_embeddings=True
    )

    category_scores = {}

    for category, prototype_embeddings in PROTOTYPE_EMBEDDINGS.items():

        similarities = np.dot(
            prototype_embeddings,
            challenge_embedding
        )

        # Use the two strongest prototype matches.
        top_scores = np.sort(similarities)[-2:]

        score = float(np.mean(top_scores))

        category_scores[category] = score

    ranked = sorted(
        category_scores.items(),
        key=lambda item: item[1],
        reverse=True
    )

    best_category, best_score = ranked[0]
    second_category, second_score = ranked[1]

    margin = best_score - second_score

    # Relative confidence, not a calibrated probability.
    temperature = 0.05

    scores_array = np.array(
        [score for _, score in ranked]
    )

    probabilities = np.exp(
        (scores_array - np.max(scores_array)) / temperature
    )

    probabilities /= probabilities.sum()

    confidence = float(probabilities[0])

    # Initial uncertainty rules.
    # We will tune these after testing.
    uncertain = (
        best_score < 0.35
        or margin < 0.02
    )

    if best_score < 0.35:
        final_category = "other"
        final_label = "Other"
    else:
        final_category = best_category
        final_label = CATEGORIES[best_category]["label"]

    top_predictions = []

    for index, (category, score) in enumerate(ranked[:top_k]):

        top_predictions.append({
            "category": category,
            "label": CATEGORIES[category]["label"],
            "score": round(float(score), 4),
        })

    return {
        "category": final_category,
        "category_label": final_label,
        "confidence": round(confidence, 4),
        "semantic_score": round(best_score, 4),
        "margin": round(margin, 4),
        "top_predictions": top_predictions,
        "uncertain": uncertain,
    }