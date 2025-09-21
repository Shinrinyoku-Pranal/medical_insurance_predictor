import pandas as pd
from flask import Flask, request, render_template, jsonify
import pickle
import traceback

flask_app = Flask(__name__)

# Load trained model
# Make sure model.pkl is in the same directory or adjust the path
MODEL_PATH = "model.pkl"
try:
    model = pickle.load(open(MODEL_PATH, "rb"))
except Exception as e:
    # If model load fails, fail loudly so you fix it before running.
    raise RuntimeError(f"Failed to load model from {MODEL_PATH}: {e}")

# Neutral/default values used to compute single-feature contributions.
# These are reasonable defaults; tune them if you know your training data stats.
NEUTRAL = {
    "age": 40,
    "bmi": 25.0,
    "children": 0,
    "sex": "female",
    "smoker": "no",
    "region": "northeast"
}


def build_input_df(age, bmi, children, sex, smoker, region):
    """Return a single-row DataFrame matching the columns your model expects."""
    return pd.DataFrame({
        "age": [age],
        "bmi": [bmi],
        "children": [children],
        "sex": [sex],
        "smoker": [smoker],
        "region": [region]
    })


@flask_app.route("/")
def home():
    return render_template("index.html")


def safe_float(x, default=0.0):
    try:
        return float(x)
    except Exception:
        return default


@flask_app.route("/predict", methods=["POST"])
def predict_form():
    """Handles regular form POST (server-rendered)."""
    try:
        # Parse & validate
        age = safe_float(request.form.get("age", ""))
        bmi = safe_float(request.form.get("bmi", ""))
        children = safe_float(request.form.get("children", ""))
        sex = request.form.get("sex", "") or NEUTRAL["sex"]
        smoker = request.form.get("smoker", "") or NEUTRAL["smoker"]
        region = request.form.get("region", "") or NEUTRAL["region"]

        input_df = build_input_df(age, bmi, children, sex, smoker, region)
        base_pred = float(model.predict(input_df)[0])

        # Compute contributions by replacing each feature with a neutral value and taking the delta.
        contributions = {}
        features = ["age", "bmi", "children", "sex", "smoker", "region"]
        for feat in features:
            mod = input_df.copy(deep=True)
            mod[feat] = [NEUTRAL[feat]]
            try:
                mod_pred = float(model.predict(mod)[0])
                # contribution is difference from base: positive means neutral reduces cost (so original feature increased it)
                delta = base_pred - mod_pred
            except Exception:
                delta = 0.0
            # Round to two decimals for display
            contributions[feat] = round(delta, 2)

        # What-if scenarios
        # 1) Non-smoker scenario
        non_smoker = input_df.copy()
        non_smoker["smoker"] = ["no"]
        non_smoker_pred = float(model.predict(non_smoker)[0])

        # 2) Lower BMI by 5 (but keep a sensible floor)
        lower_bmi = input_df.copy()
        lower_bmi["bmi"] = [max(18.0, bmi - 5.0)]
        lower_bmi_pred = float(model.predict(lower_bmi)[0])

        base_cost = 3000  # simple illustrative base; you can compute this from training set if available

        return render_template(
            "index.html",
            prediction=round(base_pred, 2),
            contributions=contributions,
            base_cost=base_cost,
            non_smoker_pred=round(non_smoker_pred, 2),
            lower_bmi_pred=round(lower_bmi_pred, 2),
            form_values={"age": age, "bmi": bmi, "children": children, "sex": sex, "smoker": smoker, "region": region}
        )

    except Exception as e:
        traceback.print_exc()
        return render_template("index.html", error=f"Error computing prediction: {str(e)}")


@flask_app.route("/api/predict", methods=["POST"])
def api_predict():
    """JSON API used by the frontend to request predictions & contributions (AJAX)."""
    try:
        payload = request.get_json() or {}
        age = safe_float(payload.get("age", NEUTRAL["age"]))
        bmi = safe_float(payload.get("bmi", NEUTRAL["bmi"]))
        children = safe_float(payload.get("children", NEUTRAL["children"]))
        sex = payload.get("sex", NEUTRAL["sex"])
        smoker = payload.get("smoker", NEUTRAL["smoker"])
        region = payload.get("region", NEUTRAL["region"])

        input_df = build_input_df(age, bmi, children, sex, smoker, region)
        base_pred = float(model.predict(input_df)[0])

        contributions = {}
        features = ["age", "bmi", "children", "sex", "smoker", "region"]
        for feat in features:
            mod = input_df.copy(deep=True)
            mod[feat] = [NEUTRAL[feat]]
            try:
                mod_pred = float(model.predict(mod)[0])
                delta = base_pred - mod_pred
            except Exception:
                delta = 0.0
            contributions[feat] = round(delta, 2)

        non_smoker = input_df.copy()
        non_smoker["smoker"] = ["no"]
        non_smoker_pred = float(model.predict(non_smoker)[0])

        lower_bmi = input_df.copy()
        lower_bmi["bmi"] = [max(18.0, bmi - 5.0)]
        lower_bmi_pred = float(model.predict(lower_bmi)[0])

        return jsonify({
            "prediction": round(base_pred, 2),
            "contributions": contributions,
            "non_smoker_pred": round(non_smoker_pred, 2),
            "lower_bmi_pred": round(lower_bmi_pred, 2),
            "base_cost": 3000
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    flask_app.run(debug=True)
