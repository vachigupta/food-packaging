def get_requirements(commodity):
    """
    Determine the packaging requirements for a commodity.
    """

    requirements = {
        "moisture_barrier": "medium",
        "gas_barrier": "medium",
        "light_barrier": "medium",
        "mechanical_strength": "medium",
        "sealability": "good"
    }

    # Grain commodities
    if commodity in ["wheat", "rice", "maize"]:
        requirements = {
            "moisture_barrier": "high",
            "gas_barrier": "high",
            "light_barrier": "medium",
            "mechanical_strength": "high",
            "sealability": "good"
        }

    # Potato
    elif commodity == "potato":
        requirements = {
            "moisture_barrier": "medium",
            "gas_barrier": "low",
            "light_barrier": "high",
            "mechanical_strength": "very high",
            "sealability": "good"
        }

    # Tomato
    elif commodity == "tomato":
        requirements = {
            "moisture_barrier": "medium",
            "gas_barrier": "low",
            "light_barrier": "medium",
            "mechanical_strength": "very high",
            "sealability": "good"
        }

    return requirements