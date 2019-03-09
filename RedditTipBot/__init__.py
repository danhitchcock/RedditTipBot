from flask import Flask, request, render_template
import mysql.connector
import configparser
import os
app = Flask(__name__)

# access the sql library
config = configparser.ConfigParser()
config_file = os.path.join(app.root_path, 'tipper.ini')
print(config_file)
config.read(config_file)
config.sections()
sql_password = config['SQL']['sql_password']
database_name = config['SQL']['database_name']

#sql_password = 'tipbot'
#database_name = 'nano_tipper_z'
mydb = mysql.connector.connect(user='root',password=sql_password,
                              host='localhost',
                              auth_plugin='mysql_native_password', database=database_name)
mycursor = mydb.cursor()


@app.route("/")
def hello():
    return render_template('index.html')


@app.route("/getaccount")
def getaccount():
    user = request.args.get('user')
    sql = "SELECT address FROM accounts WHERE username=%s"
    val = (user, )
    mycursor.execute(sql, val)
    results = mycursor.fetchall()
    if len(results)>0:
        account = results[0][0]
    else:
        account = "Error: No account found for redditor."
    return account


if __name__ == "__main__":
    app.run()
