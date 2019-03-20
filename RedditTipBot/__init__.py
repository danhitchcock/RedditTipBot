from flask import Flask, request, render_template
import mysql.connector
import configparser
import os
import datetime
import pandas as pd
import time
import json
import numpy as np
app = Flask(__name__)

# access the sql library
config = configparser.ConfigParser()
config_file = os.path.join(app.root_path, 'tipper.ini')

config.read(config_file)
config.sections()
sql_password = config['SQL']['sql_password']
database_name = config['SQL']['database_name']

mydb = mysql.connector.connect(user='root',password=sql_password,
                              host='localhost',
                              auth_plugin='mysql_native_password', database=database_name)
mycursor = mydb.cursor()


@app.route("/")
def index():
    t1 = time.time()
    sql = "SELECT username FROM accounts"
    mycursor.execute(sql)
    results = mycursor.fetchall()
    num_users = len(results)

    sql = "SELECT username FROM accounts WHERE active=1"
    mycursor.execute(sql)
    results = mycursor.fetchall()
    active_users = len(results)

    sql = "SELECT amount, sql_time FROM history WHERE action='send' AND hash IS NOT NULL AND recipient_username IS NOT NULL and amount IS NOT NULL"
    mycursor.execute(sql)
    nums = mycursor.fetchall()
    total_tipped = [float(item[0])/10**30 for item in nums]
    total_tipped = sum(total_tipped)

    total_5day = []
    t0 = datetime.datetime.now()
    for item in nums:
        if (t0-item[1]).days < 5:
            total_5day.append(item[0])
    num_5day = len(total_5day)
    total_5day = [float(item)/10**30 for item in total_5day]
    total_5day = sum(total_5day)

    sql = "SELECT reddit_time, username, recipient_username, amount, hash, comment_text FROM history WHERE comment_or_message='comment' AND action='send' AND hash IS NOT NULL AND recipient_username IS NOT NULL and amount IS NOT NULL ORDER BY id DESC limit 5"
    mycursor.execute(sql)
    results = mycursor.fetchall()
    keys=['datetime', 'user', 'recipient', 'amount', 'hash', 'comment']
    recents = []

    for recent in results:
        recents.append({key:item for key,item in zip(keys, recent)})
    for recent in recents:
        recent['amount']=int(recent['amount'])/10**30

    sql = "SELECT username, amount FROM history WHERE comment_or_message='comment' AND action='send' AND hash IS NOT NULL AND recipient_username IS NOT NULL and amount IS NOT NULL"
    mycursor.execute(sql)
    results = mycursor.fetchall()
    results = [[item[0], float(item[1])/10**30] for item in results]
    df = pd.DataFrame(results, columns=['username', 'amount'])
    df = df.groupby('username').agg(['sum', 'max', 'mean', 'count'])
    print(df)
    records = []
    records.append(["Biggest Tippers", zip(df['amount'].sort_values('sum', ascending=False).index[:5], round(df['amount'].sort_values('sum', ascending=False), 2)['sum'])])
    records.append(["Largest Tip", zip(df['amount'].sort_values('max', ascending=False).index[:5], round(df['amount'].sort_values('max', ascending=False), 2)['max'])])
    records.append(["Highest Average", zip(df['amount'].sort_values('mean', ascending=False).index[:5], round(df['amount'].sort_values('mean', ascending=False), 2)['mean'])])
    records.append(["Most Tips", zip(df['amount'].sort_values('count', ascending=False).index[:5], df['amount'].sort_values('count', ascending=False)['count'])])
    print(records)


    args = {
        'num_users': num_users,
        'active_users': active_users,
        'total_tipped': total_tipped,
        'num_5day': num_5day,
        'total_5day': total_5day,
        'recents': recents,
        'records': records,
        'time': time.time()-t1
    }
    mydb.commit()
    print(time.time()-t1)
    return render_template('index.html', **args)


@app.route("/recordbook")
def recordbook():
    return render_template('recordbook.html')


@app.route("/tutorials")
def tutorials():
    return render_template('tutorials.html')


@app.route("/contact")
def contact():
    return render_template('contact.html')


@app.route("/getaccount")
def getaccount():
    user = request.args.get('user')
    sql = "SELECT address FROM accounts WHERE username=%s"
    val = (user, )
    mycursor.execute(sql, val)
    results = mycursor.fetchall()
    if len(results) > 0:
        account = results[0][0]
    else:
        account = "Error: No account found for redditor."
    data = {'account': account}
    return json.dumps(data)


@app.route("/")
def hello():
    return render_template('index.html')

if __name__ == "__main__":
    app.run()
