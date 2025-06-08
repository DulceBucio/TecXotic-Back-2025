from flask import Flask, request
from flask_cors import CORS
from routes.float import floatData
from routes.eDNA import DNA

app = Flask(__name__)
CORS(app)


# app.register_blueprint(floatData)
app.register_blueprint(DNA)

@app.route('/')
def index():
    return "ping"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)