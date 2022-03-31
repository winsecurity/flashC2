import flask 
from flask import *


app = Flask(__name__)

@app.route("/",methods=['GET','POST'])
def index():
    
    return render_template('index.html')


@app.route("/results",methods=['GET','POST'])
def results():
    name = request.form['username_value']
    return render_template('index.html',name=name)

if __name__=='__main__':
    app.run(debug=True)


