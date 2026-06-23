from config import FMP_KEY
import requests
import pandas as pd


symbol = "AAPL"
url = f"https://financialmodelingprep.com/stable/profile?symbol={symbol}&apikey={FMP_KEY}"

response = requests.get(url).json()

sector = [i['sector'] if 'sector' in i else None for i in response]
changesPercentage = [i['changesPercentage'] if 'changesPercentage' in i else None for i in response]

data_dictionary = { 

    'Sector': sector,
    'Change Percentage': changesPercentage
}

df = pd.DataFrame(data_dictionary).sort_values('Change Percentage', ascending=False)

for i,row in df.iterrows():
    sector = row['Sector']
    change = row['Change Percentage']
    print(sector, change)