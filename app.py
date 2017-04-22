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
            dlink = getUrl(panUrl, panPass)
        else:
            dlink = getUrl(panUrl)
        if dlink is not None:
            return render_template('index.html', dlink=dlink)
if __name__ == '__main__':
    app.run(host='0.0.0.0')