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
def df_to_windowed_df(dataframe, first_date_str, last_date_str, n=3):
    # Function to convert string to datetime object
    first_date = str_to_datetime(first_date_str)
    last_date = str_to_datetime(last_date_str)
    
    target_date = first_date
    
    dates = []
    X, Y = [], []
    
    last_time = False
    while True:
        df_subset = dataframe.loc[:target_date].tail(n + 1)
        
        if len(df_subset) != n + 1:
            print(f'Error: Window of size {n} is too large for date {target_date}')
            return
        
        values = df_subset['Close'].to_numpy()
        x, y = values[:-1], values[-1]
        
        dates.append(target_date)
        X.append(x)
        Y.append(y)
        
        # Get the date of the next week
        next_week = dataframe.loc[target_date:target_date + datetime.timedelta(days=7)]
        next_datetime_str = str(next_week.head(2).tail(1).index.values[0])
        next_date_str = next_datetime_str.split('T')[0]
        year_month_day = next_date_str.split('-')
        year, month, day = year_month_day
        next_date = datetime.datetime(day=int(day), month=int(month), year=int(year))
        
        if last_time:
            break
        
        target_date = next_date
        
        if target_date == last_date:
            last_time = True
    
    # Create a dataframe for the windowed dataset
    ret_df = pd.DataFrame({})
    ret_df['Target Date'] = dates
    
    X = np.array(X)
    for i in range(0, n):
        ret_df[f'Target-{n-i}'] = X[:, i]
    
    ret_df['Target'] = Y
    
    return ret_df

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