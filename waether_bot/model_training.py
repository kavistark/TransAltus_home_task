import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import joblib

# Melt function
def melt_dataset(file_path, value_name):
    df = pd.read_csv(file_path)
    return df.melt(id_vars=['datetime'], var_name='city', value_name=value_name)

# Load and melt datasets
temp_df = melt_dataset('dataset2/temperature.csv', 'temperature')
humidity_df = melt_dataset('dataset2/humidity.csv', 'humidity')
pressure_df = melt_dataset('dataset2/pressure.csv', 'pressure')
wind_speed_df = melt_dataset('dataset2/wind_speed.csv', 'wind_speed')

# Merge datasets
merged_df = temp_df.merge(humidity_df, on=['datetime', 'city']) \
                   .merge(pressure_df, on=['datetime', 'city']) \
                   .merge(wind_speed_df, on=['datetime', 'city'])

# Feature engineering
merged_df['datetime'] = pd.to_datetime(merged_df['datetime'])
merged_df['day_of_year'] = merged_df['datetime'].dt.dayofyear
merged_df['month'] = merged_df['datetime'].dt.month
merged_df['hour'] = merged_df['datetime'].dt.hour
merged_df['day_of_week'] = merged_df['datetime'].dt.dayofweek

# Add season numeric
season_map = {'Winter': 0, 'Spring': 1, 'Summer': 2, 'Fall': 3}
merged_df['season'] = merged_df['month'].apply(lambda x: 
    'Winter' if x in [12, 1, 2] else
    'Spring' if x in [3, 4, 5] else
    'Summer' if x in [6, 7, 8] else 'Fall')
merged_df['season_numeric'] = merged_df['season'].map(season_map)

# Drop missing values
merged_df = merged_df.dropna()

# Train model
X = merged_df[['day_of_year', 'month', 'hour', 'day_of_week', 'season_numeric',
               'humidity', 'pressure', 'wind_speed']]
y = merged_df['temperature']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = LinearRegression()
model.fit(X_train, y_train)

# Evaluate model
y_pred = model.predict(X_test)
print(f"Model trained successfully")
print(f"Mean Squared Error: {mean_squared_error(y_test, y_pred):.2f}")
print(f"R² Score: {r2_score(y_test, y_pred):.2f}")

# Save model and city data
joblib.dump(model, 'temperature_prediction_model.pkl')
merged_df[['city', 'humidity', 'pressure', 'wind_speed']].drop_duplicates().to_csv('city_data.csv', index=False)
print("Model saved as 'temperature_prediction_model.pkl'")
print("City data saved as 'city_data.csv'")
