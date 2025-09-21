import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
import pickle

data = pd.read_csv("insurance.csv")
print("CSV loaded successfully")
print(data.head())

X = data[['age', 'sex', 'bmi', 'children', 'smoker', 'region']]
y = data['charges']

categorical_features = ['sex', 'smoker', 'region']
numerical_features = ['age', 'bmi', 'children']

preprocessor = ColumnTransformer(
    transformers=[
        ('cat', OneHotEncoder(), categorical_features),
    ],
    remainder='passthrough'
)

model_pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('regressor', RandomForestRegressor(n_estimators=100, random_state=42))
])

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print(f"Training shape: {X_train.shape}, Test shape: {X_test.shape}")

model_pipeline.fit(X_train, y_train)
print("Model training completed")

y_pred = model_pipeline.predict(X_test)
mse = mean_squared_error(y_test, y_pred)
print(f"Test MSE: {mse:.2f}")

with open("model.pkl", "wb") as f:
    pickle.dump(model_pipeline, f)
print("Model saved as 'model.pkl'")
