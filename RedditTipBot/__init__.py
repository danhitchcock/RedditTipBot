from flask import Flask, request, render_template
import mysql.connector
import configparser
import os
import datetime
app = Flask(__name__)

# access the sql library
config = configparser.ConfigParser()
config_file = os.path.join(app.root_path, 'tipper.ini')
print(config_file)
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

    total_5day=[]
    t0 = datetime.datetime.now()
    for item in nums:

        if (t0-item[1]).days < 5:
            total_5day.append(item[0])
    num_5day = len(total_5day)
    total_5day = [float(item)/10**30 for item in total_5day]
    total_5day = sum(total_5day)


    args = {
        'num_users': num_users,
        'active_users': active_users,
        'total_tipped': total_tipped,
        'num_5day': num_5day,
        'total_5day': total_5day
    }
    return render_template('index.html', **args)


@app.route("/recordbook")
def recordbook():
    return render_template('recordbook.html')


@app.route("/tutorials")
def tutorials():
    return render_template('index.html')


@app.route("/contact")
def contact():
    return render_template('index.html')


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
    return account


@app.route("/")
def hello():
    return render_template('index.html')

if __name__ == "__main__":
    app.run()
