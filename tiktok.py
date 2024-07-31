import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import RandomForestRegressor

# Load and preprocess data
def load_and_preprocess_data(file_path):
    data = pd.read_csv(file_path)
    scaler = MinMaxScaler()
    data_scaled = pd.DataFrame(scaler.fit_transform(data), columns=data.columns)
    return data_scaled

# Train AI model
def train_model(data):
    X = data.drop('performance_metric', axis=1)
    y = data['performance_metric']
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)
    return model

# Analyze campaigns
def analyze_campaigns(model, data):
    predictions = model.predict(data)
    best_campaign = data.iloc[predictions.argmax()]
    return best_campaign

# Main function
def main():
    file_path = 'campaign_data.csv'
    data = load_and_preprocess_data(file_path)
    model = train_model(data)
    best_campaign = analyze_campaigns(model, data)
    
    print(f"Best performing campaign: {best_campaign.name}")
    
    if best_campaign.name == 'tiktok_ads':
        print("TikTok Ads is the best performing campaign. Consider increasing its budget.")
    else:
        print(f"TikTok Ads is not the best performing campaign. The best campaign is {best_campaign.name}.")

if __name__ == "__main__":
    main()