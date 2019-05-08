import os
import requests
import pandas as pd
import numpy as np
import pickle
import threading
from pymongo import MongoClient
import time
from flask import Flask
import nlp_class


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
    '''
    Takes in the dataframe and creates new features.
    Returns a feature matrix.
    '''
    
    #'country_cat' simplifies to 2 categories for country: 0 for "safer" and 1 for more fraud prone
    fraud_prone_countries =['VN','MY','PK','MA','CH','PH','A1','CI','PS','TR','CZ',
                            'KH','NA','GH','SI','CM','RU','DZ','IL','CN','DK','CO','JE']
    df['country_cat'] = 0
    df['country_cat'][df.country.isin(fraud_prone_countries)] = 1
    
    
    # 'upper' creates a binary classifier for whether or not the title is in all uppercase letters or not
    df['upper'] = df.name.apply(lambda x: x.isupper())
    df.upper = df.upper.astype(int)
    
    # 'time_until_end' creates a value for the difference in time between event creation and the scheduled end of the event
    df['time_until_end']=df.event_end-df.event_created
    
    X = df[['user_age', 'country_cat', 'upper', 'time_until_end', 'num_order', 'body_length']].values
    
    return X

def send_to_db(data, probability, collection):
    data['probability'] = probability
    ts = time.time()
    #start recording time collected so we can plot frauds predicted vs. time
    #data['time_collected'] = ts
    collection.insert(data)

def predict_fraud():
    # get data and generate features
    df, data = get_data()
    X = get_features(df)
    lsaX = nlp_class.NLP_Feature_Engineer_().fit_transform(df)
    X = pd.concat((X, lsaX), axis=1)
    # predict probability that an event is fraud and send to MongoDB
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
    
