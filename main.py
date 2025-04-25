from threading import Thread
import os
import sys
import json


from werkzeug.utils import secure_filename
from werkzeug.utils import secure_filename
#from core.Server import run as websocket_server

# Flask imports
from flask import Response, request, abort, Flask
from flask_cors import CORS

#from routes.ButtonsFunctionality import buttons_functionality

app = Flask(__name__)
CORS(app)

#app.register_blueprint(buttons_functionality)
@app.route('/')
def index():
    return "Flask server is running!"

if __name__ == '__main__':
    try:
        # Running the server that delivers video and the task, each request runs on diferent thread
        Thread(target=lambda: app.run(host='0.0.0.0', port=8080, debug=False, use_reloader=False, threaded=True)).start()
        # Running the websocket server that manage the manual control of the ROV
        #websocket_server()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print("Releasing video") #TODO: CHECK WHETHER THIS CODE IS TRULY EXECUTING
        #cap1.release()
        #cap2.release()
        pass