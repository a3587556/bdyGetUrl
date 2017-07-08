from flask import Flask, request, render_template
from getUrl import getUrl

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'GET':
        return render_template('index.html')
    else:
        panUrl = request.form['panUrl']
        panPass = request.form['panPass']
        if len(panPass) == 4:
            linkData = getUrl(panUrl, panPass)
        else:
            linkData = getUrl(panUrl)
        if linkData is not None:
            return render_template('index.html', linkData=linkData)
if __name__ == '__main__':
    app.run(host='0.0.0.0')