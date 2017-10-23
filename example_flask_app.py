#!/usr/bin/env python3
'''
    example_flask_app.py
    Jeff Ondich, 22 April 2016
    Modified by Eric Alexander, January 2017

    A slightly more complicated Flask sample app than the
    "hello world" app found at http://flask.pocoo.org/.
'''
import flask
from flask import render_template
import json
import sys
import datasource

app = flask.Flask(__name__)

@app.route('/')
def hello():
    return render_template('index.html')

@app.route('/boring/')
def boring():
    return render_template('index.html')

@app.route('/results')
def results():
    return render_template('results.html')

@app.route('/fruit')
def fruit():
    myFruit = [
        {'name': 'apple', 'rating': 7},
        {'name': 'banana', 'rating': 5},
        {'name': 'pear', 'rating': 4}
    ]

    return render_template('fruit.html',
                           fruits=myFruit)

@app.route('/fruitImg/')
def fruitImg():
    return render_template('fruitImg.html')
    
@app.route('/<vars>/results')
def get_results(vars):
    ds = datasource.DataSource()
    splitVars = vars.split('-')
    ds.runQuery(splitVars)
    ds.createGraph()
    queryStats = ds.getStats()
    return render_template('results.html', stats=queryStats)
    

@app.route('/authors/<author>')
def get_author(author):
    ''' What a dopey function! But it illustrates a Flask route with a parameter. '''
    if author == 'Twain':
        author_dictionary = {'last_name':'Twain', 'first_name':'Mark'}
    elif author == 'Shakespeare':
        author_dictionary = {'last_name':'Shakespeare', 'first_name':'William'}
    else:
        author_dictionary = {'last_name':'McBozo', 'first_name':'Bozo'}
    return json.dumps(author_dictionary)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage: {0} host port'.format(sys.argv[0]), file=sys.stderr)
        exit()

    host = sys.argv[1]
    port = sys.argv[2]
    app.run(host=host, port=port)
