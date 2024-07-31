import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import RandomForestRegressor

def load_and_preprocess_data(file_path):
    data = pd.read_csv(file_path)
    scaler = MinMaxScaler()
    data_scaled = pd.DataFrame(scaler.fit_transform(data), columns=data.columns)
    return data_scaled

def train_model(data):
    X = data.drop('performance_metric', axis=1)
    y = data['performance_metric']
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)
    return model

def analyze_campaigns(model, data):
    predictions = model.predict(data)
    best_campaign = data.iloc[predictions.argmax()]
    return best_campaign

def main():
    file_path = 'campaign_data.csv'
    data = load_and_preprocess_data(file_path)
    model = train_model(data)
    best_campaign = analyze_campaigns(model, data)
    
    print(f"Best performing campaign: {best_campaign.name}")
    
    if best_campaign.name == 'facebook_ads':
        print("Facebook Ads is the best performing campaign. Consider increasing its budget.")
    else:
        print(f"Facebook Ads is not the best performing campaign. The best campaign is {best_campaign.name}.")

    # Additional analysis for Facebook Ads
    facebook_performance = data.loc['facebook_ads', 'performance_metric']
    print(f"\nFacebook Ads performance metric: {facebook_performance}")
    
    all_performances = data['performance_metric']
    facebook_rank = all_performances.rank(ascending=False)[facebook_performance]
    print(f"Facebook Ads rank among all campaigns: {facebook_rank} out of {len(all_performances)}")

    average_performance = all_performances.mean()
    if facebook_performance > average_performance:
        print("Facebook Ads is performing above average.")
    else:
        print("Facebook Ads is performing below average.")

if __name__ == "__main__":
    main()