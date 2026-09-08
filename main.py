from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import json
import os

from services.requirement_engine import get_requirements
from services.recommendation_engine import get_recommendations


# ============================================================
# APP
# ============================================================

app = FastAPI(
    title="WrapWise - Intelligent Food Packaging",
    description="AI-assisted food packaging recommendation system",
    version="1.0"
)


# ============================================================
# BASE DIRECTORY
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# ============================================================
# FRONTEND DIRECTORY
# ============================================================

FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

app.mount(
    "/frontend",
    StaticFiles(directory=FRONTEND_DIR),
    name="frontend"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# LOAD DATABASES
# ============================================================

with open(
    os.path.join(BASE_DIR, "data", "commodities.json"),
    "r"
) as file:
    commodities = json.load(file)

with open(
    os.path.join(BASE_DIR, "data", "packaging.json"),
    "r"
) as file:
    packaging = json.load(file)


# ============================================================
# REQUEST MODEL
# ============================================================

class RecommendationRequest(BaseModel):
    commodity: str
    form: str
    temperature: float
    relative_humidity: float
    target_shelf_life: float
    storage_condition: str
    transportation_distance_km: float
    priority: str
    weights: dict


# ============================================================
# HOME PAGE
# ============================================================

@app.get("/")
def home():
    frontend_path = os.path.join(
        FRONTEND_DIR,
        "index (1).html"
    )

    return FileResponse(frontend_path)


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


# ============================================================
# GET COMMODITIES
# ============================================================

@app.get("/commodities")
def get_commodities():
    return commodities


# ============================================================
# GET PACKAGING DATABASE
# ============================================================

@app.get("/packaging")
def get_packaging():
    return packaging


# ============================================================
# GET COMMODITY REQUIREMENTS
# ============================================================

@app.get("/requirements/{commodity}")
def get_commodity_requirements(commodity: str):

    commodity = commodity.lower()

    if commodity not in commodities:
        return {
            "status": "error",
            "message": "Commodity not found"
        }

    requirements = get_requirements(commodity)

    return {
        "status": "success",
        "commodity": commodities[commodity]["name"],
        "requirements": requirements
    }


# ============================================================
# RECOMMENDATION API
# ============================================================

@app.post("/api/recommend")
def recommend(request: RecommendationRequest):

    commodity = request.commodity.lower()

    # --------------------------------------------------------
    # Check commodity
    # --------------------------------------------------------

    if commodity not in commodities:
        return {
            "status": "error",
            "summary": "Unknown commodity",
            "recommendations": []
        }

    # --------------------------------------------------------
    # Get packaging requirements
    # --------------------------------------------------------

    requirements = get_requirements(commodity)

    # --------------------------------------------------------
    # Generate recommendations
    # --------------------------------------------------------

    recommendations = get_recommendations(
        requirements=requirements,
        temperature=request.temperature,
        humidity=request.relative_humidity,
        target_shelf_life=request.target_shelf_life,
        storage_condition=request.storage_condition,
        transportation_distance_km=request.transportation_distance_km,
        priority=request.priority,
        weights=request.weights
    )

    # --------------------------------------------------------
    # Return complete response
    # --------------------------------------------------------

    return {
        "status": "success",

        "commodity": {
            "id": commodity,
            "name": commodities[commodity]["name"],
            "form": request.form
        },

        "input_conditions": {
            "temperature": request.temperature,
            "relative_humidity": request.relative_humidity,
            "target_shelf_life": request.target_shelf_life,
            "storage_condition": request.storage_condition,
            "transportation_distance_km": request.transportation_distance_km,
            "priority": request.priority,
            "weights": request.weights
        },

        "requirements": {
            "moisture_barrier": requirements["moisture_barrier"],
            "gas_requirement": requirements["gas_barrier"],
            "light_barrier": requirements["light_barrier"],
            "mechanical_strength": requirements["mechanical_strength"],
            "sealability": requirements["sealability"],
            "temperature_suitability": "checked",
            "food_contact": True
        },

        "recommendations": recommendations,

        "warning": (
            "This prototype uses simulated packaging performance data. "
            "Recommendations require experimental and regulatory validation."
        )
    }