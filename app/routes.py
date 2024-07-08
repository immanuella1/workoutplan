from flask import render_template, current_app as app

@app.route('/')
def home():
    return render_template('index.html')
