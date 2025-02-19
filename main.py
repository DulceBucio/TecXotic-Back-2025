from threading import Thread
import os
import sys
import json


from werkzeug.utils import secure_filename
from werkzeug.utils import secure_filename
from core.Server import run as websocket_server



if __name__ == '__main__':
    try:
        # Running the server that delivers video and the task, each request runs on diferent thread
        # Running the websocket server that manage the manual control of the ROV
        websocket_server()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print("Releasing video") #TODO: CHECK WHETHER THIS CODE IS TRULY EXECUTING
        #cap1.release()
        #cap2.release()
        pass