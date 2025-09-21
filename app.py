import numpy as np
import pandas as pd
from flask import Flask, request, render_template
import pickle

# Create Flask app
flask_app = Flask(__name__)

# Load trained model
model = pickle.load(open("model.pkl", "rb"))

@flask_app.route("/")
def Home():
    return render_template("index.html")

@flask_app.route("/predict", methods=["POST"])
def predict():
    # Extract form inputs
    age = float(request.form['age'])
    bmi = float(request.form['bmi'])
    children = float(request.form['children'])
    sex = request.form['sex']
    smoker = request.form['smoker']
    region = request.form['region']

    # Create DataFrame matching training columns
    input_data = pd.DataFrame({
        'age': [age],
        'bmi': [bmi],
        'children': [children],
        'sex': [sex],
        'smoker': [smoker],
        'region': [region]
    })

    # Make prediction
    prediction = model.predict(input_data)[0]  # get scalar

    return render_template("index.html", 
                           prediction_text=f"Your Medical Insurance Prediction is ${prediction:,.2f}")

if __name__ == "__main__":
    flask_app.run(debug=True)
