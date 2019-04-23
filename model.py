import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
import pickle
from sys import argv


def get_features(df):
    '''
    Takes in the dataframe and creates binary classification labels and new features.
    Returns a feature matrix and a target array.
    '''
    
    fraud_idx = df[(df.acct_type=='fraudster_event')| (df.acct_type=='fraudster')|(df.acct_type=='fraudster_att')].index
    # create label column
    df['label'] = 0
    df['label'].iloc[list(fraud_idx)]=1 # changes fraud labels to 1
    
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
    y = df.label.values
    
    return X,y








if __name__ == '__main__':
    input_filepath = argv[1]
    
    df = pd.read_json(input_filepath)
    
    X,y = get_features(df)
    
    model = RandomForestClassifier(criterion='entropy', max_depth=50, n_estimators=100)
    model.fit(X,y)
    
    with open('model.pkl', 'wb') as f:
        # Write the fit model to a file.
        pickle.dump(model, f)

    
    