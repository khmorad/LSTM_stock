import requests
import pandas as pd
import matplotlib.pyplot as plt
import datetime
import numpy as np
from config import API_KEY
#LSTM model

#if the API_KEY is not working make sure to manually include it in this file
#ex: API_KEY = '...'

#not including input for quick testing
company_symbol = 'AAPL'
start_date = '2021-05-01'
end_date = '2023-08-01'
# Function to convert string to datetime object
def str_to_datetime(s):
    str_date = s.split('-')
    year, month, day = int(str_date[0]), int(str_date[1]), int(str_date[2])
    return datetime.datetime(year=year, month=month, day=day)

# Function to create a windowed dataset for LSTM
# need implementation

# Retrieve company information using the Polygon API
company_info_url = f'https://api.polygon.io/v1/meta/symbols/{company_symbol}/company?apiKey={API_KEY}'
response = requests.get(company_info_url)
company_name = response.json()['name']

# Retrieve historical stock data using the Polygon API
url = f'https://api.polygon.io/v2/aggs/ticker/{company_symbol}/range/1/day/{start_date}/{end_date}?apiKey={API_KEY}'
response = requests.get(url)
data = response.json()['results']
df = pd.DataFrame(data)
df = df.rename(columns={'v': 'Volume', 'o': 'Open', 'c': 'Close', 'h': 'High', 'l': 'Low', 't': 'Date', 'n': 'num'})
df = df[['Date', 'Close']]

# Convert timestamps to date format
df['Date'] = df['Date'].apply(lambda ts: datetime.datetime.fromtimestamp(ts / 1000).strftime('%Y-%m-%d'))
df['Date'] = df['Date'].apply(str_to_datetime)
df = df.set_index('Date')

# Plot the closing prices over time
plt.plot(df.index, df['Close'])
plt.show(block=True)