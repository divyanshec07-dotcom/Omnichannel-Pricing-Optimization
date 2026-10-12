import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import gc

if __name__ == "__main__":
    print("Step 1: Loading processed dataset...")
    df = pd.read_pickle('data/processed_pricing_data.pkl')

    print("Step 2: Filtering data for Store CA_1 to optimize memory...")
    # Drop rows with missing prices to ensure clean training data
    df = df[df['store_id'] == 'CA_1'].dropna(subset=['sell_price', 'sales'])

    print("Step 3: Engineering features...")
    # Defining our feature variables (X) and target variable (y)
    X = df[['sell_price', 'snap_CA', 'snap_TX', 'snap_WI']]
    y = df['sales']

    print("Step 4: Splitting data into train and test sets...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Free up memory before training
    del df, X, y
    gc.collect()

    print("Step 5: Training the Random Forest Regressor...")
    # n_estimators=20 and max_depth=5 keeps the model lightweight for standard hardware
    model = RandomForestRegressor(n_estimators=20, max_depth=5, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)

    print("Step 6: Evaluating the pricing engine...")
    predictions = model.predict(X_test)
    mse = mean_squared_error(y_test, predictions)
    print(f"  -> Model Mean Squared Error (MSE): {mse:.2f}")
    
    print("Algorithm execution complete. Ready for business integration.")