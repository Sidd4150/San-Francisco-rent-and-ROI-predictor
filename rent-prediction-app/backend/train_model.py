"""
Train and save the Gradient Boosting model for rent prediction.
Based on the Jupyter notebook analysis.
"""

import pandas as pd
import numpy as np
import pickle
from pathlib import Path
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import warnings
warnings.filterwarnings('ignore')

def clean_data(df):
    """Clean and preprocess the rental data."""
    # Drop premium data columns and unnecessary columns
    columns_to_drop = [
        'Monthly HOA Fees (Premium Data)', 'Year Built (Premium Data)',
        'Stories (Premium Data)', 'Heating (Premium Data)',
        'Cooling (Premium Data)', 'Fireplaces (Premium Data)',
        'Flooring (Premium Data)', 'Foundation (Premium Data)',
        'Garage Capacity (Premium Data)', 'Sewer (Premium Data)',
        'Subdivision (Premium Data)', 'Zoning Desc. (Premium Data)',
        'Property Condition (Premium Data)', 'Roof Type (Premium Data)',
        'Tax Paid (Most Recent) (Premium Data)', 'Has Private Pool (Premium Data)',
        'Pool Features (Premium Data)', 'Lot Area', 'Lot Area Units',
        'Most Recent Date Listed for Sale', 'Most Recent Price Listed for Sale',
        'City', 'County', 'Listing URL', 'Short Address', 'Address',
        'Zestimate', 'Rent Zestimate', 'State', 'Raw Rent Details',
        'Lowest Rent', 'Highest Rent', 'Tax Assessed Value (Most Recent)',
        'Price Per Sq. Ft.', 'Raw Property Details'
    ]
    
    # Drop columns that exist
    existing_cols = [col for col in columns_to_drop if col in df.columns]
    df = df.drop(columns=existing_cols)
    
    # Convert price to numeric
    df['Price'] = df['Price'].str.replace('$', '').str.replace(',', '').astype(float)
    
    # Fill missing bathrooms with 1 (reasonable assumption)
    df['Baths'] = df['Baths'].fillna(1)
    
    # Drop rows with missing footage (for simplicity in this script)
    df = df.dropna(subset=['Footage', 'Latitude', 'Longitude'])
    
    # Remove outliers
    df = df[(df['Latitude'] >= 37.6) & (df['Longitude'] <= -120)]
    df = df[df['Price'] <= 15000]
    df = df[(df['Footage'] <= 3000) & (df['Footage'] >= 250)]
    
    # Drop Zip column if it exists
    if 'Zip' in df.columns:
        df = df.drop(columns=['Zip'])
    
    return df

def train_gradient_boosting_model(X_train, y_train):
    """Train the Gradient Boosting model with the same parameters as in the notebook."""
    gb_model = GradientBoostingRegressor(
        n_estimators=200,
        learning_rate=0.05,
        max_depth=3,
        min_samples_split=10,
        random_state=42
    )
    
    gb_model.fit(X_train, y_train)
    return gb_model

def main():
    """Main training pipeline."""
    print("SF Rent Prediction Model Training")
    print("=" * 50)
    
    # Check if CSV file exists
    csv_path = input("Enter path to rental listings CSV file (or press Enter to use sample data): ").strip()
    
    if not csv_path:
        # Create sample data for demonstration
        print("\nCreating sample training data...")
        np.random.seed(42)
        n_samples = 500
        
        # Generate synthetic data similar to SF rental market
        sample_data = pd.DataFrame({
            'Price': ['$' + str(int(np.random.normal(3500, 1500, 1)[0])) for _ in range(n_samples)],
            'Beds': np.random.choice([0, 1, 2, 3, 4], n_samples, p=[0.15, 0.35, 0.30, 0.15, 0.05]),
            'Baths': np.random.choice([1.0, 1.5, 2.0, 2.5, 3.0], n_samples, p=[0.40, 0.20, 0.25, 0.10, 0.05]),
            'Footage': np.random.normal(1000, 400, n_samples),
            'Latitude': np.random.uniform(37.70, 37.83, n_samples),
            'Longitude': np.random.uniform(-122.51, -122.36, n_samples)
        })
        
        # Ensure positive footage
        sample_data['Footage'] = np.abs(sample_data['Footage'])
        
        df = sample_data
    else:
        try:
            df = pd.read_csv(csv_path)
            print(f"\nLoaded data from {csv_path}")
            print(f"Shape: {df.shape}")
        except FileNotFoundError:
            print(f"\nError: File not found at {csv_path}")
            return
        except Exception as e:
            print(f"\nError loading CSV: {str(e)}")
            return
    
    # Clean data
    print("\nCleaning data...")
    df = clean_data(df)
    print(f"Cleaned data shape: {df.shape}")
    
    # Prepare features and target
    feature_columns = ['Beds', 'Baths', 'Footage', 'Latitude', 'Longitude']
    X = df[feature_columns].values
    y = df['Price'].values
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    print(f"\nTraining set size: {X_train.shape[0]}")
    print(f"Test set size: {X_test.shape[0]}")
    
    # Train model
    print("\nTraining Gradient Boosting model...")
    model = train_gradient_boosting_model(X_train, y_train)
    
    # Evaluate model
    y_pred = model.predict(X_test)
    r2 = r2_score(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    
    print(f"\nModel Performance:")
    print(f"  R²: {r2:.4f}")
    print(f"  RMSE: ${rmse:,.2f}")
    
    # Feature importance
    feature_importance = pd.DataFrame({
        'Feature': feature_columns,
        'Importance': model.feature_importances_
    }).sort_values('Importance', ascending=False)
    
    print(f"\nFeature Importances:")
    print(feature_importance)
    
    # Save model
    model_dir = Path("models")
    model_dir.mkdir(exist_ok=True)
    
    model_path = model_dir / "gradient_boosting_model.pkl"
    with open(model_path, "wb") as f:
        pickle.dump(model, f)
    
    print(f"\nModel saved to: {model_path}")
    print("\nTraining complete! You can now run the FastAPI server.")

if __name__ == "__main__":
    main()