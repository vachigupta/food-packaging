import json

from model.ranking_model import predict_score


# ============================================================
# LOAD PACKAGING DATABASE
# ============================================================

with open("data/packaging.json", "r") as file:
    packaging_data = json.load(file)


# ============================================================
# QUALITATIVE LEVELS
# ============================================================

LEVELS = {
    "low": 1,
    "medium": 2,
    "high": 3,
    "very high": 4
}


# ============================================================
# WVTR -> MOISTURE BARRIER SCORE
# Lower WVTR = Better moisture barrier
# ============================================================

def barrier_score_from_wvtr(wvtr):

    if wvtr <= 0.05:
        return 4

    elif wvtr <= 0.5:
        return 3

    elif wvtr <= 2:
        return 2

    return 1


# ============================================================
# OTR -> GAS/OXYGEN BARRIER SCORE
# Lower OTR = Better oxygen barrier
# ============================================================

def barrier_score_from_otr(otr):

    if otr <= 0.1:
        return 4

    elif otr <= 30:
        return 3

    elif otr <= 1500:
        return 2

    return 1


# ============================================================
# SEALABILITY SCORE
# ============================================================

def sealability_score(sealability):

    if sealability == "excellent":
        return 3

    elif sealability == "good":
        return 2

    return 1


# ============================================================
# COST SCORE
# ============================================================

def cost_score(cost_tier):

    if cost_tier == "low":
        return 3

    elif cost_tier == "medium":
        return 2

    return 1


# ============================================================
# ML PACKAGING SCORE
# ============================================================

def calculate_packaging_score(
    packaging,
    requirements,
    temperature,
    humidity
):

    moisture_requirement = LEVELS[
        requirements["moisture_barrier"]
    ]

    gas_requirement = LEVELS[
        requirements["gas_barrier"]
    ]

    light_requirement = LEVELS[
        requirements["light_barrier"]
    ]

    mechanical_requirement = LEVELS[
        requirements["mechanical_strength"]
    ]

    packaging_moisture_barrier = barrier_score_from_wvtr(
        packaging["WVTR"]
    )

    packaging_gas_barrier = barrier_score_from_otr(
        packaging["OTR"]
    )

    packaging_light_barrier = LEVELS[
        packaging["light_barrier"]
    ]

    packaging_mechanical_strength = LEVELS[
        packaging["mechanical_strength"]
    ]

    packaging_sealability = sealability_score(
        packaging["sealability"]
    )

    packaging_cost_score = cost_score(
        packaging["cost_tier"]
    )

    score = predict_score(
        moisture=moisture_requirement,
        gas=gas_requirement,
        light=light_requirement,
        mechanical=mechanical_requirement,
        temperature=temperature,
        humidity=humidity,
        packaging_moisture_barrier=packaging_moisture_barrier,
        packaging_gas_barrier=packaging_gas_barrier,
        packaging_light_barrier=packaging_light_barrier,
        packaging_mechanical_strength=packaging_mechanical_strength,
        packaging_sealability=packaging_sealability,
        cost_score=packaging_cost_score,
        sustainability_score=packaging[
            "sustainability_score"
        ]
    )

    return round(
        max(0, min(100, score)),
        2
    )


# ============================================================
# GENERATE REASONS
# ============================================================

def generate_reasons(packaging, requirements):

    reasons = []

    # Moisture
    if requirements["moisture_barrier"] in [
        "high",
        "very high"
    ]:

        if packaging["WVTR"] <= 0.5:
            reasons.append(
                "Strong moisture barrier."
            )

    # Oxygen / gas
    if requirements["gas_barrier"] in [
        "high",
        "very high"
    ]:

        if packaging["OTR"] <= 30:
            reasons.append(
                "Strong gas/oxygen barrier."
            )

    # Light
    required_light = LEVELS[
        requirements["light_barrier"]
    ]

    actual_light = LEVELS[
        packaging["light_barrier"]
    ]

    if actual_light >= required_light:
        reasons.append(
            "Adequate light protection."
        )

    # Mechanical
    required_strength = LEVELS[
        requirements["mechanical_strength"]
    ]

    actual_strength = LEVELS[
        packaging["mechanical_strength"]
    ]

    if actual_strength >= required_strength:
        reasons.append(
            "Good mechanical protection."
        )

    # Sealability
    if packaging["sealability"] == "excellent":
        reasons.append(
            "Excellent sealability."
        )

    # Food contact
    if packaging["food_contact"]:
        reasons.append(
            "Marked as food-contact suitable in prototype data."
        )

    return reasons


# ============================================================
# GENERATE TRADE-OFFS
# ============================================================

def generate_tradeoffs(packaging):

    tradeoffs = []

    if packaging["cost_tier"] == "high":

        tradeoffs.append(
            "Higher cost."
        )

    elif packaging["cost_tier"] == "medium":

        tradeoffs.append(
            "Moderate cost."
        )

    if not packaging["recyclable"]:

        tradeoffs.append(
            "Not recyclable in the prototype dataset."
        )

    if packaging["sustainability_score"] <= 5:

        tradeoffs.append(
            "Lower sustainability score."
        )

    if packaging["sealability"] == "poor":

        tradeoffs.append(
            "Poor sealability."
        )

    return tradeoffs


# ============================================================
# MAIN RECOMMENDATION ENGINE
# ============================================================

def get_recommendations(
    requirements,
    temperature,
    humidity,
    target_shelf_life=180,
    storage_condition="ambient",
    transportation_distance_km=500,
    priority="balanced",
    weights=None
):

    results = []
    rejected = []

    # Default weights
    if weights is None:

        weights = {
            "shelf_life": 5,
            "cost": 5,
            "sustainability": 5
        }

    # Make sure weights are valid
    shelf_weight = max(
        0,
        min(10, float(weights.get("shelf_life", 5)))
    )

    cost_weight = max(
        0,
        min(10, float(weights.get("cost", 5)))
    )

    sustainability_weight = max(
        0,
        min(10, float(weights.get("sustainability", 5)))
    )


    # ========================================================
    # EVALUATE EACH PACKAGING
    # ========================================================

    for packaging_id, packaging in packaging_data.items():

        # ----------------------------------------------------
        # HARD CONSTRAINT: FOOD CONTACT
        # ----------------------------------------------------

        if not packaging["food_contact"]:

            rejected.append({
                "packaging_id": packaging_id,
                "reason": "Not suitable for food contact"
            })

            continue


        # ----------------------------------------------------
        # HARD CONSTRAINT: TEMPERATURE
        # ----------------------------------------------------

        if (
            temperature < packaging["temperature_min"]
            or
            temperature > packaging["temperature_max"]
        ):

            rejected.append({
                "packaging_id": packaging_id,
                "reason": "Temperature outside packaging range"
            })

            continue


        # ----------------------------------------------------
        # BASE ML SCORE
        # ----------------------------------------------------

        ml_score = calculate_packaging_score(
            packaging=packaging,
            requirements=requirements,
            temperature=temperature,
            humidity=humidity
        )

        adjusted_score = ml_score


        # ====================================================
        # USER WEIGHTING
        # ====================================================

        # Normalize weights to a small influence range.
        # This prevents sliders from completely overpowering ML.

        weight_total = (
            shelf_weight
            + cost_weight
            + sustainability_weight
        )

        if weight_total == 0:
            weight_total = 1


        # ----------------------------------------------------
        # SHELF-LIFE PREFERENCE
        # ----------------------------------------------------

        shelf_component = 0

        if packaging["WVTR"] <= 0.5:
            shelf_component += 2

        if packaging["OTR"] <= 30:
            shelf_component += 2

        shelf_bonus = (
            shelf_component
            * (shelf_weight / weight_total)
            * 4
        )

        adjusted_score += shelf_bonus


        # ----------------------------------------------------
        # COST PREFERENCE
        # ----------------------------------------------------

        cost_component = cost_score(
            packaging["cost_tier"]
        )

        cost_bonus = (
            cost_component
            * (cost_weight / weight_total)
            * 2
        )

        adjusted_score += cost_bonus


        # ----------------------------------------------------
        # SUSTAINABILITY PREFERENCE
        # ----------------------------------------------------

        sustainability_bonus = (
            packaging["sustainability_score"]
            * (sustainability_weight / weight_total)
            * 1.5
        )

        adjusted_score += sustainability_bonus


        # ====================================================
        # PRIMARY PRIORITY
        # ====================================================

        if priority == "cost":

            if packaging["cost_tier"] == "low":
                adjusted_score += 5

            elif packaging["cost_tier"] == "medium":
                adjusted_score += 2


        elif priority == "sustainability":

            adjusted_score += (
                packaging["sustainability_score"]
                * 1.5
            )


        elif priority == "shelf_life":

            if packaging["WVTR"] <= 0.5:
                adjusted_score += 4

            if packaging["OTR"] <= 30:
                adjusted_score += 4


        elif priority == "balanced":

            adjusted_score += (
                packaging["sustainability_score"]
                * 0.5
            )


        # ====================================================
        # TRANSPORTATION
        # ====================================================

        if transportation_distance_km > 500:

            if packaging["mechanical_strength"] in [
                "high",
                "very high"
            ]:

                adjusted_score += 2


        # ====================================================
        # LONG SHELF LIFE
        # ====================================================

        if target_shelf_life > 180:

            if packaging["WVTR"] <= 0.5:
                adjusted_score += 2

            if packaging["OTR"] <= 30:
                adjusted_score += 2


        # ====================================================
        # STORAGE CONDITION
        # ====================================================

        # Additional temperature compatibility is already
        # checked as a hard constraint.

        if storage_condition == "frozen":

            if packaging["temperature_min"] <= -18:
                adjusted_score += 1


        elif storage_condition == "chilled":

            if (
                packaging["temperature_min"] <= 2
                and packaging["temperature_max"] >= 8
            ):
                adjusted_score += 1


        # Keep score between 0 and 100
        adjusted_score = max(
            0,
            min(100, adjusted_score)
        )


        # ====================================================
        # EXPLANATIONS
        # ====================================================

        reasons = generate_reasons(
            packaging,
            requirements
        )

        tradeoffs = generate_tradeoffs(
            packaging
        )

        warnings = []

        if packaging["source"] == "Prototype simulated data":

            warnings.append(
                "Packaging performance values are simulated "
                "prototype data and require experimental validation."
            )


        # ====================================================
        # RESULT
        # ====================================================

        results.append({

            "packaging_id": packaging_id,

            "packaging": packaging["name"],

            "family": packaging["family"],

            "score": round(
                adjusted_score,
                2
            ),

            "reasons": reasons,

            "tradeoffs": tradeoffs,

            "warnings": warnings,

            "food_contact": packaging["food_contact"],

            "recyclable": packaging["recyclable"],

            "otr": packaging["OTR"],

            "otr_unit": packaging["OTR_unit"],

            "wvtr": packaging["WVTR"],

            "wvtr_unit": packaging["WVTR_unit"],

            "thickness": packaging["thickness"],

            "thickness_unit": packaging["thickness_unit"],

            "mechanical_strength":
                packaging["mechanical_strength"],

            "sealability":
                packaging["sealability"],

            "temperature_range": (
                f"{packaging['temperature_min']} "
                f"to {packaging['temperature_max']} C"
            ),

            "cost_tier":
                packaging["cost_tier"],

            "sustainability_score":
                packaging["sustainability_score"],

            "source":
                packaging["source"]
        })


    # ========================================================
    # SORT
    # ========================================================

    results.sort(
        key=lambda item: item["score"],
        reverse=True
    )


    # Return Top 3
    return results[:3]