from flask import Flask

app = Flask(__name__)

@app.route("/hello")
def home():
    return "hey skida"

app.run()
