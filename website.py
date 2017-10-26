import flask
from flask import render_template
import sys
import datasource
import numpy as np

app = flask.Flask(__name__)

@app.route('/')
def homepage():
    return render_template('index.html')
    
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/results/<var>')
def getResults1Variable(var):
    validVars = np.load('varList.npy')
    if var not in validVars:
        return render_template('invalidvariables.html')
    else:
        return displayResults(var, "")
                                
@app.route('/results/<var1>/<var2>')
def getResults2Variables(var1, var2):
    validVars = np.load('varList.npy')
    if var1 not in validVars or var2 not in validVars:
        return render_template('invalidvariables.html')
    else:
        return displayResults(var1, var2)
        
        
                                
@app.route('/second/<var>')
def getSecond(var):
    print(var)
    return render_template('second.html', var = var)
    
def displayResults(var1, var2):
    descriptionDict = np.load('descriptionDict.npy').item()
    descr1 = descriptionDict[var1]
    descr2 = ""
    if var2 != "":
        descr2 = descriptionDict[var2]
    try:
        ds = datasource.DataSource()
        ds.runQuery([var1, var2])
        ds.createGraph()
        queryStats = ds.getStats()
        return render_template('results.html', 
                              stats=queryStats, 
                              var1 = var1, var2 = var2,
                              descr1 = descr1, descr2 = descr2)
    except ValueError:
        return render_template('novalues.html')

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage: {0} host port'.format(sys.argv[0]), file=sys.stderr)
        exit()

    host = sys.argv[1]
    port = sys.argv[2]
    app.run(host=host, port=port)
