from flask import Flask, request, render_template
import pandas as pd
import pymongo


app = Flask(__name__)
# defines the values to alert on

    




# defines the values to alert on
def alert(a):
    if a['probability'] >= 0.65:  # change to 'probability'
        return 'HIGH'
    if a['probability'] >= 0.19:
        return 'moderate'
    else:
        return 'low'
    # end function


# defines the values to flag on countries
def flag(f):
    flag_list = []
    
    # bad countries
    ok_cntry = ['AT', 'SG', 'TH', 'ZA','SE','NZ','NL','GB','FR','US','BE','CA','ES','AU']
    if f['country'] not in ok_cntry:
        flag_list.append("country")

    #emails
    bad_emails = ['yahoo.com', 'lidf.co.uk', 'live.com', 'live.fr', 'yahoo.co.uk', 'rocketmail.com', 'yahoo.fr', 'hotmail.co.uk', 'ultimatewine.co.uk', 'yahoo.ca', 'yopmail.com', 'diversity-church.com', 'yahoo.com.vn']
    if f['email_domain'] in bad_emails:
        flag_list.append("email")
    
    # missing payout
    if f['payout_type'] == "":
        flag_list.append("payout")

    # known fraud
    no_fly_list = []
    if f['name'] in no_fly_list:
        flag_list.append("known fraudster")
    
    flags = ', '.join(flag_list)
    return flags
    # end function
    

@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')


@app.route('/hello', methods=['GET'])
def hello_world():
    return ''' <h1> Hello, World!</h1> '''


@app.route('/form_example', methods=['GET'])
#@app.route('/', methods=['GET'])
def form_display():
    return ''' <form action="/string_reverse" method="POST">
                <input type="text" name="some_string" />
                <input type="submit" />
               </form>
             '''


@app.route('/string_reverse', methods=['POST'])
def reverse_string():
    text = str(request.form['some_string'])
    reversed_string = text[-1::-1]
    return ''' output: {}  '''.format(reversed_string)


#plotting
@app.route('/plot',  methods = ['GET'])
def plot():
    df = pd.read_csv('cars.csv')
    data = list(zip(df.mpg, df.weight))
    return jsonify(data)


## the table data
@app.route("/table")
def table():
  
    # get the mongo data:
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    db = client.new_db
    collection = db.new_test
    docs = [document for document in collection.find()]

    #mycol = mydb["fraudevents"].sort( { object_id: -1 } ).limit(50)
    
    # convert to pandas dataframe
    data = pd.DataFrame(docs)
  
    D = pd.DataFrame(docs)
    D.sort_values('_id', ascending=False, inplace=True)
    D = D.iloc[:50,:].copy()
        # add the tier column
    D['tier'] = D.apply(alert, axis=1)
    
    # add the flag column
    D['flag'] = D.apply(flag, axis=1)
    
    #convert to list for html 
    results = D.to_dict("list")
    
    return render_template('table.html', results = results)
    

@app.route("/detail")
def detail_table():
  # get the mongo data:
  client = pymongo.MongoClient("mongodb://localhost:27017/")
  db = client.new_db
  collection = db.new_test
  docs = [document for document in collection.find()]

  #mycol = mydb["fraudevents"].sort( { object_id: -1 } ).limit(50)
    
  # convert to pandas dataframe
  D = pd.DataFrame(docs)
  D.sort_values('_id', ascending=False, inplace=True)
  D = D.iloc[:50,:].copy()

      # add the tier column
  D['tier'] = D.apply(alert, axis=1)
  
  # add the flag column
  D['flag'] = D.apply(flag, axis=1)

  results = D.to_dict("list")
  return render_template('detail.html', results = results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)