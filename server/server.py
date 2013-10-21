from flask import Flask
from flask import render_template
from pysqlite2 import dbapi2 as db
app = Flask(__name__)

@app.route('/')
@app.route('/<name>')
def home(name=None):
    values = [ 0,1,2,3,4,5 ]
    return render_template('hello.html',name=name, values=values)

@app.route('/list_data')
def list_data():
    cur = db.connect('../data.sqlite').cursor()
    data = cur.execute('SELECT * FROM tweets').fetchall()
    return render_template('list.html', data=data)

if __name__ == '__main__':
    app.run()
