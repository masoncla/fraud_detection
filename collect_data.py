import os
import requests
import pandas as pd
import numpy as np
import pickle
import threading
from pymongo import MongoClient
import time
from flask import Flask


# initialization
app = Flask(__name__)
app.config.update(
    DEBUG = True,
)


# collecting page
@app.route('/score')
def homepage():
    threading.Timer(60.0,homepage).start()
    predict_fraud()
    return 'record collected'


def get_data():
    # grab data from API
    url = url_name
    response = requests.get(url)
    raw_data = response.json()
    # grab column names
    columns = list(raw_data.keys())
    # create a list of corresponding data
    df_data = [raw_data[col] for col in columns]
    # put into dataframe
    df = pd.DataFrame([df_data],columns=columns)
    return df, raw_data

def get_features(df):
    #'channels_cat' simplifies to 2 categories for channels: 0 for (fraud-prone) '0' channel; '1' for all others
    channels_idx = df[(df.channels==0)].index
    df['channels_cat'] = 1
    df['channels_cat'].iloc[list(channels_idx)]=0
    # simplifies payment types into 3 categories, check has almost no fraud
    payout_Aidx = df[(df.payout_type=='ACH')].index #for ACH
    payout_Cidx = df[(df.payout_type=='CHECK')].index #for CHECK
    df['payout_cat'] = 2
    df['payout_cat'].iloc[list(payout_Aidx)]=1
    df['payout_cat'].iloc[list(payout_Cidx)]=0

    #'country_cat' simplifies to 2 categories for country: 0 for less fraud prone and 1 for high risk countries
    #“Regular” countries include: AT (Austria), SG (Singapore), TH (Thailand), ZA (South Africa), SE (Sweden),
    #NZ (New Zealand), NL (Netherlands), GB (UK), FR (France), US, BE (Belgium), CA (Canada), ES (Spain), AU (Australia)
    country_idx = df[(df.country=='AT')| (df.country=='SG')| (df.country=='TH')| (df.country=='ZA')| (df.country=='SE')| (df.country=='NZ')| (df.country=='NL')| (df.country=='GB')| (df.country=='FR')| (df.country=='US')| (df.country=='BE')| (df.country=='CA')| (df.country=='ES')| (df.country=='AU')].index
    df['country_cat'] = 1
    df['country_cat'].iloc[list(country_idx)]=0

    # create feature matrix
    X= df[['num_order','user_age','num_payouts','country_cat','payout_cat','body_length','channels_cat', 'gts']].values
    return X

def send_to_db(data, probability, collection):
    data['probability'] = probability
    ts = time.time()
    #start recording time collected so we can plot frauds predicted vs. time
    #data['time_collected'] = ts
    collection.insert(data)

def predict_fraud():
    df, data = get_data()
    X = get_features(df)
    predicted_proba = model.predict_proba(X)
    send_to_db(data, predicted_proba[:,1][0], collection)

if __name__=='__main__':
    
    # get model
    model = pickle.load(open('model.pkl', 'rb'))
    
    client = MongoClient()
    db = client.new_db
    collection = db.new_test
    app.run(host='0.0.0.0',port=8000, debug=True)
    threading.Timer(5.0,predict_fraud).start()
    

    while True:
        time.sleep(10)
        predict_fraud()
    
