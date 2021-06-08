from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def frontpage():
    return render_template('frontpage.html')

@app.route('/textpredictor')
def text_predictor():
    return render_template('text_predictor.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
