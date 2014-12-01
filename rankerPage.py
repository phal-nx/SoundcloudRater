from flask import Flask
from flask import request
from flask import render_template
import soundcloudRanker

app = Flask(__name__)
stylePage = url_for('static', filename='style.css')

@app.route('/')
def mainPage():
    return 'Hello World!'

@app.route('/songs/<songid>')
def songs(songid=None):
    return render_template('songs.html', songid=songid)

@app.route('/actions', methods=['GET', 'POST'])
def action():
    error = None
    if request.method == 'POST':
        if valid_login(request.form['action']):
            return executeFunction(request.form['username'])
        else:
            error = 'Invalid username/password'
            # the code below is executed if the request method
            # was GET or the credentials were invalid
    return render_template('login.html', error=error)

'''
url_for('songs', songid='592')
'''

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
