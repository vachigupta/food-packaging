import pandas as pd
import joblib
from sklearn.ensemble import RandomForestRegressor


# Load training data
data = pd.read_csv("data/training_data.csv")


# Features used by the Random Forest
features = [
    "moisture_requirement",
    "gas_requirement",
    "light_requirement",
    "mechanical_requirement",
    "temperature",
    "humidity",
    "packaging_moisture_barrier",
    "packaging_gas_barrier",
    "packaging_light_barrier",
    "packaging_mechanical_strength",
    "packaging_sealability",
    "cost_score",
    "sustainability_score"
]


# Input features
X = data[features]

# Target value
y = data["score"]


# Create Random Forest model
model = RandomForestRegressor(
    n_estimators=100,
    random_state=42
)


# Train the model
model.fit(X, y)

print("Random Forest training completed!")


# Save trained model
joblib.dump(
    model,
    "model/ranking_model.pkl"
)

print("Model saved successfully!")


def predict_score(
    moisture,
    gas,
    light,
    mechanical,
    temperature,
    humidity,
    packaging_moisture_barrier,
    packaging_gas_barrier,
    packaging_light_barrier,
    packaging_mechanical_strength,
    packaging_sealability,
    cost_score,
    sustainability_score
):
    """
    Predict the suitability score for a packaging option.
    """

    input_data = pd.DataFrame([{
        "moisture_requirement": moisture,
        "gas_requirement": gas,
        "light_requirement": light,
        "mechanical_requirement": mechanical,
        "temperature": temperature,
        "humidity": humidity,
        "packaging_moisture_barrier":
            packaging_moisture_barrier,
        "packaging_gas_barrier":
            packaging_gas_barrier,
        "packaging_light_barrier":
            packaging_light_barrier,
        "packaging_mechanical_strength":
            packaging_mechanical_strength,
        "packaging_sealability":
            packaging_sealability,
        "cost_score": cost_score,
        "sustainability_score":
            sustainability_score
    }])

    prediction = model.predict(input_data)

    return prediction[0]


# Test the model
test_score = predict_score(
    moisture=3,
    gas=3,
    light=2,
    mechanical=3,
    temperature=25,
    humidity=60,
    packaging_moisture_barrier=4,
    packaging_gas_barrier=4,
    packaging_light_barrier=4,
    packaging_mechanical_strength=3,
    packaging_sealability=3,
    cost_score=1,
    sustainability_score=4
)

print(
    "Test packaging score:",
    round(test_score, 2)
)