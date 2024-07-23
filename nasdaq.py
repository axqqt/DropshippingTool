import pandas as pd
import numpy as np

# Load the CSV file
df = pd.read_csv("NASDAQ.csv")

# Convert the 'Date' column to datetime
df['Date'] = pd.to_datetime(df['Date'])

# Sort the dataframe by date
df = df.sort_values('Date')

# Calculate short-term (5-day) and long-term (20-day) moving averages
df['SMA5'] = df['Price'].rolling(window=5).mean()
df['SMA20'] = df['Price'].rolling(window=20).mean()

# Initialize columns for signals and positions
df['Signal'] = 0
df['Position'] = 0

# Generate buy/sell signals
df.loc[df['SMA5'] > df['SMA20'], 'Signal'] = 1  # Buy signal
df.loc[df['SMA5'] < df['SMA20'], 'Signal'] = -1  # Sell signal

# Calculate positions
df['Position'] = df['Signal'].diff()

# Calculate returns
df['Returns'] = df['Price'].pct_change()
df['Strategy_Returns'] = df['Position'].shift(1) * df['Returns']

# Calculate cumulative returns
df['Cumulative_Returns'] = (1 + df['Returns']).cumprod()
df['Strategy_Cumulative_Returns'] = (1 + df['Strategy_Returns']).cumprod()

# Print the final cumulative returns
print(f"Buy and Hold Returns: {df['Cumulative_Returns'].iloc[-1]:.2f}")
print(f"Strategy Returns: {df['Strategy_Cumulative_Returns'].iloc[-1]:.2f}")

# Print the last few rows to see the signals and positions
print(df[['Date', 'Price', 'SMA5', 'SMA20', 'Signal', 'Position', 'Strategy_Returns']].tail())